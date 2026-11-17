# Connecting the demonstrator to a genuine Altinn deployment

This document prevents a common misunderstanding: **an Altinn-inspired workflow is not the Altinn Platform.** The demo portal is deliberately independent of native Altinn while illustrating the value of its capabilities.

## What would constitute a genuine Altinn solution?

A real Altinn-based service would execute its application using **Altinn Apps runtime**, access **Altinn Platform** storage and authorization services or approved external equivalents, and use official Altinn authentication and integration protocols. The current repository does not include those runtimes.

Per Altinn's official documentation:

- Altinn Authentication delegates identity proofing to external identity providers such as Norway's ID-porten; it is not BankID itself.
- Altinn Authorization includes distinct Access Management, Resource Registry and policy decision responsibilities.
- Altinn LocalTest **emulates** the platform for testing an application. It is not equivalent to all national production components.
- Altinn Studio Designer is a separate development tool, not itself the full runtime.

References:
- https://docs.altinn.studio/en/technology/architecture/altinn-landscape/
- https://docs.altinn.studio/en/authorization/getting-started/authentication/
- https://docs.altinn.studio/en/authorization/reference/system/components/
- https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/

## A practical integration sequence

**Phase A: current interactive demonstrator.** Use this repository to demonstrate roles, federation, registries, officer decisions, delegation, event audit and a citizen inbox. This is what `docker compose up --build -d` starts.

**Phase B: first native Altinn app.** Create an application in a permitted Altinn Studio environment with a data model, UI layouts and process definition for the licence-correction service. Use the official `studioctl` local development workflow and its LocalTest emulator:

```bash
# Inside a genuine Altinn app repository created in Altinn Studio:
studioctl env up
studioctl run
# Visit http://local.altinn.cloud:8000
```

These commands are **not** supported by this repository alone; an actual generated Altinn app is required.

**Phase C: replace demonstrator adapters.** Introduce a Nepal-approved OIDC identity provider into an independently operated Altinn Authentication environment. Map Nepal's business register, party information, authorization and policy decisions; integrate DoTM and Nagarik through approved APIs. Be careful: the Norwegian Altinn deployment only accepts configured/approved identity providers, not an arbitrary issuer URL pasted into an application.

**Phase D: country-level infrastructure assessment.** Inventory all external Norwegian platform dependencies and services, evaluate licensing, data residency, Kubernetes, cloud services, secrets, certificate management, service-to-service identity, databases, observability, costs, runbooks, backup, reliability and support. A national rollout needs dedicated engineering and institutional ownership.

## Migration contract for this demo

| Demo route or module | Native equivalent to investigate |
|---|---|
| Keycloak and `/auth/*` | External national IdP + Altinn Authentication token/session |
| `/api/delegations` | Altinn Access Management / delegation APIs |
| `/api/cases` | Altinn Apps application runtime and Storage |
| `/api/audit` | Platform audit/event services |
| `/api/inbox` | Nagarik notification adapter; optionally Dialogporten-style service overview |
| `connectors.py` | Approved national/agency registry integrations |

Do **not** route real identity or registry data through these stub endpoints. Their entire purpose is to agree on the future interface while keeping the live government ecosystem untouched.

## Decision gate for the Norwegian–Nepali team

Before promising a single-command **full Altinn Platform** deployment, demonstrate a native app on a documented local stack, identify the Altinn components that genuinely run, list all missing components, and publish test results. That claim cannot be made on the basis of the current local presentation demo.
