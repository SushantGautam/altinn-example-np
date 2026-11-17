# Documentation guide

Choose a route based on what you need. All scenarios use **made-up data**. Nothing connects to live Nepali government systems.

| Reader | Start here | Purpose |
|---|---|---|
| Government secretary, ministry leadership, policy adviser | [Government brief — English](GOVERNMENT_BRIEF_EN.md) | The problem, public value, limits, and what a pilot would demonstrate |
| नेपालीमा पढ्न चाहने सरकारी प्रतिनिधि | [सरल नेपालीमा परिचय](GOVERNMENT_BRIEF_NP.md) | Explanation in plain Nepali, without developer terminology |
| Presenter / delegation | [Presentation walkthrough](PRESENTATION_SCRIPT.md) | What to click, what to say, and what not to claim |
| Solutions architect | [Architecture](ARCHITECTURE.md) | As-is vs future topology and trust boundaries |
| Engineers cloning the repo | [Developer guide](DEVELOPER_GUIDE.md) | Installation, commands, routes, testing and troubleshooting |
| Anyone launching the demo | [Docker operations](DOCKER.md) | All-container app runtime, one-command up/down, logs, persistence and cleanup |
| Identity, Nagarik App, web channel owners | [Identity and channels](IDENTITY_AND_CHANNELS.md) | Mobile today, possible web tomorrow, identity and security |
| Agency API integration teams | [Integration contracts](INTEGRATION_CONTRACTS.md) | Real demo endpoints and proposed future adapters |
| Technical due diligence | [Component status](ALTINN_COMPONENT_STATUS.md) | Real / emulated / simulated / absent, with verification |
| Altinn platform engineers | [Native Altinn path](NATIVE_ALTINN_PATH.md) | Migration from LocalTest to independent production services |
| Project sponsor / pilot partner | [Pilot plan](PILOT_PLAN.md) | Scope, roles, measurable results, decision gates |

## Language and source-of-truth rules

- **Current Nagarik App public channel:** mobile app. A future Nagarik Web may be developed, but is not implemented in this repository.
- **Actual Altinn in repo:** native Altinn Apps runtime (form, BPMN, XACML), running locally with **LocalTest emulators** for shared platform services.
- **Nepal visual simulator:** a **web-based presentation interface** that imitates possible service journeys; it is **not an official Nagarik Web** and does not replace or extend Nagarik App.
- **Authentication:** the simulator has a local Keycloak OIDC login. The native Altinn App uses LocalTest identities. **Not one login across both**, not BankID, and not an approved Nepal eID.
- **Local integrations:** actual native Altinn lifecycle hook code can talk to synthetic DoTM and Nagarik-inbox endpoints. No real departmental APIs, notifications, or citizen data.
- **Business delegation and officer dashboard:** real functioning demo logic in the simulator, **not native Altinn Access Management or a production agency back office**.
- **Production:** deployment of all Altinn national microservices and Nepal federation is not complete.

Status refers to code as checked on **17 November 2026**. Re-run GitHub Actions to verify after changes. Refer to source code and tests for operational truth rather than relying on a static screenshot.

## External sources

- [Altinn: local development with studioctl](https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/)
- [Altinn: authentication and external identity providers](https://docs.altinn.studio/en/authorization/getting-started/authentication/)
- [Altinn: authorization capabilities](https://docs.altinn.studio/en/authorization/)
- [Altinn: ID-provider configuration](https://docs.altinn.studio/en/altinn-studio/v8/reference/configuration/authentication/)
- [Nepal government procurement scope for Nagarik Web](https://bolpatra.gov.np/egp/download?alfId=cm%3ABidding_Documentsnull%2Fcm%3AY2021%2Fcm%3AM1%40%40%40%40%40cf6cc693-9187-454a-9bc7-0bcf44d42e3d&docId=66495320), section 3.2.1. The document describes public services through the mobile app and a proposed standalone web application. This is evidence of **intent/scope**, not proof that a web service has launched.

## Local showcase startup

Run `./demo up` then `./demo down` from the repository root. All runtime services are containers; the official `studioctl` controller still runs on the host. A host .NET SDK is not required. See [Docker operations](DOCKER.md).
