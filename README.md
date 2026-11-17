# Nepal Digital Government × Altinn — Working Demonstrator 🇳🇵

**Nagarik App is the mobile door people already know. The question is what common services can run behind that door — and a possible future web door — without every ministry building everything again.**

This is an **open-for-review demonstration project**, not an official Nepal government product. It brings together:

1. **A real Altinn Studio application**: official .NET Altinn Apps runtime, Altinn UI, form model, BPMN process and XACML policy. It runs with **official LocalTest emulators** for shared services.
2. **A Nepal-facing visual simulator**: citizen, transport officer, director, accountant and observer dashboards backed by fake records and **local Keycloak OpenID Connect** login.
3. **A narrow localhost integration bridge**: native Altinn can fetch a synthetic DoTM licence record and publish a task-completion event into the simulator's synthetic Nagarik inbox.

**No real Nepal government, Nagarik App, national ID, company registry, transport department, BankID or nationwide Altinn platform service is connected.** Neither source code nor screenshots should be presented as a production deployment.

## Read this first

| Audience | Document |
|---|---|
| **Government officials** | [Brief in simple English](docs/GOVERNMENT_BRIEF_EN.md) |
| **सरकारी प्रतिनिधि** | [सरल नेपालीमा परिचय](docs/GOVERNMENT_BRIEF_NP.md) |
| **Meeting presenter** | [Live presentation script](docs/PRESENTATION_SCRIPT.md) |
| **Developer / engineer** | [Installation and development](docs/DEVELOPER_GUIDE.md) |
| **Architect / technical reviewer** | [Architecture](docs/ARCHITECTURE.md) and [component status](docs/ALTINN_COMPONENT_STATUS.md) |
| **Identity and Nagarik stakeholders** | [Mobile today; possible web later](docs/IDENTITY_AND_CHANNELS.md) |
| **Project sponsor** | [Proof-of-value pilot plan](docs/PILOT_PLAN.md) |
| **All documentation** | [Documentation index](docs/README.md) |

## How Nagarik App fits

