# Developer guide — native Altinn + Nepal showcase

This guide documents the **implemented system** as of 17 November 2026. Read [architecture](ARCHITECTURE.md) and [component status](ALTINN_COMPONENT_STATUS.md) first if you need to know which services are genuine, emulated or simulated.

## Requirements

- Git and a local computer (Linux/macOS/Windows with a suitable shell).
- Docker Engine/Desktop with Docker Compose **v2**; enough memory for Keycloak and Altinn LocalTest images.
- **.NET 10 SDK** as pinned in `native-altinn/nepal-licence/global.json`.
- **Python 3** for the combined launcher’s ephemeral local integration token.
- **studioctl** CLI (currently preview): [official installer and platform-specific instructions](https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/).
- For tests: Python packages in `api/requirements.txt`. Node.js for checking browser JS syntax in CI.

Do not confuse `studioctl` with Altinn Studio Designer or with a complete national platform installer. It launches an official **local application development environment**.

## Choose one execution mode

### Mode 1 — native Altinn only

```bash
git clone https://github.com/SushantGautam/altinn-example-np.git
cd altinn-example-np
bash scripts/start-native.sh
```

- App: **http://local.altinn.cloud:8000/ttd/nepal-licence/**
- LocalTest login with a test user. **Keycloak users cannot sign in.**
- Start script calls `studioctl doctor`, `studioctl env up` and `studioctl run --detach` from the app repository.
- With no fake HTTP bridge configured, the native registry adapter returns a synthetic fallback and the notification hook does nothing.

To stop:

```bash
cd native-altinn/nepal-licence
studioctl stop
studioctl env down
```

### Mode 2 — Nepal presentation simulator only

```bash
docker compose up --build -d
```

- Web simulator: **http://localhost:8000**
- Keycloak login: **http://localhost:8081**
- Keycloak synthetic usernames: `asha`, `maya`, `raj`, `priya`, `kiran`; common password **`Demo123!`**.
- FastAPI + SQLite stores invented cases/notifications, with role checks and local OIDC login.

To stop (optional data wipe):

```bash
docker compose down
# deletes the simulator's persisted demo database:
docker compose down -v
```

**Warning:** Mode 1 and Mode 2 each use port 8000; use Mode 3 to show both.

### Mode 3 — combined showcase (for meetings)

```bash
bash scripts/start-all.sh
```

- Genuine native Altinn app: **http://local.altinn.cloud:8000/ttd/nepal-licence/**
- Nepal web simulator: **http://localhost:8085**
- Keycloak: **http://localhost:8081**

`start-all.sh` creates an ephemeral token, exports the local mock DoTM lookup and mock Nagarik event URL to the native `studioctl` app, then launches the separate presentation containers on port 8085. The native app can fetch a synthetic licence at instance creation and send an event at task completion. **Neither login is shared.** No official Nagarik web service is running.

```bash
bash scripts/stop-all.sh
```

If a detached native process was started before changing environment variables, stop/restart the native app to pick up the new bridge variables.

## Repository layout

| Path | Purpose |
|---|---|
| `native-altinn/nepal-licence/App/Program.cs` | Actual Altinn app service registration |
| `native-altinn/nepal-licence/App/config/process/process.bpmn` | Native BPMN workflow |
| `native-altinn/nepal-licence/App/config/authorization/policy.xml` | Native XACML policy |
| `native-altinn/nepal-licence/App/models/*` | Native C#/JSON Schema/XSD data model |
| `native-altinn/nepal-licence/App/ui/*` | Native Altinn form layouts and resources |
| `native-altinn/nepal-licence/App/logic/NepalRegistryPrefill.cs` | Native instantiation hook; synthetic DoTM HTTP adapter/fallback |
| `native-altinn/nepal-licence/App/logic/NativeNagarikTaskEnd.cs` | Native task-completed hook; synthetic callback |
| `identity/nepal-realm.json` | Demo Keycloak realm/accounts; **not** government identities |
| `api/main.py`, `api/connectors.py` | Simulator API, role logic and mocked records |
| `api/static/index.html`, `app.js`, `style.css` | Demo web presentation |
| `api/test_demo.py` | Simulator API/security/bridge unit tests |
| `scripts/smoke_oidc.py` | Actual Keycloak browser-protocol smoke through Python HTTP client |
| `scripts/check_native.py` | Native configuration/model consistency |
| `.github/workflows/*` | Automated build/CI/LocalTest checks |

## Tests

```bash
# Simulator API and permission checks:
python3 -m pip install -r api/requirements.txt
(cd api && python3 -m pytest -q)

# Native Altinn metadata, BPMN, form and XACML consistency:
python3 scripts/check_native.py

# Genuine native Altinn .NET build:
dotnet build native-altinn/nepal-licence/App/App.csproj --configuration Release

# Browser code syntax (if Node installed):
node --check api/static/app.js

# Compose config:
docker compose config --quiet
```

