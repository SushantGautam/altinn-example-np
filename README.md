# Nepal digital services: Altinn reference implementation

A local demonstrator for exploring how Norway's Altinn technology could support digital public services in Nepal, alongside the existing Nagarik App.

This is an independent technical project. It is not a service of the Government of Nepal, the Norwegian government, Digdir, or the Altinn programme, and it has not been approved for public-service delivery.

## What this project demonstrates

The project contains three parts:

- **Native Altinn application.** A sample driving-licence information service built with the Altinn Apps .NET runtime, Altinn UI, a BPMN process, an application data model and XACML access policy. It runs against the official **LocalTest** emulators.
- **Nepal service simulator.** A separate FastAPI web application with fictional citizens, officers, companies and cases. Keycloak provides local OpenID Connect sign-in. Its officer review and business delegation are simulator features, **not** Altinn shared authorization services.
- **Local integration examples.** Native Altinn hooks call a mock transport registry and publish task events to a simulated service inbox. A separate federation example illustrates network segmentation and gateway communication with synthetic records.

No live Nepal government register, Nagarik App, national identity provider, BankID, or production Altinn shared service is connected.

## For government and programme teams

The proposal is to **complement, not replace, Nagarik App**. Nepal already has a mobile channel for citizens. The question is whether common building blocks behind government services could reduce duplicate development and make responsibilities, permissions and processing easier to manage.

A useful next step would be a small, jointly defined technical pilot with one willing institution and an agreed service. This repository is a conversation starter, not evidence of savings or a recommendation to procure a particular platform.

- [Brief for decision-makers (English)](docs/GOVERNMENT_BRIEF_EN.md)
- [सरकारी प्रतिनिधिका लागि नेपाली परिचय](docs/GOVERNMENT_BRIEF_NP.md)
- [Meeting walkthrough](docs/PRESENTATION_SCRIPT.md)
- [Proposed pilot and evaluation criteria](docs/PILOT_PLAN.md)

## Run locally

Requirements: Docker with Compose v2, Bash, Git, and the official [Altinn `studioctl` preview CLI](https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/). The application runtime is containerized; No host .NET SDK or Python runtime is required for the combined demonstration.

```bash
git clone https://github.com/SushantGautam/altinn-example-np.git
cd altinn-example-np
./demo up
./demo status
```

| Address | Purpose |
| --- | --- |
| http://localhost:8085 | Nepal service simulator |
| http://local.altinn.cloud:8000/ttd/nepal-licence/ | Native Altinn app, using LocalTest identities |
| http://localhost:8081 | Local Keycloak identity provider |

The simulator uses fictional accounts, including `asha` (citizen), `maya` (officer), `raj` (director) and `priya` (accountant), with the local-only password `Demo123!`. These credentials are intentionally public examples, not real accounts. The native Altinn app uses **different LocalTest identities**. The two systems do not share a login session.

To stop services:

```bash
./demo down
```

`./demo clean --yes` also deletes the simulator's persisted sample data. See [Docker operations](docs/DOCKER.md) for additional commands, network settings and troubleshooting. Run this project only on a trusted development machine; never expose the demo ports publicly.

## Repository layout

| Path | Contents |
| --- | --- |
| `native-altinn/nepal-licence/` | Native Altinn application, model and process |
| `api/` | Service simulator, web UI and tests |
| `identity/` | Synthetic Keycloak realm |
| `federation/`, `infra/federation/` | Interagency gateway and Docker-network simulation |
| `scripts/` | Launcher, smoke tests and configuration checks |
| `docs/` | Government, architectural and engineering documentation |
| `.github/workflows/` | Build and integration checks |

## Implementation status

| Capability | Current implementation |
| --- | --- |
| Altinn app runtime, UI, BPMN, XACML | Native application |
| Shared Altinn Authentication, Authorization, Storage and Register | Official LocalTest emulators |
| Officer decisions and business delegation | Local simulator |
| Registry read and task event | Synthetic local HTTP integration |
| Agency network separation and service authentication | Docker-based federation example |
| Nepal eID, Nagarik App and authoritative agency APIs | Not connected |
| Standalone production Altinn platform | Not deployed |

The GitHub Actions workflows validate builds, configurations, simulator behavior and local integration smoke tests. They do **not** demonstrate a full browser-driven native submission, officer approval and final delivery through real government infrastructure.

For the exact test and component boundaries, consult [component status](docs/ALTINN_COMPONENT_STATUS.md), [architecture](docs/ARCHITECTURE.md) and the [developer guide](docs/DEVELOPER_GUIDE.md).

## Working with this repository

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a change. Report security concerns using [SECURITY.md](SECURITY.md), not a public issue. The [public-release checklist](docs/PUBLIC_RELEASE_CHECKLIST.md) identifies checks required before the repository is made public.

### Attribution and licensing

The native application was adapted from the [Altinn Studio application template](https://github.com/Altinn/altinn-studio); see [upstream attribution](native-altinn/nepal-licence/UPSTREAM.md). Upstream licensing and any third-party notices must be preserved. **A project-wide license has not yet been selected; publication and reuse terms require maintainer review before public release.**

All names, credentials, company details and records in this project are fictional. Do not use real personal data, official government credentials or live registry tokens.
