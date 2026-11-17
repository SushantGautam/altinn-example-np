"""Real Keycloak OIDC sign-in + service journey on a running Docker Compose stack.

No third-party Python packages are needed; use:
    docker compose up --build -d
    python scripts/smoke_oidc.py
"""
import json
import sys
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener

BASE = "http://localhost:8000"


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.action = None
        self.inside = False
        self.inputs = {}

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == "form" and fields.get("id") == "kc-form-login":
            self.inside = True
            self.action = fields.get("action")
        if self.inside and tag == "input" and fields.get("name"):
            self.inputs[fields["name"]] = fields.get("value", "")

    def handle_endtag(self, tag):
        if tag == "form" and self.inside:
            self.inside = False


def person(username):
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    login = opener.open(BASE + "/auth/login", timeout=30)
    page = login.read().decode("utf-8")
    form = FormParser()
    form.feed(page)
    assert form.action and "login-actions" in form.action, "Keycloak login form not located"
    form.inputs.update({"username": username, "password": "Demo123!"})
    response = opener.open(Request(form.action, data=urlencode(form.inputs).encode(),
                                   headers={"Content-Type": "application/x-www-form-urlencoded"}), timeout=30)
    response.read()
    me = get(opener, "/api/me")
    assert me["user"]["username"] == username, "OIDC identity was not established"
    assert me["identity"]["provider"].startswith("NepalID")
    return opener, me["csrf_token"]


def get(opener, path):
    with opener.open(BASE + path, timeout=30) as response:
        return json.load(response)


def mutate(opener, path, method, body, csrf):
    with opener.open(Request(BASE + path, data=json.dumps(body).encode(), method=method,
                             headers={"Content-Type":"application/json", "X-CSRF-Token":csrf}), timeout=30) as response:
        return json.load(response)


def main():
    citizen, citizen_csrf = person("asha")
    assert get(citizen, "/api/registries/me")["person"]["nid"] == "NP-DEMO-001"
    created = mutate(citizen, "/api/cases", "POST", {"service":"licence-correction",
                     "new_address":"Ward 9, Kathmandu", "reason":"Demonstrate end to end identity"}, citizen_csrf)
    reference = created["case_id"]
    officer, officer_csrf = person("maya")
    decision = mutate(officer, "/api/cases/" + reference + "/decision", "PATCH",
                      {"status":"approved", "note":"Approved for the demonstration"}, officer_csrf)
    assert decision["case"]["status"] == "approved"
    proof = decision["case"]["verification_url"]
    assert get(citizen, proof)["valid"] is True
    assert any(item["case_id"] == reference for item in get(citizen, "/api/inbox")["notifications"])
    director, director_csrf = person("raj")
    mutate(director, "/api/delegations", "POST",
           {"grantee":"priya", "scope":"transport-permit"}, director_csrf)
    accountant, accountant_csrf = person("priya")
    permit = {"service":"transport-permit", "permit":"TP-SMOKE-26", "reason":"Annual renewal"}
    assert mutate(accountant, "/api/cases", "POST", permit, accountant_csrf)["status"] == "submitted"
    grants = get(director, "/api/delegations")["delegations"]
    active = next(x for x in grants if x["active"] == 1)
    mutate(director, "/api/delegations/" + str(active["id"]), "DELETE", {}, director_csrf)
    try:
        mutate(accountant, "/api/cases", "POST", permit, accountant_csrf)
        raise AssertionError("Revoked accountant access was incorrectly accepted")
    except HTTPError as exc:
        assert exc.code == 403, "Expected 403 after revocation"
    print("PASS: real OIDC logins, registry prefill, citizen submission, officer decision,")
    print("      verifiable demo proof, inbox event, business delegation, and revocation denial")
    print("      Reference: " + reference)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("OIDC end-to-end smoke test failed: " + repr(exc), file=sys.stderr)
        raise
