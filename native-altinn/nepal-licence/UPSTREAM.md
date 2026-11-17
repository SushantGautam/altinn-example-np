# Upstream source and adaptation

The native Altinn application scaffold was copied and adapted from the open-source
[Altinn/altinn-studio](https://github.com/Altinn/altinn-studio) repository,
`src/App/template/v8/src`, retrieved in November 2026.

The upstream structure supplies the .NET Altinn Apps application scaffold, API/Core package references, BPMN, XACML policy, data-model structure, native UI/layout files, and deployment artefacts. This project adds a fictional Nepal driving-licence service, synthetic registry adapter and optional demonstration callback.

**Licensing:** the Altinn Studio source is MIT-licensed, with copyright retained by the Norwegian Digitalisation Agency. The full upstream license notice is reproduced in [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). This attribution is not an assertion of Norwegian government sponsorship or approval.

**Runtime truth:** this is actual Altinn App code that compiles and can be launched with official `studioctl`. Its local shared Storage/Authentication/Authorization APIs are served by **LocalTest emulators**, not a full production Altinn Platform installation.

**Identity truth:** the native App uses LocalTest test identities; it is not connected to Norway's BankID or Nepal's identity infrastructure. A separate Keycloak demo exists in the repository and is **not federated** with this app.

**Channels:** Nagarik App is currently discussed here as a **mobile channel**. A possible future Nagarik Web is outside this source tree. The repository's own web simulator is a presentation aid, not an official government channel.

For development and provenance, use [native application readme](README.md), [component matrix](../../docs/ALTINN_COMPONENT_STATUS.md), and official [studioctl documentation](https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/).
