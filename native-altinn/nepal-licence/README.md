# Nepal licence correction — genuine Altinn App source

This is a **native Altinn Studio v8 application**, adapted from the official .NET template. It is the **real Altinn Apps runtime**, with native form/model, BPMN process, XACML application policy and two standard Altinn lifecycle extension hooks. For local development it uses **LocalTest emulators** for shared Norwegian platform endpoints; these are **not** independently deployed national production microservices.

App ID: **`ttd/nepal-licence`** (`ttd` is a Norwegian local test organisation identifier, **not a Nepali agency**).

## Start

For the all-Docker showcase, install Docker/Compose and the official `studioctl` CLI on the host ([instructions](https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/)). A host .NET 10 SDK is **not required**; the build SDK is inside Docker. Engineers may optionally install .NET for process-mode development.

From the repository root:

```bash
bash scripts/start-native.sh
# http://local.altinn.cloud:8000/ttd/nepal-licence/
```

Or, after installing `studioctl`:

```bash
cd native-altinn/nepal-licence
studioctl doctor
studioctl env up
studioctl run --mode container --detach
```

Use a **LocalTest test user** at the native app login. The Nepal simulator's `asha`, `maya`, `raj`, `priya`, and `kiran` Keycloak credentials **cannot** sign in to this app. There is **no NepalID or BankID integration**.

## Actual components in this folder

| File | Purpose |
|---|---|
| `App/Program.cs` | Registers actual Altinn runtime services, prefill and task-end hooks |
| `App/App.csproj` | Native Altinn.App.Api/Core package dependencies |
| `App/config/process/process.bpmn` | Native Altinn workflow: data task and PDF step, **not officer approval** |
| `App/config/authorization/policy.xml` | Native XACML policy; still uses Norwegian local test roles |
| `App/config/applicationmetadata.json` | Application metadata/data types |
| `App/models/model.cs`, `model.schema.json`, `model.xsd` | C#/JSON/XSD representations of licence number, address and reason |
| `App/ui/form/layouts/Side1.json` | Native Altinn form and field bindings |
| `App/logic/NepalRegistryPrefill.cs` | Genuine `IInstantiationProcessor` and replaceable synthetic DoTM registry client |
| `App/logic/NativeNagarikTaskEnd.cs` | Genuine `IProcessTaskEnd` and optional synthetic Nagarik-event callback |

## Combined Nepal demonstration

```bash
# From the repository root:
./demo up
```

Native Altinn uses **http://local.altinn.cloud:8000/ttd/nepal-licence/**, and the separate Nepal presentation simulator uses **http://localhost:8085**.

In combined mode the launcher gives both processes the same ephemeral local bridge token. The native prefill hook can call `GET /api/stubs/dotm/licence`; the task-end hook can call `POST /api/integrations/native-altinn/events` on the separate simulator. Both carry only **synthetic** data. With no optional bridge the native app uses an explicit synthetic fallback and no notification callback.

The simulated Nagarik inbox currently delivers the task event to **fictional Asha**, not to a real Altinn applicant. Neither backend offers single sign-on across native Altinn and Keycloak, real government notifications, or a legal licence amendment.

## What's still absent

A completed native browser-submission-to-callback integration test, native officer review task, real Altinn Access Management delegation, approved Nepal identity federation, independent Altinn shared production services, and authoritative DoTM/registries. The repo's separate simulator illustrates some of these **as scenarios only**.

Build and validate:

```bash
python3 scripts/check_native.py
dotnet build native-altinn/nepal-licence/App/App.csproj --configuration Release
```

The `native-altinn.yml` and `native-localtest.yml` workflows run these checks and start the actual native app/LocalTest stack in CI.

**Use fictional records only; never enter real personal or licence data.** Upstream: [source attribution](UPSTREAM.md). Detailed guides: [developer handbook](../../docs/DEVELOPER_GUIDE.md), [component status](../../docs/ALTINN_COMPONENT_STATUS.md), [native integration roadmap](../../docs/NATIVE_ALTINN_PATH.md).

## Docker container lifecycle

The official `studioctl run --mode container` builds and starts the genuine Altinn App container (`localtest-app-nepal-licence`). `./demo up` additionally starts Keycloak/portal via Compose, joins the native app to the synthetic portal network, and injects an ephemeral bridge config into `/tmp/altinn-nepal-bridge.json` without baking a token into the image. `./demo down` stops both environments; LocalTest emulators remain emulators. [Docker operations](../../docs/DOCKER.md).
