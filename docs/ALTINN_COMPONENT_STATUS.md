# Component status — what has actually been implemented?

**Status: 17 November 2026.** Terms are deliberately strict.

- **Genuine Altinn:** official Altinn Studio app code now running by default as a **Docker .NET application**, with an optional developer process mode.
- **Official LocalTest emulator:** test implementation of an Altinn API contract. It is **not** the independently deployed Norwegian shared platform service.
- **Functional simulator:** locally implemented demonstration code, **not** an Altinn component.
- **Synthetic connector:** a real local HTTP integration carrying made-up records, not a government API.
- **Not implemented:** required deployment, federation, or feature is absent.

| Capability | Current implementation | Verification / remaining limit |
|---|---|---|
| Altinn Apps .NET runtime | **Genuine Altinn** (`Altinn.App.Api/Core`), `native-altinn/nepal-licence` | Builds in `native-altinn.yml`; native container starts through `studioctl run --mode container` in `containerized-native.yml` |
| Native form/UI/data model | **Genuine Altinn** layouts, model and text resources | Static consistency checks / .NET build; no full UI automation |
| BPMN workflow | **Genuine Altinn** process (data task then PDF step) | Configured and startup-tested; **not** a native officer approval workflow |
| XACML application policy | **Genuine policy** scoped to `ttd/nepal-licence` | Evaluated by LocalTest authorization emulator; still uses Norwegian LocalTest roles |
| Native app registry prefill | **Genuine `IInstantiationProcessor`** calling replaceable synthetic DoTM adapter | C# build; fake stub + token tested; native browser prefill not end-to-end UI tested |
| Native task-completed callback | **Genuine `IProcessTaskEnd`** publishes minimal fake event | C# build; bridge endpoint tested independently; whole native BPMN transition callback not browser-tested |
| Altinn Storage | **Official LocalTest emulator** | No separate national Storage service installed |
| Altinn Authentication | **Official LocalTest emulator** | LocalTest user identities; no real BankID or approved Nepal issuer |
| Altinn Authorization | **Official LocalTest emulator** | Tests app policy; no production access management/party delegation |
| Altinn Register/Profile | **Official LocalTest emulator** | Synthetic LocalTest parties; not Nepal registries |
| Altinn Events/Dialogporten/correspondence | **Not deployed** as national services | Native custom task-end callback is **not** their replacement |
| Separate simulator Keycloak | **Real OIDC protocol**, synthetic users | `ci.yml` tests OIDC and sign-ins; no identity proofing/assurance |
| Simulator case workflow | **Functional simulator** in FastAPI/SQLite | Tests case creation/decision/inbox; **not native Altinn Apps** |
| Simulator business delegation | **Functional simulator** with server-side scope/revocation | Tests 403 after revocation; **not native Altinn Authorization** |
| Simulator officer dashboard | **Functional simulator** | Not a real DoTM system |
| DoTM registry | **Synthetic in-memory + HTTP stub** | Local authenticated endpoint; no real licence lookup |
| Nagarik App inbox | **Synthetic inbox** accessible in demo web UI | Local bridge can post event; **not live Nagarik mobile app** |
| Nagarik Web | **Not implemented** | Government scope mentions future web; the demo UI is **not** an official Nagarik Web |
| Nepal eID / mobile+web SSO | **Not implemented** | No Nepal federation, no common sessions across stacks |
| BankID-like high-assurance digital identity | **Not implemented** | Local Keycloak login is not BankID |
| Real approval certificate/signature | **Not implemented** | HMAC reference is demo-only; not an electronic signature |
| Complete independent Altinn production shared-services ecosystem | **Not implemented** | Requires separate platform deployment and national adaptation |
| Government cost/benefit data | **Not measured** | Requires an institutional pilot |

## Evidence in this repository

| Workflow | What it verifies |
|---|---|
| [`ci.yml`](../.github/workflows/ci.yml) | Python API tests, authorization/CSRF, browser JS syntax, Docker Compose validation, real Keycloak OIDC demo flow, simulator event and delegation |
| [`native-altinn.yml`](../.github/workflows/native-altinn.yml) | Native model/BPMN/XACML/layout consistency, NuGet restore, compile with actual Altinn packages |
| [`native-localtest.yml`](../.github/workflows/native-localtest.yml) | Additional development-mode host-process testing, not the default |
| [`containerized-native.yml`](../.github/workflows/containerized-native.yml) | Full `./demo up` and `./demo down`, checks native app container, synthetic bridge, OIDC and teardown |

**Meaning of green CI:** it proves only the checks above passed; it does **not** mean every feature is production-safe or a real user navigated an Altinn form in a browser. CI status can change after edits; use the latest action results.

## Product and identity boundaries

- **Mobile Nagarik App:** existing public-facing product. **No current official Nagarik web presence is assumed in this repo.**
- **Potential future Nagarik Web:** government decision and engineering task, not software deployed here.
- **Demo web portal:** synthetic explanation tool, not a government channel.
- **Keycloak OIDC users:** simulator only.
- **LocalTest users:** native Altinn only.
- **Shared ephemeral HTTP token:** synthetic connector only, not federated user authentication.

## What would qualify as full national Altinn?

A validated deployment of the required shared **Authentication, Authorization/Access Management, Storage, Register, events/notification components** (or documented, integrated approved substitutes), a legal identity/party/representation model, production hosting/security/monitoring, and live agency APIs. None can be inferred simply from `studioctl env up`, which deliberately starts local emulators.

Reference: [Official Altinn studioctl local development](https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/). For next steps see [native integration path](NATIVE_ALTINN_PATH.md).

## Local all-Docker execution

`./demo up` runs every demo **runtime** in Docker: real Altinn App, official LocalTest emulators, Keycloak, Nepal simulator and databases. A host `studioctl` CLI manages Altinn's containers, but no host .NET SDK is needed. `./demo down` stops all containers and removes the shared Compose network while keeping data; `./demo clean --yes` additionally deletes simulator volume data. The independent national Altinn production microservices are **not installed**. See [Docker operations](DOCKER.md).
