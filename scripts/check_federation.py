"""End-to-end cross-agency checks against fully running Docker stack.

Uses only synthetic accounts, records, local presentation endpoints.
"""
import json
import os
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8090"
EXPECTED = {
    "transport": "DL-NP-SYNTHETIC-001",
    "civil": "CIV-NP-SYNTHETIC-001",
    "company": "CO-NP-SYNTHETIC-001",
}


def request(path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["x-native-demo-token"] = token
    req = urllib.request.Request(
        BASE + path,
        headers=headers,
        data=json.dumps(body).encode() if body is not None else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as ex:
        return ex.code, json.loads(ex.read().decode())


def retry(path, condition, count=30):
    last = None
    for _ in range(count):
        try:
            last = request(path)
            if condition(last):
                return last
        except Exception as ex:
            last = str(ex)
        time.sleep(2)
    raise AssertionError(f"Timed out waiting for {path}: {last}")


status, topology = retry("/v1/topology", lambda p: p[0] == 200)
assert len(topology["networks"]) >= 5, topology
assert topology["governmentConnections"] is False, topology

for agency, reference in EXPECTED.items():
    status, response = retry(
        "/v1/demo/request/" + agency, lambda p: p[0] == 200 and p[1].get("allowed"),
        count=35
    )
    assert response["record"]["reference"] == reference, response
    assert response["record"]["isSynthetic"] is True, response
    assert response["record"]["agencyOwnsRecord"] is True, response
    assert len(response["correlationId"]) == 36, response
    print(f"PASS: Keycloak service token -> {agency} edge JWT authorization -> private agency DB")

status, response = request("/v1/demo/deny/transport")
assert status == 200 and not response["allowed"] and response["edgeStatus"] == 401, response
print("PASS: no bearer token denied by agency gateway")

status, limited = request("/v1/demo/limited/company")
assert status == 200 and limited["allowed"] is False and limited["edgeStatus"] == 403, limited
status, permitted = request("/v1/demo/limited/transport")
assert status == 200 and permitted["allowed"] is True, permitted
print("PASS: valid, correctly signed transport-only token rejected by company agency")

status, response = request("/v1/native/dotm")
assert status == 403, response
print("PASS: native Altinn synthetic bridge requires its separate local token")

env = {}
with open(".demo.local.env", encoding="utf-8") as file:
    for line in file:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            env[key] = value
token = env["NATIVE_WEBHOOK_TOKEN"]
status, response = request("/v1/native/dotm", token=token)
assert status == 200 and response["reference"] == EXPECTED["transport"], response
assert response["source"].startswith("OAuth-verified"), response
print("PASS: native bridge reaches real OAuth federation to transport agency")

event = {
    "source": "ttd/nepal-licence",
    "event_type": "native.altinn.task.completed",
    "event_id": "native.ci.federation.Task_1",
    "instance_id": "CI-FEDERATION/1234567890",
}
status, first = request("/v1/native/events", event, token=token)
assert status == 202 and first["queued"], first
status, second = request("/v1/native/events", event, token=token)
assert status == 202 and second["duplicate"], second
for _ in range(25):
    status, activity = request("/v1/audit")
    outbox = {x["event_id"]: x for x in activity["outbox"]}
    if outbox.get(event["event_id"], {}).get("state") == "delivered":
        break
    time.sleep(1)
else:
    raise AssertionError("Synthetic Altinn event remained queued; outbox=" + str(outbox))
assert len([x for x in activity["exchanges"] if x["outcome"] == "PERMITTED"]) >= 3
assert any(x["outcome"] == "DENIED" for x in activity["exchanges"])
print("PASS: token-protected native event -> broker durable outbox -> fake Nagarik notification")
print("PASS: audit logs include permitted and denied resource decisions")
