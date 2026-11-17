"""Functional tests: local permissions, workflow and demonstration proof."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", str(tmp_path / "test.db"))
    main.init_db()
    with TestClient(main.app) as c:
        yield c


def act(client, username):
    token = main.session_token(username)
    client.cookies.set("np_session", token)
    return {"x-csrf-token": main.csrf_value(token)}


def test_health_states_not_real_altinn(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["altinn_connected"] is False


def test_needs_authentication_and_csrf(client):
    assert client.get("/api/cases").status_code == 401
    act(client, "asha")
    assert client.post("/api/cases", json={"service": "licence-correction", "new_address": "Ward 8, Kathmandu", "reason": "Moved"}).status_code == 403


def test_citizen_to_officer_to_inbox_and_proof(client):
    headers = act(client, "asha")
    lookup = client.get("/api/registries/me")
    assert lookup.json()["person"]["nid"] == "NP-DEMO-001"
    result = client.post("/api/cases", json={"service": "licence-correction", "new_address": "Ward 8, Kathmandu", "reason": "Moved residence"}, headers=headers)
    assert result.status_code == 200, result.text
    case_id = result.json()["case_id"]
    headers = act(client, "maya")
    decision = client.patch("/api/cases/" + case_id + "/decision", json={"status": "approved", "note": "Synthetic documents match"}, headers=headers)
    assert decision.status_code == 200, decision.text
    assert decision.json()["case"]["status"] == "approved"
    proof_url = decision.json()["case"]["verification_url"]
    assert client.get(proof_url).json()["valid"] is True
    assert client.get("/api/verify/" + case_id + "?proof=bad").status_code == 403
    headers = act(client, "asha")
    inbox = client.get("/api/inbox").json()["notifications"]
    assert any(x["case_id"] == case_id for x in inbox)
    assert any(x["id"] == case_id for x in client.get("/api/cases").json()["cases"])
    assert client.patch("/api/cases/" + case_id + "/decision", json={"status": "rejected", "note": "No"}, headers=headers).status_code == 403


def test_delegation_required_and_immediately_revocable(client):
    headers = act(client, "priya")
    payload = {"service": "transport-permit", "permit": "TP-12345", "reason": "Annual renewal"}
    assert client.post("/api/cases", json=payload, headers=headers).status_code == 403
    headers = act(client, "raj")
    res = client.post("/api/delegations", json={"grantee": "priya", "scope": "transport-permit"}, headers=headers)
    assert res.status_code == 200, res.text
    delegation_id = client.get("/api/delegations").json()["delegations"][0]["id"]
    headers = act(client, "priya")
    assert client.post("/api/cases", json=payload, headers=headers).status_code == 200
    assert client.get("/api/registries/company").status_code == 200
    headers = act(client, "raj")
    assert client.delete("/api/delegations/" + str(delegation_id), headers=headers).status_code == 200
    headers = act(client, "priya")
    assert client.post("/api/cases", json=payload, headers=headers).status_code == 403
    assert client.get("/api/registries/company").status_code == 403
    assert client.get("/api/cases").json()["cases"] == []


def test_observer_cannot_access_personal_cases(client):
    headers = act(client, "kiran")
    assert client.get("/api/cases").json()["cases"] == []
    assert client.get("/api/audit").status_code == 200
    assert client.get("/api/registries/me").status_code == 403
    assert client.post("/api/demo/reset", json={}, headers=headers).status_code == 200


def test_local_native_altinn_callback_is_authenticated_idempotent_and_visible(client, monkeypatch):
    monkeypatch.setattr(main, "NATIVE_WEBHOOK_TOKEN", "unit-test-secret-only")
    event = {"source": "ttd/nepal-licence", "event_type": "native.altinn.task.completed",
             "event_id": "native.12345.abcdef.Task_1", "instance_id": "12345/abcdef"}
    assert client.post("/api/integrations/native-altinn/events", json=event).status_code == 403
    bad = dict(event, source="other-app")
    assert client.post("/api/integrations/native-altinn/events", json=bad,
                       headers={"x-native-demo-token": "unit-test-secret-only"}).status_code == 422
    response = client.post("/api/integrations/native-altinn/events", json=event,
                           headers={"x-native-demo-token": "unit-test-secret-only"})
    assert response.status_code == 200, response.text
    assert response.json() == {"accepted": True, "duplicate": False}
    assert client.post("/api/integrations/native-altinn/events", json=event,
                       headers={"x-native-demo-token": "unit-test-secret-only"}).json()["duplicate"]
    act(client, "asha")
    messages = client.get("/api/inbox").json()["notifications"]
    assert len([x for x in messages if "Native Altinn" in x["title"]]) == 1