**Today:** public-facing Nagarik App is a **mobile application**. It is **not** the web interface in this repository. A Nepal government procurement scope describes **Nagarik Web** as a possible/planned web counterpart; this does not establish that the web product is operating today. [Source: Nagarik App upgrade scope, section 3.2.1](https://bolpatra.gov.np/egp/download?alfId=cm%3ABidding_Documentsnull%2Fcm%3AY2021%2Fcm%3AM1%40%40%40%40%40cf6cc693-9187-454a-9bc7-0bcf44d42e3d&docId=66495320).

**Potential future:** mobile Nagarik App and an authorized Nagarik Web could share the same **identity integration, agency services, workflows and notifications**. That needs approved Nepal identity federation, legal authority, API integrations and security engineering. The browser simulator here is a **teaching aid**, not Nagarik Web.

## Run everything locally

Prerequisites: Git, Docker with Compose v2, **.NET 10 SDK**, Python 3 for launcher, and official **`studioctl`** ([installation instructions](https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/)). The repo uses Altinn Studio **v8** template dependencies; `studioctl` itself is a **preview CLI**.

```bash
git clone https://github.com/SushantGautam/altinn-example-np.git
cd altinn-example-np
bash scripts/start-all.sh
```

| Screen | Local URL | What it really is |
|---|---|---|
| Native Altinn App | http://local.altinn.cloud:8000/ttd/nepal-licence/ | Real Altinn Apps code, LocalTest platform emulation; uses **LocalTest** identities |
| Nepal government presentation portal | http://localhost:8085 | Separate **web-based simulator**, not official Nagarik App/Web |
| Local demo IdP | http://localhost:8081 | Keycloak for simulator users, **not** Nepal eID |

```bash
# Stop both systems
bash scripts/stop-all.sh
```

For native Altinn only, use `bash scripts/start-native.sh` (same app at `local.altinn.cloud:8000`). For simulator only, use `docker compose up --build -d` (its web UI then uses `localhost:8000`). **Do not start both in their standalone modes simultaneously**, as both need port 8000. See [developer guide](docs/DEVELOPER_GUIDE.md).

### Local demo accounts — simulator only

All passwords are **`Demo123!`**; accounts are synthetic:

| Username | Persona | What to show |
|---|---|---|
| `asha` | Citizen | Licence correction, status and simulated inbox |
| `maya` | DoTM reviewing officer | Case review and decision **inside the simulator** |
| `raj` | Company director | Grant/revoke a narrow transport-permit scope **inside the simulator** |
| `priya` | Accountant | Submit for the company only when delegated **inside the simulator** |
| `kiran` | Government observer | Event log, counts, simulated connections and reset |

**These Keycloak identities are not accepted by the native Altinn LocalTest application.** Log into native Altinn using a LocalTest test user. The narrow HTTP bridge **does not provide SSO or shared identity**.

## What is real, what is not?

| Area | Status |
|---|---|
| .NET Altinn App runtime, Altinn form, BPMN, XACML and extensions | **GENUINE ALTINN APPLICATION CODE** |
| Shared Storage, Authentication, Authorization, Register/Profile used by native local app | **OFFICIAL LOCALTEST EMULATORS** |
| NepalID-style local sign-in | **REAL OIDC PROTOCOL**, synthetic Keycloak identities; no national identity proofing |
| Native DoTM prefill and task-end callback | **REAL NATIVE ALTINN HOOKS**, synthetic/localhost-only data exchange |
| Citizen/officer/accountant/delegation dashboard | **FUNCTIONAL LOCAL SIMULATOR**, not native Altinn Access Management |
| Nagarik App, Nagarik Web, real DoTM/civil/company APIs | **NOT CONNECTED** |
| Independent national-scale Altinn shared microservices | **NOT DEPLOYED** |
| Official digital signatures, legal issuance, measured citizen outcomes | **NOT IMPLEMENTED / NOT CLAIMED** |

See [complete, evidence-based status matrix](docs/ALTINN_COMPONENT_STATUS.md).

## Show the value to non-developers

The [presentation script](docs/PRESENTATION_SCRIPT.md) starts with **what changes for a citizen and government officer**, not Kubernetes or source code. Show a fictional licence correction, its visible review and inbox result, then a company director granting/revoking accountant access. Explicitly explain that the officer and business workflows are simulated today; the native Altinn app proves the actual application technology separately.

The government proposal is **reuse**, not replacement of the mobile Nagarik App: one shared layer for the service-building and operational tasks behind approved channels. A [small agency pilot](docs/PILOT_PLAN.md) should measure real benefits instead of asserting them.

## Development, checks and evidence

- [Native Altinn app source](native-altinn/nepal-licence/README.md): official template structure plus synthetic Nepal service.
- [Native Altinn path](docs/NATIVE_ALTINN_PATH.md): what is necessary beyond LocalTest for a genuine national platform.
- [API contracts](docs/INTEGRATION_CONTRACTS.md): the implemented localhost stubs and *proposed* government interfaces.
- [Developer guide](docs/DEVELOPER_GUIDE.md): files, ports, configuration, tests, troubleshooting and security.
- GitHub Actions: `.github/workflows/ci.yml`, `native-altinn.yml`, `native-localtest.yml`. These build the genuine app, validate configuration, exercise the simulator, start both processes and test the synthetic HTTP contracts. They **do not** yet automate a full native browser form submission through to a task-ended callback.

## Safety and ownership

**Local presentation only.** The sample usernames, passwords, role assignments, HMAC proof, SQLite store and HTTP bridge are intentionally not production-grade. **Do not enter real ID numbers, personal data or government credentials; do not expose these endpoints publicly.**

Any Nepal deployment needs a named government owner, approved identity issuer, legal review, access-control mapping, agency integration contracts, security assurance, operations and sustainable support.

**Status reviewed: 17 November 2026.** For reproducibility and limitations, start with the [documentation index](docs/README.md).
