# Native Altinn in this repository — state of implementation

This repository now has **two distinct execution paths**, intentionally not
misrepresented as one integrated deployment.

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
delegation, officer desk, notification inbox and audit views. This is a
**functional local simulator**, not the real Altinn platform or the native
App above.

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

Present the **native Altinn App** to prove the technology is real and the
**separate simulator** to illustrate the intended Nepal-specific agency
workflow. Do not say they are integrated until the adapter and identity
federation are actually implemented and tested.
