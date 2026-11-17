"""Nepal Digital Government demo, inspired by Altinn concepts.

Only the OIDC flow is a genuine standards-based integration. Workflow,
delegation, registries, notifications and authorization are local demos,
NOT official Altinn implementations or Nepali government connections.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

import httpx
import jwt
from jwt import PyJWKClient
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from connectors import INTEGRATIONS, get_company, get_licence, get_person

BASE = Path(__file__).resolve().parent
DB_PATH = os.getenv("DB_PATH", "/tmp/nepal-demo.db")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")
OIDC_ISSUER = os.getenv("OIDC_ISSUER", "http://localhost:8081/realms/nepal-demo")
OIDC_INTERNAL = os.getenv("OIDC_INTERNAL", "http://localhost:8081/realms/nepal-demo")
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID", "nepal-demo")
OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET", "local-demo-only-change-me")
SESSION_SECRET = os.getenv("SESSION_SECRET", "local-dev-only-change-me")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
NATIVE_WEBHOOK_TOKEN = os.getenv("NATIVE_WEBHOOK_TOKEN", "")

# Roles are fixture data, NOT Norwegian or Nepali government role assertions.
PEOPLE = {
    "asha": {"username": "asha", "name": "Asha Shrestha", "role": "citizen", "role_label": "Citizen", "nid": "NP-DEMO-001"},
    "raj": {"username": "raj", "name": "Raj Thapa", "role": "director", "role_label": "Company Director", "organisation_id": "COMP-100"},
    "priya": {"username": "priya", "name": "Priya Kandel", "role": "accountant", "role_label": "Accountant / Representative"},
    "maya": {"username": "maya", "name": "Maya Adhikari", "role": "officer", "role_label": "DoTM Reviewing Officer"},
    "kiran": {"username": "kiran", "name": "Kiran Sharma", "role": "observer", "role_label": "Government Demonstration Observer"},
}
SERVICES = {
    "licence-correction": {"name": "Driving licence address correction", "agency": "Department of Transport Management", "audience": "Citizen"},
    "transport-permit": {"name": "Transport operator permit renewal", "agency": "Department of Transport Management", "audience": "Business"},
}

app = FastAPI(title="Nepal Digital Government — Altinn Concepts Demo", version="0.1.0", docs_url="/api/docs")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def conn():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def event(db, actor, action, detail, case_id=None):
    db.execute("INSERT INTO events(case_id,actor,action,detail,created_at) VALUES(?,?,?,?,?)",
               (case_id, actor, action, detail, now()))


def message(db, recipient, title, body, case_id):
    db.execute("INSERT INTO notifications(recipient,title,body,case_id,created_at) VALUES(?,?,?,?,?)",
               (recipient, title, body, case_id, now()))


def reset_data(db):
    for table in ("native_deliveries", "notifications", "events", "delegations", "cases"):
        db.execute("DELETE FROM " + table)
    cases = [
        ("NP-SEED-01", "licence-correction", "asha", None, "approved",
         {"current_address": "Ward 3, Lalitpur", "new_address": "Ward 4, Lalitpur", "reason": "Household move", "licence": "DL-09418"}, "maya"),
        ("NP-SEED-02", "transport-permit", "raj", "COMP-100", "submitted",
         {"company_name": "Everest Logistics Pvt. Ltd.", "permit": "TP-DEMO-221", "reason": "Annual renewal"}, None),
    ]
    for case_id, service, applicant, organisation, status, payload, reviewer in cases:
        db.execute("""INSERT INTO cases(id,service,applicant,organisation_id,status,payload,reviewed_by,created_at,updated_at)
                      VALUES(?,?,?,?,?,?,?,?,?)""",
                   (case_id, service, applicant, organisation, status, json.dumps(payload), reviewer, now(), now()))
        event(db, "system", "DEMO_SEEDED", "Synthetic example application created", case_id)
    message(db, "asha", "Licence correction completed", "Your sample licence correction was approved.", "NP-SEED-01")
    db.commit()


def init_db():
    with conn() as db:
        db.executescript("""
          CREATE TABLE IF NOT EXISTS native_deliveries (event_id TEXT PRIMARY KEY, source TEXT NOT NULL, instance_id TEXT NOT NULL, created_at TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS cases (
             id TEXT PRIMARY KEY, service TEXT NOT NULL, applicant TEXT NOT NULL,
             organisation_id TEXT, status TEXT NOT NULL, payload TEXT NOT NULL,
             reviewed_by TEXT, decision_note TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
          );
          CREATE TABLE IF NOT EXISTS delegations (
             id INTEGER PRIMARY KEY AUTOINCREMENT, organisation_id TEXT NOT NULL,
             grantor TEXT NOT NULL, grantee TEXT NOT NULL, scope TEXT NOT NULL,
             active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL
          );
          CREATE TABLE IF NOT EXISTS events (
             id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT, actor TEXT NOT NULL,
             action TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL
          );
          CREATE TABLE IF NOT EXISTS notifications (
             id INTEGER PRIMARY KEY AUTOINCREMENT, recipient TEXT NOT NULL,
             title TEXT NOT NULL, body TEXT NOT NULL, case_id TEXT,
             created_at TEXT NOT NULL
          );
        """)
        if db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0:
            reset_data(db)


@app.on_event("startup")
def startup():
    init_db()


def session_token(username):
    return jwt.encode({"sub": username, "iss": "nepal-demo", "iat": int(datetime.now(timezone.utc).timestamp()),
                       "exp": int((datetime.now(timezone.utc) + timedelta(hours=4)).timestamp())},
                      SESSION_SECRET, algorithm="HS256")


def csrf_value(raw_session):
    return hmac.new(SESSION_SECRET.encode(), raw_session.encode(), hashlib.sha256).hexdigest()


def current_user(request: Request):
    token = request.cookies.get("np_session")
    if not token:
        raise HTTPException(401, "Please sign in through the demonstration identity provider")
    try:
        claims = jwt.decode(token, SESSION_SECRET, algorithms=["HS256"], issuer="nepal-demo")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Session expired or invalid")
    person = PEOPLE.get(claims["sub"])
    if not person:
        raise HTTPException(403, "Identity not enabled for the demonstration")
    return person


def require_csrf(request: Request, user=Depends(current_user)):
    raw = request.cookies.get("np_session", "")
    supplied = request.headers.get("x-csrf-token", "")
    if not supplied or not hmac.compare_digest(supplied, csrf_value(raw)):
        raise HTTPException(403, "Missing or invalid CSRF token")
    return user


def require_roles(user, *roles):
    if user["role"] not in roles:
        raise HTTPException(403, "This role is not permitted to perform the operation")


def has_delegation(db, grantee, org="COMP-100", scope="transport-permit"):
    return db.execute("""SELECT 1 FROM delegations
                         WHERE organisation_id=? AND grantee=? AND scope=? AND active=1 LIMIT 1""",
                      (org, grantee, scope)).fetchone() is not None


def case_view(row):
    result = dict(row)
    result["payload"] = json.loads(result["payload"])
    result["service_name"] = SERVICES[result["service"]]["name"]
    result["agency"] = SERVICES[result["service"]]["agency"]
    if result["status"] == "approved":
        proof = hmac.new(SESSION_SECRET.encode(), (result["id"] + "|" + result["updated_at"]).encode(), hashlib.sha256).hexdigest()[:24]
        result["verification_url"] = "/api/verify/" + result["id"] + "?proof=" + proof
    return result


@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")


@app.get("/health")
def health():
    return {"ok": True, "mode": "demonstration", "altinn_connected": False}


@app.get("/auth/login")
def login():
    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    tmp = jwt.encode({"state": state, "nonce": nonce, "verifier": verifier,
                      "exp": int((datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp())},
                     SESSION_SECRET, algorithm="HS256")
    params = {
        "client_id": OIDC_CLIENT_ID, "redirect_uri": PUBLIC_BASE_URL + "/auth/callback",
        "response_type": "code", "scope": "openid profile email",
        "state": state, "nonce": nonce, "code_challenge": challenge, "code_challenge_method": "S256",
        "prompt": "login",
    }
    response = RedirectResponse(OIDC_ISSUER + "/protocol/openid-connect/auth?" + urlencode(params))
    response.set_cookie("np_oidc", tmp, httponly=True, samesite="lax", max_age=600, secure=False)
    return response


@app.get("/auth/callback")
async def callback(request: Request, state: str = "", code: str = "", error: str = ""):
    if error:
        raise HTTPException(400, "Identity provider returned: " + error)
    tmp = request.cookies.get("np_oidc")
    if not tmp:
        raise HTTPException(400, "Missing authentication state")
    try:
        stored = jwt.decode(tmp, SESSION_SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(400, "Invalid authentication state")
    if not state or not hmac.compare_digest(state, stored["state"]) or not code:
        raise HTTPException(400, "Authentication state mismatch")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            token_response = await client.post(
                OIDC_INTERNAL + "/protocol/openid-connect/token",
                data={"grant_type": "authorization_code", "client_id": OIDC_CLIENT_ID,
                      "client_secret": OIDC_CLIENT_SECRET, "code": code,
                      "redirect_uri": PUBLIC_BASE_URL + "/auth/callback",
                      "code_verifier": stored["verifier"]})
        token_response.raise_for_status()
        id_token = token_response.json()["id_token"]
        key = PyJWKClient(OIDC_INTERNAL + "/protocol/openid-connect/certs").get_signing_key_from_jwt(id_token)
        claims = jwt.decode(id_token, key.key, algorithms=["RS256"], audience=OIDC_CLIENT_ID, issuer=OIDC_ISSUER)
    except (httpx.HTTPError, KeyError, jwt.PyJWTError) as exc:
        raise HTTPException(502, "Identity provider verification failed: " + type(exc).__name__)
    if not hmac.compare_digest(str(claims.get("nonce", "")), stored["nonce"]):
        raise HTTPException(400, "Identity nonce mismatch")
    username = claims.get("preferred_username", "")
    if username not in PEOPLE:
        raise HTTPException(403, "This identity is not a demonstration user")
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("np_oidc")
    response.set_cookie("np_session", session_token(username), httponly=True, samesite="lax",
                        max_age=14400, secure=False)
    return response


@app.get("/auth/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("np_session")
    response.delete_cookie("np_oidc")
    return response


@app.get("/api/me")
def me(request: Request, user=Depends(current_user)):
    return {"user": user, "csrf_token": csrf_value(request.cookies["np_session"]),
            "identity": {"provider": "NepalID (local Keycloak OIDC)", "assurance": "DEMO ONLY — no real NID/BankID verification"}}


@app.get("/api/demo-users")
def demo_users():
    if not DEMO_MODE:
        raise HTTPException(404)
    return [{"username": x["username"], "name": x["name"], "role": x["role_label"]} for x in PEOPLE.values()]


@app.get("/api/integrations")
def integrations(user=Depends(current_user)):
    return {"integrations": [vars(x) for x in INTEGRATIONS],
            "notice": "All Nepal agency APIs and the Altinn connector are simulated/not connected."}


@app.get("/api/registries/me")
def registries(user=Depends(current_user)):
    require_roles(user, "citizen")
    person = get_person(user["nid"])
    licence = get_licence("DL-09418")
    return {"person": person, "licence": licence, "origin": "SIMULATED API RESPONSES"}


@app.get("/api/registries/company")
def company(user=Depends(current_user)):
    require_roles(user, "director", "accountant", "officer")
    with conn() as db:
        if user["role"] == "accountant" and not has_delegation(db, user["username"]):
            raise HTTPException(403, "No active business representation")
    return {"company": get_company("COMP-100"), "origin": "SIMULATED API RESPONSE"}


@app.get("/api/delegations")
def delegations(user=Depends(current_user)):
    require_roles(user, "director", "accountant")
    with conn() as db:
        if user["role"] == "director":
            rows = db.execute("SELECT * FROM delegations ORDER BY id DESC").fetchall()
        else:
            rows = db.execute("SELECT * FROM delegations WHERE grantee=? ORDER BY id DESC",
                              (user["username"],)).fetchall()
    return {"delegations": [dict(x) for x in rows]}


@app.post("/api/delegations")
def grant(payload: dict, user=Depends(require_csrf)):
    require_roles(user, "director")
    if payload.get("grantee") != "priya" or payload.get("scope") != "transport-permit":
        raise HTTPException(422, "Only synthetic Priya / transport-permit delegation is available in demo")
    with conn() as db:
        if has_delegation(db, "priya"):
            raise HTTPException(409, "An active delegation already exists")
        db.execute("""INSERT INTO delegations(organisation_id,grantor,grantee,scope,active,created_at)
                      VALUES('COMP-100',?,?,?,1,?)""",
                   (user["username"], "priya", "transport-permit", now()))
        event(db, user["username"], "DELEGATION_GRANTED", "Priya may submit transport-permit for COMP-100")
        message(db, "priya", "Representation granted", "You can now apply for a transport permit on behalf of Everest Logistics.", None)
        db.commit()
    return {"ok": True, "message": "Limited permission granted; password was never shared"}


@app.delete("/api/delegations/{delegation_id}")
def revoke(delegation_id: int, user=Depends(require_csrf)):
    require_roles(user, "director")
    with conn() as db:
        row = db.execute("SELECT * FROM delegations WHERE id=? AND grantor=? AND active=1",
                         (delegation_id, user["username"])).fetchone()
        if not row:
            raise HTTPException(404, "Active delegation not found")
        db.execute("UPDATE delegations SET active=0 WHERE id=?", (delegation_id,))
        event(db, user["username"], "DELEGATION_REVOKED", "Representation revoked for Priya / COMP-100")
        message(db, "priya", "Representation revoked", "You can no longer submit applications for Everest Logistics.", None)
        db.commit()
    return {"ok": True}


@app.get("/api/cases")
def cases(user=Depends(current_user)):
    with conn() as db:
        if user["role"] == "officer":
            rows = db.execute("SELECT * FROM cases ORDER BY created_at DESC").fetchall()
        elif user["role"] == "citizen":
            rows = db.execute("SELECT * FROM cases WHERE applicant=? ORDER BY created_at DESC", (user["username"],)).fetchall()
        elif user["role"] == "director":
            rows = db.execute("SELECT * FROM cases WHERE organisation_id=? ORDER BY created_at DESC",
                              (user["organisation_id"],)).fetchall()
        elif user["role"] == "accountant" and has_delegation(db, user["username"]):
            rows = db.execute("SELECT * FROM cases WHERE organisation_id='COMP-100' ORDER BY created_at DESC").fetchall()
        else:
            rows = []
    return {"cases": [case_view(x) for x in rows]}


@app.post("/api/cases")
def submit(payload: dict, user=Depends(require_csrf)):
    service = payload.get("service")
    if service not in SERVICES:
        raise HTTPException(422, "Unknown government service")
    organisation = None
    fields = {}
    if service == "licence-correction":
        require_roles(user, "citizen")
        new_address = str(payload.get("new_address", "")).strip()
        reason = str(payload.get("reason", "")).strip()
        if not 6 <= len(new_address) <= 160 or not 4 <= len(reason) <= 300:
            raise HTTPException(422, "Enter an address (6–160 characters) and reason (4–300 characters)")
        person = get_person(user["nid"])
        licence = get_licence("DL-09418")
        fields = {"name": person["name"], "nid": person["nid"], "licence": licence["number"],
                  "current_address": licence["address"], "new_address": new_address, "reason": reason}
    else:
        require_roles(user, "director", "accountant")
        organisation = "COMP-100"
        permit = str(payload.get("permit", "")).strip()
        reason = str(payload.get("reason", "")).strip()
        if not 5 <= len(permit) <= 30 or not 4 <= len(reason) <= 300:
            raise HTTPException(422, "Enter a permit reference and renewal reason")
        fields = {"company_name": get_company(organisation)["name"], "permit": permit, "reason": reason}
    case_id = "NP-" + uuid.uuid4().hex[:8].upper()
    with conn() as db:
        if service == "transport-permit" and user["role"] == "accountant" and not has_delegation(db, user["username"]):
            event(db, user["username"], "ACCESS_DENIED", "Attempted submission without an active delegation")
            db.commit()
            raise HTTPException(403, "A director must first grant a transport-permit delegation")
        stamp = now()
        db.execute("""INSERT INTO cases(id,service,applicant,organisation_id,status,payload,created_at,updated_at)
                      VALUES(?,?,?,?,?,?,?,?)""",
                   (case_id, service, user["username"], organisation, "submitted", json.dumps(fields), stamp, stamp))
        event(db, user["username"], "REGISTRY_LOOKUP", "Read synthetic registry records", case_id)
        event(db, user["username"], "APPLICATION_SUBMITTED", SERVICES[service]["name"], case_id)
        message(db, user["username"], "Application received",
                "Your request " + case_id + " has been sent for officer review.", case_id)
        if organisation and user["username"] != "raj":
            message(db, "raj", "Company application submitted",
                    "An authorized representative submitted " + case_id + ".", case_id)
        db.commit()
    return {"ok": True, "case_id": case_id, "status": "submitted"}


@app.patch("/api/cases/{case_id}/decision")
def decide(case_id: str, payload: dict, user=Depends(require_csrf)):
    require_roles(user, "officer")
    status = payload.get("status")
    note = str(payload.get("note", "")).strip()
    if status not in ("approved", "rejected", "needs-info") or len(note) < 3 or len(note) > 300:
        raise HTTPException(422, "Choose decision and enter a short note")
    with conn() as db:
        row = db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Application not found")
        if row["status"] in ("approved", "rejected"):
            raise HTTPException(409, "Finalized applications cannot be decided again")
        db.execute("""UPDATE cases SET status=?,reviewed_by=?,decision_note=?,updated_at=? WHERE id=?""",
                   (status, user["username"], note, now(), case_id))
        event(db, user["username"], "OFFICER_" + status.upper().replace("-", "_"), note, case_id)
        message(db, row["applicant"], "Application " + status.replace("-", " "),
                "Decision for " + case_id + ": " + note, case_id)
        if row["organisation_id"] and row["applicant"] != "raj":
            message(db, "raj", "Company application " + status.replace("-", " "),
                    "Decision recorded for " + case_id + ".", case_id)
        db.commit()
        updated = db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
    return {"case": case_view(updated)}


@app.get("/api/inbox")
def inbox(user=Depends(current_user)):
    with conn() as db:
        rows = db.execute("SELECT * FROM notifications WHERE recipient=? ORDER BY id DESC",
                          (user["username"],)).fetchall()
    return {"notifications": [dict(x) for x in rows], "system": "Nagarik App inbox — simulated integration"}


@app.get("/api/audit")
def audit(user=Depends(current_user)):
    require_roles(user, "officer", "observer")
    with conn() as db:
        rows = db.execute("SELECT * FROM events ORDER BY id DESC LIMIT 80").fetchall()
    return {"events": [dict(x) for x in rows], "notice": "Synthetic event log, not Altinn Audit Log"}


@app.get("/api/metrics")
def metrics(user=Depends(current_user)):
    with conn() as db:
        cases_total = db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        submitted = db.execute("SELECT COUNT(*) FROM cases WHERE status='submitted'").fetchone()[0]
        approved = db.execute("SELECT COUNT(*) FROM cases WHERE status='approved'").fetchone()[0]
        delegations_active = db.execute("SELECT COUNT(*) FROM delegations WHERE active=1").fetchone()[0]
        event_count = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    return {"cases": cases_total, "awaiting_review": submitted, "approved": approved,
            "active_delegations": delegations_active, "audit_events": event_count,
            "services": len(SERVICES), "agency_integrations": 0}


@app.post("/api/demo/reset")
def reset(user=Depends(require_csrf)):
    if not DEMO_MODE:
        raise HTTPException(404)
    require_roles(user, "observer")
    with conn() as db:
        reset_data(db)
        event(db, user["username"], "DEMO_RESET", "Reset all simulated records")
        db.commit()
    return {"ok": True}


@app.post("/api/integrations/native-altinn/events")
def receive_native_altinn_event(payload: dict, request: Request):
    """Local-only synthetic bridge from a REAL Altinn process hook.

    This does not authenticate a Nepal government or Altinn platform service.
    A runtime-generated shared token connects two laptop demo processes.
    """
    if not DEMO_MODE:
        raise HTTPException(404)
    supplied = request.headers.get("x-native-demo-token", "")
    if not NATIVE_WEBHOOK_TOKEN or not supplied or not hmac.compare_digest(supplied, NATIVE_WEBHOOK_TOKEN):
        raise HTTPException(403, "Invalid local demonstration integration token")
    event_id = str(payload.get("event_id", ""))
    instance_id = str(payload.get("instance_id", ""))
    if (payload.get("source") != "ttd/nepal-licence"
        or payload.get("event_type") != "native.altinn.task.completed"
        or not 8 <= len(event_id) <= 128
        or not 8 <= len(instance_id) <= 128
        or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._/" for c in event_id + instance_id)):
        raise HTTPException(422, "Invalid native Altinn synthetic event")
    with conn() as db:
        exists = db.execute("SELECT 1 FROM native_deliveries WHERE event_id=?", (event_id,)).fetchone()
        if exists:
            return {"accepted": True, "duplicate": True}
        db.execute("INSERT INTO native_deliveries(event_id,source,instance_id,created_at) VALUES(?,?,?,?)",
                   (event_id, "ttd/nepal-licence", instance_id, now()))
        event(db, "native-altinn", "NATIVE_ALTINN_TASK_COMPLETED",
              "Native Altinn instance " + instance_id + " completed its data task; delivered to synthetic Nagarik bridge")
        message(db, "asha", "Native Altinn application update",
                "A native Altinn app instance completed its submission task. Reference: " + instance_id
                + ". This notification is a synthetic Nagarik App integration.", None)
        db.commit()
    return {"accepted": True, "duplicate": False}


@app.get("/api/verify/{case_id}")
def verify(case_id: str, proof: str = ""):
    with conn() as db:
        row = db.execute("SELECT * FROM cases WHERE id=? AND status='approved'", (case_id,)).fetchone()
    if not row:
        return JSONResponse({"valid": False, "notice": "No matching approved demonstration document"}, status_code=404)
    expected = hmac.new(SESSION_SECRET.encode(), (row["id"] + "|" + row["updated_at"]).encode(), hashlib.sha256).hexdigest()[:24]
    if not hmac.compare_digest(proof, expected):
        return JSONResponse({"valid": False, "notice": "Demonstration proof did not match"}, status_code=403)
    return {"valid": True, "reference": row["id"], "service": SERVICES[row["service"]]["name"],
            "approved_at": row["updated_at"], "notice": "Demo HMAC only — NOT a legal digital signature"}


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
