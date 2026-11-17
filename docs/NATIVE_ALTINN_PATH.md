# From the running native Altinn App to a complete Nepal platform

**Important distinction:** The repository includes **genuine Altinn Apps application code**. It does **not** independently deploy all Norway's national Altinn Authentication, Authorization/Access Management, Storage, Register, Events or Dialogporten services.

## 1. Verified native App baseline

Path: [`native-altinn/nepal-licence`](../native-altinn/nepal-licence/README.md).

- Official Altinn Studio v8 .NET app template, targeting .NET 10 and Altinn.App.Api/Core packages.
- Altinn UI layout, data model, BPMN application process with data task and PDF step, and XACML policy for `ttd/nepal-licence`.
- Genuine `IInstantiationProcessor` extension calls a synthetic registry adapter.
- Genuine `IProcessTaskEnd` extension can emit a synthetic, minimal task event.
- Official `studioctl env up` runs **containerized LocalTest emulators**; the default `studioctl run --mode container --detach` builds and runs the genuine Altinn App as a Docker container. The controller CLI remains on the host.
- Native CI compiles app and checks configuration; LocalTest CI starts app, verifies route, and tests bridge contracts.

```bash
bash scripts/start-native.sh
# http://local.altinn.cloud:8000/ttd/nepal-licence/
```

```bash
./demo up
# native Altinn :8000 and separate Nepal simulator :8085
```

The synthetic bridge demonstrates local **system-to-system data exchange** only. It is not NepalID/Altinn SSO and does not perform end-user identity mapping. The browser simulator's company delegation and officer review remain **local simulator logic**.

## 2. Component gap map

| Goal | Current baseline | Work required for actual national infrastructure |
|---|---|---|
| Altinn Apps | Genuine app present | Add native officer approval task and production-grade process controls |
| Authentication | LocalTest emulator; separate Keycloak OIDC simulator | Approved Nepal eID/IdP federation, token exchange/assurance, session security, recovery |
| Authorization | LocalTest policy evaluator; simulated company grants | Real resource registry, Access Management, verifiable Nepal party/company roles, policy enforcement |
| Storage | LocalTest API emulator | Production service storage, databases/blobs, encryption, backup, retention, operations |
| Registers | LocalTest parties + synthetic transport fixture | Authorized connectors to Nepal registers and agency systems |
| Events/notification | Native app custom callback to mock inbox | Reliable event architecture, recipient mapping and actual Nagarik mobile API access |
| Dialogporten/service overview | Not deployed | Evaluate need and integration separately |
| Nagarik Web | Not deployed | Government decision; browser authentication/UI consuming shared backend |
| National hosting | Single-laptop stack | Infrastructure, IaC, deployment topology, secrets, HA, disaster recovery, audit, SLA |

**Do not say `studioctl` alone deploys the complete Altinn ecosystem.** It is the developer workflow for Altinn Apps plus emulated platform endpoints. [Official documentation](https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/).

## 3. Recommended engineering sequence

### Stage A — prove native workflow end to end

Implement and automate a native Altinn **test-user login → instance creation → form filling → task completion → event in mock inbox** journey. Replace the current one-shot/best-effort callback with a tested event delivery contract if the pilot requires reliability. This is an engineering acceptance test, not a claim of a working government service.

### Stage B — add genuine agency processing

Define BPMN steps for officer review and potential request for correction. Use Altinn policy and real service-specific permissions, not `api/main.py`'s synthetic `maya` role. Agree with a real agency on what must remain in its authoritative case management system.

### Stage C — verified identity and representation

Inventory Nepal's existing identity issuer(s), mobile Nagarik authentication capabilities, company/civil registry identity linkages and relevant law. Configure an approved IdP in the appropriate Altinn Authentication environment. Do not equate a configured Keycloak URL with approval. Implement genuine Access Management or an approved substitute, and test scoped grants/revocation.

### Stage D — independently operated shared services

With official Altinn maintainers and Nepal institutions, assess which components will be deployed, adapted, integrated with existing national infrastructure, or not adopted. Evaluate real upstream service repositories and their dependencies before drafting a one-command installer. Requirements include secrets, service auth, storage, cloud/Kubernetes, observability, data protection, integration and support.

### Stage E — citizen channels

Integrate the existing **mobile Nagarik App** through an approved API or routing mechanism. If the government later launches **Nagarik Web**, it may reuse the same application service APIs and rights evaluation after browser-specific assurance and security work. The presentation portal in this repository is **not** that web channel.

### Stage F — independently evaluate

Demonstrate two services reusing infrastructure; measure build effort, user burden, decision traceability, support cost, reliability, inclusivity and operating cost. Seek approvals before a wider rollout.

## 4. What constitutes evidence?

- **Source imported/compiled** is not evidence that the full platform is deployed.
- **LocalTest running** is evidence of compatible application execution **against an emulator**.
- **Bridge endpoint tests** verify HTTP contracts, not national ID integration or guaranteed delivery.
- **Native browser journey + server-side policy tests** verify an end-to-end pilot workflow.
- **Independent production service deployment with audited integrations** would be required for an authentic full-platform claim.

The latest [component status matrix](ALTINN_COMPONENT_STATUS.md), [architecture](ARCHITECTURE.md) and [pilot plan](PILOT_PLAN.md) should be reviewed at every milestone.

## Official technical material

- [Altinn Studio local app development with studioctl](https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/)
- [Altinn Authentication and external IdPs](https://docs.altinn.studio/en/authorization/getting-started/authentication/)
- [Altinn app IdP configuration](https://docs.altinn.studio/en/altinn-studio/v8/reference/configuration/authentication/)
- [Altinn Authorization](https://docs.altinn.studio/en/authorization/)
- [Altinn architecture](https://docs.altinn.studio/en/technology/architecture/altinn-landscape/)
- [Altinn app-localtest source](https://github.com/Altinn/app-localtest)

## Dockerized local development and demonstration

`./demo up` launches all demonstration runtime services inside Docker, including the native Altinn App. Its image is built through official `studioctl run --mode container`. Docker Compose manages the Nepal simulator and the separate synthetic agency federation stack. `./demo down` stops all three environments; `./demo clean --yes` removes portal, synthetic agency and exchange audit volumes (LocalTest data is managed separately). A host .NET SDK is not needed. [Docker operations](DOCKER.md).
