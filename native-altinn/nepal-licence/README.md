# Nepal licence correction — native Altinn App (v8 template)

This is an **actual Altinn App project** using Altinn.App.Api and Altinn.App.Core,
the official BPMN process engine, application metadata, native XACML policy,
data model and Altinn React UI.

Requires .NET 10 SDK, Docker/Podman/Colima, and Altinn `studioctl`.

```bash
curl -sSL https://altinn.studio/designer/api/v1/studioctl/install.sh | sh
cd native-altinn/nepal-licence
studioctl doctor
studioctl env up
studioctl run
```

Open http://local.altinn.cloud:8000 and use a **LocalTest test user**, not a
NepalID/Keycloak user. The Keycloak provider from the presentation sandbox
has not been federated into Altinn Authentication.

LocalTest emulates Norwegian Altinn's Storage, Authentication, Authorization,
Register and related platform contracts. The process runtime here is genuine
Altinn App code. XACML policy from the official template still uses **Norwegian
testing roles** `priv` and `dagl`; this is not Nepal's legal authorization.

No real government data or identity is connected. Never enter real ID numbers,
licences, permits or other personal records.

## Local synthetic Nepal integration

If launched using `bash scripts/start-all.sh` from the repository root,
`DOTM_MOCK_REGISTRY_URL` points at the protected synthetic DoTM HTTP endpoint
and `NAGARIK_DEMO_WEBHOOK_URL` points at the protected synthetic Nagarik inbox.
The native Altinn `IInstantiationProcessor` reads the DoTM mock at creation;
`IProcessTaskEnd` posts a minimal event when the data task ends. This uses a
runtime-generated local token, no real citizens or sensitive government data.
Standalone `studioctl run` uses a static synthetic prefill and disables
optional callbacks. Neither method is an identity federation.
