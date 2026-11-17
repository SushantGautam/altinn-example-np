"""Nepal multi-agency network reference implementation (SYNTHETIC RECORDS ONLY).

Modes:
  broker  -- public localhost dashboard and cross-agency authenticated exchange
  edge    -- agency-specific OAuth2 resource server, separate network edge
  records -- agency-owned data store, reachable only on private Docker network

This is a security and deployment demonstration, NOT a national government system.
"""
import asyncio
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import httpx
import jwt
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from jwt import PyJWKClient

MODE = os.getenv("MODE", "broker")
AGENCY = os.getenv("AGENCY", "transport")
DB = os.getenv("DB_PATH", "/tmp/federation.db")
ISSUER = os.getenv("KEYCLOAK_ISSUER", "http://localhost:8081/realms/nepal-demo")
AUDIENCE = os.getenv("OAUTH_AUDIENCE", "interagency-api")
AGENCIES = {
    "transport": ("DL-NP-SYNTHETIC-001", "Department of Transport Management (sample only)"),
    "civil": ("CIV-NP-SYNTHETIC-001", "National Civil Registry (sample only)"),
    "company": ("CO-NP-SYNTHETIC-001", "Company Registrar (sample only)"),
}
REF_PATTERN = re.compile(r"^[A-Z][A-Z0-9-]{7,63}$")
PERMISSIONS = {agency: "agency-" + agency + "-read" for agency in AGENCIES}
CLIENTS = {"interagency-broker", "agency-transport-probe"}

def agency_tls_client(timeout=5):
    """Mutual-TLS transport for cross-institution calls (local demo CA)."""
    return httpx.AsyncClient(
        timeout=timeout,
        verify="/pki/ca.crt",
        cert=("/pki/tls.crt", "/pki/tls.key"),
    )

PRESENTATION_CHANNEL = "LOCAL_PRESENTATION_ONLY"
_jwks = None
_cached_token = ""
_token_expires = 0.0


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db_connection():
    Path(DB).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with db_connection() as conn:
        if MODE == "records":
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS records (
                    reference TEXT PRIMARY KEY, agency TEXT NOT NULL, payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS request_nonces (
                    nonce TEXT PRIMARY KEY, created_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS access_log (
                    correlation_id TEXT NOT NULL, created_at TEXT NOT NULL,
                    agency TEXT NOT NULL, reference TEXT NOT NULL,
                    purpose TEXT NOT NULL, decision TEXT NOT NULL
                );
            """)
            reference, source = AGENCIES[AGENCY]
            payload = {
                "reference": reference, "source": source, "recordType": AGENCY,
                "status": "verified-in-fictional-registry", "isSynthetic": True,
                "maskedHolder": "DEMO-****", "agencyOwnsRecord": True,
            }
            conn.execute(
                "INSERT OR IGNORE INTO records(reference, agency, payload) VALUES(?,?,?)",
                (reference, AGENCY, json.dumps(payload))
            )
        elif MODE == "broker":
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS exchanges (
                    id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, agency TEXT NOT NULL,
                    reference TEXT NOT NULL, action TEXT NOT NULL, outcome TEXT NOT NULL,
                    code INTEGER NOT NULL, detail TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS outbox (
                    event_id TEXT PRIMARY KEY, payload TEXT NOT NULL, state TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0, next_try INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
                );
            """)


async def delivery_worker():
    # Retryable durable local outbox (in prod use HA broker, DLQ, metrics and tracing).
    while True:
        try:
            if MODE == "broker":
                with db_connection() as conn:
                    items = conn.execute(
                        "SELECT event_id,payload,attempts FROM outbox WHERE state='queued' "
                        "AND next_try <= ? ORDER BY created_at LIMIT 10", (int(time.time()),)
                    ).fetchall()
                for item in items:
                    token = os.getenv("NATIVE_WEBHOOK_TOKEN", "")
                    target = os.getenv("PORTAL_CALLBACK_URL", "")
                    if not token or not target:
                        continue
                    try:
                        async with httpx.AsyncClient(timeout=3) as client:
                            result = await client.post(
                                target, json=json.loads(item["payload"]),
                                headers={"x-native-demo-token": token}
                            )
                            result.raise_for_status()
                        with db_connection() as conn:
                            conn.execute(
                                "UPDATE outbox SET state='delivered',attempts=attempts+1,last_error='' "
                                "WHERE event_id=?", (item["event_id"],)
                            )
                    except Exception as error:
                        # Keep the error short, never persist authorization headers.
                        delay = min(2 ** min(int(item["attempts"]) + 1, 7), 120)
                        with db_connection() as conn:
                            conn.execute(
                                "UPDATE outbox SET attempts=attempts+1, next_try=?, last_error=? "
                                "WHERE event_id=?",
                                (int(time.time()) + delay, type(error).__name__, item["event_id"])
                            )
        except Exception:
            # Any unexpected worker failure leaves persisted events for a later iteration.
            pass
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app):
    init_db()
    background = asyncio.create_task(delivery_worker()) if MODE == "broker" else None
    try:
        yield
    finally:
        if background is not None:
            background.cancel()
            try:
                await background
            except asyncio.CancelledError:
                pass


