# Native Altinn in this repository — state of implementation

This repository now has **two distinct identity and workflow paths** and an
optional token-protected *synthetic event/data bridge* between them. That bridge
is not a national identity federation or production Altinn Access Management.

## A. Genuine Altinn app — implemented and builds in CI

Path: `native-altinn/nepal-licence/`.

- Uses official Altinn Studio **v8** .NET application template.
- Builds against `Altinn.App.Api` and `Altinn.App.Core` (currently 8.12.15).
- Contains a native Altinn React form, data model, BPMN process and XACML policy.
- Implements a real `IInstantiationProcessor` extension that calls the
  replaceable `INepalRegistryClient` (currently synthetic DoTM record).
- `studioctl` launches its official LocalTest environment and application
  backend, using Altinn's app process engine and platform API contracts.
- At runtime LocalTest **emulates** the shared Storage, Authentication,
  Authorization, Register, Profile and related systems.

```bash
bash scripts/start-native.sh
# http://local.altinn.cloud:8000
```

The .NET build and schema checks are automated in
`.github/workflows/native-altinn.yml`. A separate workflow,
`native-localtest.yml`, checks actual `studioctl` startup.

## B. Standalone visual scenario simulator — implemented separately

The original `docker compose up --build -d` launches the Nepal-style portal,
Keycloak OIDC provider, simulated citizen and business records, workflow,
delegation, officer desk, notification inbox and audit views. This is a **functional local simulator**. The native app now supports two optional
localhost-only connections to its registry and inbox stubs, but the simulator's
agency decisions and business delegation are not native Altinn services.

This separation is visible in the portal's **Native Altinn** navigation.

## C. Not yet integrated

| Desired production capability | Required engineering |
|---|---|
| Genuine Nepal eID / BankID-like login to Altinn | Operate an approved Nepal identity provider, configure Altinn Authentication federation, identity/assurance/token mapping and legal proofing |
| Shared Altinn Authentication microservice (not LocalTest) | Independently deploy `Altinn/altinn-authentication` and its dependencies |
| Shared Altinn Authorization, Access Management and delegation (not LocalTest) | Deploy the relevant components and registries, define Nepal party/organization roles and access policies |
| Shared Altinn Storage microservice (not LocalTest) | Deploy `Altinn/altinn-storage` with database/blob/queue/auth dependencies, ops and migration |
| Nagarik App returning native cases and notifications | Approved portal API/event contract, security, callback reconciliation and user consent |
| Live DoTM / civil / company registry adapters | Government-issued credentials, lawfully-scoped APIs, data minimization and audit |
| Real agency approval chain | Extend BPMN with a real officer task or validated agency callbacks and permissions |
| National observability, hosting and high availability | Kubernetes/cloud architecture, secrets, TLS, CI/CD, operations, SLAs, security assessment |

The Altinn national components are not a single self-contained `studioctl`
installation. They have multiple external Norwegian dependencies and local
development methods. See
https://docs.altinn.studio/en/authorization/reference/system/development-architecture/
and https://docs.altinn.studio/en/technology/architecture/altinn-landscape/.

## Government demo framing

Present the **native Altinn App** as genuine application runtime and the
**simulator** as Nepal agency workflow. The combined start command supports
only synthetic DoTM prefill and one native task-event callback; it does **not**
provide identity federation, native delegation, real agency decisions or a full
production Altinn Platform deployment.