Run `scripts/smoke_oidc.py` only with the simulator and Keycloak services **running**; for port 8085 set `PORTAL_BASE_URL=http://localhost:8085`. Combined LocalTest tests are in GitHub Actions **`native-localtest.yml`**; CI starts and stops the containers.

**Known gap:** green tests do not yet show an automated native Altinn browser filling the form and advancing the BPMN task to produce a callback. Adding that scenario is useful before a high-stakes live presentation.

## Configuration / endpoints

| Environment variable | Used by | Meaning |
|---|---|---|
| `PORTAL_PORT` | Docker Compose host port | 8000 simulator alone, 8085 combined |
| `PORTAL_BASE_URL` | Simulator OIDC callback | `http://localhost:8000` or `http://localhost:8085` |
| `NATIVE_WEBHOOK_TOKEN` | Native hook and FastAPI | Shared ephemeral **local demo** token |
| `DOTM_MOCK_REGISTRY_URL` | Native `IInstantiationProcessor` adapter | Local synthetic licence lookup |
| `NAGARIK_DEMO_WEBHOOK_URL` | Native `IProcessTaskEnd` adapter | Local synthetic event receiver |
| `DB_PATH` | Simulator | Local SQLite database path |
| `OIDC_ISSUER`, `OIDC_INTERNAL` | Simulator | Browser and container endpoint for Keycloak |
| `SESSION_SECRET` | Simulator | Development-only signing secret; not for production |

### Implemented localhost bridge

```http
GET /api/stubs/dotm/licence
X-Native-Demo-Token: <ephemeral-local-token>
```

Returns synthetic `reference` and `source`. The native C# adapter maps this to a model prefill field.

```http
POST /api/integrations/native-altinn/events
X-Native-Demo-Token: <ephemeral-local-token>
Content-Type: application/json
```

Expected JSON: `{"source":"ttd/nepal-licence","event_type":"native.altinn.task.completed","event_id":"native.example.Task_1","instance_id":"TEST/12345678"}`. The API rejects wrong tokens/source/event type and deduplicates `event_id`. It creates a **fake notification for Asha**; it is not identity-aware delivery.

Full route definitions and hypothetical future agency contracts: [integration contracts](INTEGRATION_CONTRACTS.md).

## How to extend safely

- For an Altinn process change, modify `App/config/process/process.bpmn`, data types, UI and policies together; build and validate using `studioctl`.
- For a new agency connector, implement the `INepalRegistryClient` boundary with mock tests first. Only after an approved legal/API contract should it call a real service. Do **not** reuse the static local token or fake national IDs for production.
- For notifications, replace `NativeNagarikTaskEnd`'s best-effort HTTP call with an approved, authenticated event/notification transport with retries, dead-letter and recipient mapping.
- For an officer approval, implement real Altinn process tasks and resource-specific authorization; do **not** assume the simulator's `maya` role is a native Altinn role.
- For business delegation, integrate genuine Altinn Access Management or an approved government service, not the simulator's local SQLite grant table.
- For a possible Nagarik Web, build or integrate a separate approved citizen channel that shares backend APIs and identity policies with the mobile channel.

## Troubleshooting

| Symptom | Likely cause / action |
|---|---|
| Port 8000 already in use | Another stack started in standalone mode. Stop it, then `start-all.sh`. |
| Keycloak login fails at first | The identity container is still starting. Inspect `docker compose logs -f identity`. |
| `studioctl` not found | Install the preview CLI via official docs and ensure it is on your PATH. |
| .NET build failure | Verify `dotnet --info`, selected SDK and NuGet network access. |
| LocalTest stale resource conflict | Follow official `studioctl env up` cleanup guidance; remove only known orphan LocalTest resources. |
| Native page opens but no form | Review LocalTest user, app instance creation and `studioctl app logs`. Gateway 200 alone does not prove form submission. |
| Mock DoTM prefill returns fallback | HTTP endpoint unavailable / token not inherited by detached process; restart combined mode and inspect logs. |
| No native event in mock inbox | The BPMN task may not have ended, callback may have failed, or bridge was not configured. It is best-effort and uses a fixed test recipient. |
| Simulator inbox empty | Sign in as `asha`; generate a simulator decision or native event while bridge is active. |
| Schema / policy mismatch | Run `python3 scripts/check_native.py` and verify model names, form bindings, BPMN task ID and XACML scope. |

## Security warning

**Development environment only.** All synthetic users, demo secrets, LocalTest roles, HTTP transport, simple HMAC document proof and SQLite permissions are unsuitable for public production. The repo contains **no national ID proofing**. Never enter real citizen data, and do not expose localhost services via public reverse proxies. A future government pilot requires identity assurance, secret storage, HTTPS/mTLS, lawfully scoped data, policy evaluation, audit, backups, monitoring, independent review and operations ownership.

[Documentation index](README.md) · [Identity and channels](IDENTITY_AND_CHANNELS.md) · [Native component status](ALTINN_COMPONENT_STATUS.md).