app = FastAPI(
    title="Synthetic Nepal inter-agency exchange",
    description="Multi-network OAuth machine-to-machine reference; NO real government data.",
    lifespan=lifespan,
    docs_url="/api/docs" if MODE == "broker" else None,
)


@app.get("/health")
def health():
    return {"ok": True, "service": MODE, "agency": AGENCY if MODE != "broker" else None}


def demo_token(request: Request):
    good = os.getenv("NATIVE_WEBHOOK_TOKEN", "")
    supplied = request.headers.get("x-native-demo-token", "")
    if not good or not supplied or not hmac.compare_digest(good, supplied):
        raise HTTPException(403, "Invalid local Altinn-to-exchange demo token")


def audit(agency: str, reference: str, action: str, outcome: str, code: int, detail: str,
          correlation_id: str | None = None):
    correlation_id = correlation_id or str(uuid.uuid4())
    with db_connection() as conn:
        conn.execute(
            "INSERT INTO exchanges VALUES(?,?,?,?,?,?,?,?)",
            (correlation_id, utcnow(), agency, reference, action, outcome, code, detail)
        )
    return correlation_id


async def oauth_client_token(client_id=None, client_secret=None):
    global _cached_token, _token_expires
    default_client = client_id is None
    if default_client and _cached_token and time.time() < _token_expires - 15:
        return _cached_token
    params = {
        "grant_type": "client_credentials",
        "client_id": client_id or os.getenv("OAUTH_CLIENT_ID", "interagency-broker"),
        "client_secret": client_secret if client_secret is not None else os.getenv("OAUTH_CLIENT_SECRET", ""),
    }
    try:
        async with httpx.AsyncClient(timeout=6) as client:
            response = await client.post(os.environ["KEYCLOAK_TOKEN_URL"], data=params)
            response.raise_for_status()
            data = response.json()
        if default_client:
            _cached_token = data["access_token"]
            _token_expires = time.time() + int(data.get("expires_in", 40))
        return data["access_token"]
    except (httpx.HTTPError, KeyError, ValueError) as error:
        raise HTTPException(503, "Identity provider is temporarily unavailable") from error


async def contact_agency(agency: str, reference: str, credential: str | None):
    if agency not in AGENCIES or not REF_PATTERN.fullmatch(reference):
        raise HTTPException(422, "Agency or synthetic reference is invalid")
    url = os.getenv(agency.upper() + "_EDGE_URL", f"http://{agency}-edge:8000")
    correlation_id = str(uuid.uuid4())
    headers = {"x-correlation-id": correlation_id,
               "x-data-purpose": "synthetic-service-delivery"}
    if credential is not None:
        headers["Authorization"] = "Bearer " + credential
    try:
        async with agency_tls_client(timeout=5) as client:
            response = await client.get(
                url + "/v1/records/" + reference, headers=headers
            )
    except httpx.HTTPError as error:
        audit(agency, reference, "read", "UNAVAILABLE", 503,
              type(error).__name__, correlation_id)
        raise HTTPException(503, "Agency gateway is unreachable") from error
    state = "PERMITTED" if response.status_code == 200 else "DENIED"
    trace_id = audit(agency, reference, "read", state, response.status_code,
                     "OAuth bearer token" if credential else "missing token",
                     correlation_id)
    if response.status_code != 200:
        # Gateways never return arbitrary registry content on denial.
        return {"allowed": False, "agency": agency,
                "edgeStatus": response.status_code, "correlationId": trace_id}
    payload = response.json()
    return {"allowed": True, "agency": agency, "record": payload,
            "correlationId": trace_id}


