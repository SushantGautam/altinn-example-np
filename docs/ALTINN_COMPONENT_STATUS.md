# Native Altinn component coverage

This document is deliberately precise about the word **actual**.

| Component | Code in this repository | Running when `scripts/start-native.sh` succeeds | Completeness |
|---|---|---|---|
| Altinn Apps runtime | Official .NET 10 Altinn Studio v8 app template, Altinn.App.Api/Core | **Genuine Altinn runtime**, with synthetic Nepal form | Native app |
| Altinn app process | Official BPMN configuration and Altinn process library | **Genuine native BPMN process** | Data submission and PDF step, not officer approval |
| Altinn data model & UI | Official Altinn app UI / JSON schemas, model, C# | **Genuine native UI** | Licence request form |
| Altinn XACML policy | Official application policy template, scoped to `ttd/nepal-licence` | Evaluated by LocalTest’s authorization emulator | Does not represent Nepal roles |
| Altinn Storage | Official LocalTest API emulator | **Emulated** storage API; not the national storage microservice | Local test only |
| Altinn Authentication | Official LocalTest API emulator | **Emulated** auth + LocalTest test user login | Not BankID/ID-porten or Nepal eID |
| Altinn Authorization | Official LocalTest policy evaluation | **Emulated** authorization API and XACML policy | No real business delegation |
| Altinn Register / Profile | LocalTest emulators | **Emulated** register/profile contracts | Synthetic Norwegian test parties |
| Altinn Events / Notifications | LocalTest/test support varies | Not wired to Nepal notification pipeline | Incomplete |
| NepalDoTM registry | `INepalRegistryClient` + `SyntheticNepalRegistryClient` in native Altinn code | **Synthetic adapter**, triggers native Altinn instantiation hook | No government connection |
| Nagarik App | Legacy visual sandbox only | **Simulated** inbox, not connected to native app | No government connection |
| Business delegation | Legacy visual sandbox only | **Simulated** permissions in sandbox | Not native Altinn Access Management |

## What `studioctl` does

From `native-altinn/nepal-licence`:

```sh
studioctl doctor
studioctl env up
studioctl run
```

The .NET app can now use **Altinn's official app runtime** and connect to
LocalTest endpoints documented at https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/.

LocalTest is an **emulator** (see https://github.com/Altinn/app-localtest).
This is how Altinn developers are meant to test apps locally, but it is not
a national-scale self-hosted installation of Altinn Authentication, Authorization,
Storage, Register, Events, Notifications and Dialogporten.

## Production-grade deployment remains open

The full Norwegian platform has Norwegian national dependencies and infrastructure
(Azure/Kubernetes, registries, ID-porten/Maskinporten, identity claims, resource registry,
access management and operations). An independent Nepal deployment requires separate
engineering, approved identity assurances, service-level authorization rules,
lawful cross-agency data access and infrastructure.

**Never tell officials that the current LocalTest instance is Nepal's full,
production-ready Altinn Platform.** This repo is instead a credible native-app
integration proof of concept plus a separate scenario simulator.