if MODE == "broker":
    @app.get("/")
    def dashboard():
        return FileResponse(Path(__file__).with_name("dashboard.html"))

    @app.get("/v1/topology")
    def topology():
        return {
            "title": "Nepal inter-agency exchange — isolated Docker networks",
            "realAltinnApp": True, "altinnSharedServices": "official LocalTest emulators",
            "governmentConnections": False, "channel": PRESENTATION_CHANNEL,
            "networks": [
                {"name": "presentation", "members": ["Keycloak", "Nepal visual portal", "exchange broker", "Altinn App bridge"]},
                {"name": "exchange", "members": ["exchange broker", "transport edge", "civil edge", "company edge"]},
                {"name": "transport-private", "members": ["transport edge", "DoTM registry", "DoTM SQLite volume"]},
                {"name": "civil-private", "members": ["civil edge", "civil registry", "civil SQLite volume"]},
                {"name": "company-private", "members": ["company edge", "company registry", "company SQLite volume"]},
            ],
            "trust": "OAuth2 client_credentials + JWKS signed JWT + issuer/audience/agency role checks",
            "caveat": "Separate Docker bridge networks simulate boundary, NOT separate data centers, mTLS, firewalls, VPNs or production service assurance",
        }

    @app.get("/v1/audit")
    def audit_view():
        with db_connection() as conn:
            events = conn.execute("SELECT * FROM exchanges ORDER BY timestamp DESC, rowid DESC LIMIT 100").fetchall()
            outbox = conn.execute("SELECT event_id,state,attempts,created_at,last_error FROM outbox ORDER BY created_at DESC LIMIT 30").fetchall()
        return {"exchanges": [dict(row) for row in events], "outbox": [dict(row) for row in outbox]}

    @app.get("/v1/status")
    async def statuses():
        result = {}
        async with agency_tls_client(timeout=2) as client:
            for agency in AGENCIES:
                try:
                    url = os.environ.get(agency.upper() + "_EDGE_URL", f"http://{agency}-edge:8000")
                    r = await client.get(url + "/health")
                    result[agency] = "online" if r.status_code == 200 else "unavailable"
                except httpx.HTTPError:
                    result[agency] = "unavailable"
        return {"agencies": result, "identityMode": "real Keycloak OIDC machine tokens",
                "dataMode": "synthetic independent agency registries"}

    @app.get("/internal/jwks")
    async def published_jwks():
        # Gateways have no access to citizen-facing networks or Keycloak
        # directly. Broker's dedicated trusted JWKS endpoint forwards public keys.
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(os.environ["KEYCLOAK_JWKS_URL"])
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as error:
            raise HTTPException(503, "Unable to retrieve identity signing keys") from error

    @app.get("/v1/demo/request/{agency}")
    async def demonstrate_request(agency: str):
        if agency not in AGENCIES:
            raise HTTPException(404, "Agency not in synthetic demo")
        credential = await oauth_client_token()
        return await contact_agency(agency, AGENCIES[agency][0], credential)

    @app.get("/v1/demo/deny/{agency}")
    async def demonstrate_denial(agency: str):
        if agency not in AGENCIES:
            raise HTTPException(404, "Agency not in synthetic demo")
        return await contact_agency(agency, AGENCIES[agency][0], None)

    @app.get("/v1/demo/limited/{agency}")
    async def demonstrate_least_privilege(agency: str):
        # This genuine OAuth service account can READ TRANSPORT ONLY.
        # Other agency gateways must reject its signed, valid access token.
        if agency not in AGENCIES:
            raise HTTPException(404, "Agency not in synthetic demo")
        token = await oauth_client_token(
            "agency-transport-probe", "transport-local-example-secret-change-me"
        )
        return await contact_agency(agency, AGENCIES[agency][0], token)

    @app.get("/v1/native/dotm")
    async def native_prefill(request: Request):
        demo_token(request)
        credential = await oauth_client_token()
        result = await contact_agency("transport", AGENCIES["transport"][0], credential)
        if not result.get("allowed"):
            raise HTTPException(503, "Transport agency denied the request")
        record = result["record"]
        return {"reference": record["reference"],
                "source": "OAuth-verified exchange → " + record["source"]}

    @app.post("/v1/native/events", status_code=202)
    async def native_event(request: Request, body: dict):
        demo_token(request)
        eid = str(body.get("event_id", ""))
        iid = str(body.get("instance_id", ""))
        if (body.get("source") != "ttd/nepal-licence"
            or body.get("event_type") != "native.altinn.task.completed"
            or not 8 <= len(eid) <= 128 or not 8 <= len(iid) <= 128
            or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._/" for c in eid + iid)):
            raise HTTPException(422, "Malformed synthetic native Altinn event")
        with db_connection() as conn:
            existing = conn.execute("SELECT state FROM outbox WHERE event_id=?", (eid,)).fetchone()
            if existing:
                return {"queued": True, "duplicate": True, "state": existing["state"]}
            conn.execute(
                "INSERT INTO outbox(event_id,payload,state,created_at) VALUES(?,?,'queued',?)",
                (eid, json.dumps({"source": body["source"], "event_type": body["event_type"],
                                  "event_id": eid, "instance_id": iid}), utcnow())
            )
        audit("nagarik", iid, "notification", "QUEUED", 202,
              "Durable local outbox; delivery retry worker")
        return {"queued": True, "duplicate": False, "state": "queued"}


if MODE == "edge":
    jwk_source = os.getenv("JWKS_URL", "http://exchange-broker:8000/internal/jwks")
    _jwks = PyJWKClient(jwk_source, cache_keys=True)

    def resource_token(request: Request):
        auth = request.headers.get("authorization", "")
        if not auth.lower().startswith("bearer "):
            raise HTTPException(401, "Bearer token required")
        encoded = auth.split(" ", 1)[1].strip()
        try:
            key = _jwks.get_signing_key_from_jwt(encoded).key
            claims = jwt.decode(
                encoded, key, algorithms=["RS256"], issuer=ISSUER,
                audience=AUDIENCE, options={"require": ["exp", "iss", "aud"]}
            )
        except Exception as error:
            raise HTTPException(401, "Invalid or unverifiable OAuth access token") from error
        if claims.get("azp") not in CLIENTS:
            raise HTTPException(403, "Untrusted OAuth client")
        if PERMISSIONS[AGENCY] not in claims.get("realm_access", {}).get("roles", []):
            raise HTTPException(403, "Missing agency-specific permission")
        return claims

    @app.get("/v1/records/{reference}")
    async def read_record(reference: str, request: Request):
        resource_token(request)
        purpose = request.headers.get("x-data-purpose", "")
        correlation_id = request.headers.get("x-correlation-id", "")
        if purpose != "synthetic-service-delivery":
            raise HTTPException(403, "Data access requires an approved, declared purpose")
        try:
            uuid.UUID(correlation_id)
        except ValueError as error:
            raise HTTPException(422, "Invalid cross-agency correlation ID") from error
        if not REF_PATTERN.fullmatch(reference):
            raise HTTPException(422, "Invalid synthetic record reference")
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(16)
        path = "/internal/records/" + reference
        signing_text = f"{timestamp}:{nonce}:GET:{path}:{purpose}:{correlation_id}"
        secret = os.environ["INTERNAL_HMAC_SECRET"].encode()
        signature = hmac.new(secret, signing_text.encode(), hashlib.sha256).hexdigest()
        try:
            async with agency_tls_client(timeout=3) as client:
                result = await client.get(os.environ["RECORD_URL"] + path,
                    headers={"x-agency-timestamp": timestamp,
                             "x-agency-nonce": nonce,
                             "x-data-purpose": purpose,
                             "x-correlation-id": correlation_id,
                             "x-agency-signature": signature})
            if result.status_code != 200:
                raise HTTPException(result.status_code, "Agency registry rejected the request")
            return result.json()
        except httpx.HTTPError as error:
            raise HTTPException(503, "Agency-owned registry unavailable") from error


if MODE == "records":
    @app.get("/internal/records/{reference}")
    def private_record(reference: str, request: Request):
        if not REF_PATTERN.fullmatch(reference):
            raise HTTPException(422, "Invalid reference")
        timestamp = request.headers.get("x-agency-timestamp", "")
        nonce = request.headers.get("x-agency-nonce", "")
        signature = request.headers.get("x-agency-signature", "")
        if not nonce or len(nonce) != 32 or not re.fullmatch(r"[0-9a-f]{32}", nonce):
            raise HTTPException(401, "Invalid internal service nonce")
        try:
            ts = int(timestamp)
            if abs(time.time() - ts) > 45:
                raise ValueError()
        except ValueError:
            raise HTTPException(401, "Expired internal request timestamp")
        purpose = request.headers.get("x-data-purpose", "")
        trace_id = request.headers.get("x-correlation-id", "")
        if purpose != "synthetic-service-delivery":
            raise HTTPException(403, "This registry denies unapproved purposes")
        try:
            uuid.UUID(trace_id)
        except ValueError as error:
            raise HTTPException(422, "Invalid request correlation ID") from error
        signing_text = f"{timestamp}:{nonce}:GET:/internal/records/{reference}:{purpose}:{trace_id}"
        expected = hmac.new(os.environ["INTERNAL_HMAC_SECRET"].encode(),
                            signing_text.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(401, "Invalid internal service signature")
        with db_connection() as conn:
            conn.execute("DELETE FROM request_nonces WHERE created_at < ?", (int(time.time()) - 120,))
            try:
                conn.execute("INSERT INTO request_nonces(nonce,created_at) VALUES(?,?)",
                             (nonce, int(time.time())))
            except sqlite3.IntegrityError:
                raise HTTPException(409, "Replayed internal service request")
            item = conn.execute("SELECT payload FROM records WHERE reference=? AND agency=?",
                                (reference, AGENCY)).fetchone()
            conn.execute(
                "INSERT INTO access_log VALUES(?,?,?,?,?,?)",
                (trace_id, utcnow(), AGENCY, reference, purpose,
                 "PERMITTED" if item else "NOT_FOUND")
            )
        if not item:
            raise HTTPException(404, "No record in this agency's synthetic registry")
        return json.loads(item["payload"])
