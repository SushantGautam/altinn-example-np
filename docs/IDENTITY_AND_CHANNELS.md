# Identity, authentication, authorization and citizen channels

## State the channel correctly

- **Existing:** Nagarik App is a **mobile** public-service channel as described in the government procurement scope.
- **Possible future:** **Nagarik Web**, a government-run browser channel that could expose equivalent services; this is planned/proposed in procurement material, **not built here or confirmed launched**.
- **Demonstration only:** `api/static` is a web interface created to explain an ecosystem to officials. It is **not Nagarik App** and **not Nagarik Web**.
- **Reusable behind either channel:** an authenticated service API, agency process, registry adapter, authorization policy and notification mechanism. This is a proposed architecture, not yet a government integration.

Source: [Nepal procurement document, Nagarik App upgradation, section 3.2.1](https://bolpatra.gov.np/egp/download?alfId=cm%3ABidding_Documentsnull%2Fcm%3AY2021%2Fcm%3AM1%40%40%40%40%40cf6cc693-9187-454a-9bc7-0bcf44d42e3d&docId=66495320).

## Four easily confused concepts

| Term | What it means | Example |
|---|---|---|
| Identity proofing | Establishing that a real person is who they claim | National ID enrolment and verification |
| Authentication | Confirming that a known user is signing in now | BankID/ID-porten in Norway; a Nepal-approved provider in a future integration |
| Authorization | Checking what the logged-in person may do | A citizen can submit their own request; an officer can approve only assigned decisions |
| Delegation | A rights-holder allows another person/system to act on their behalf | A director gives an accountant permission to renew a specific permit |

Altinn **does not itself issue BankID**. Its Authentication component accepts established external identity providers; a full Nepal solution would require a Nepal-approved IdP and configured trust, not simply changing a login URL. Altinn documents that an app may choose only providers approved/configured at its platform authentication layer: [Authentication](https://docs.altinn.studio/en/authorization/getting-started/authentication/) and [App ID provider configuration](https://docs.altinn.studio/en/altinn-studio/v8/reference/configuration/authentication/).

## Today in this repository

**Simulator:** Keycloak 26 serves a synthetic `nepal-demo` realm with five fabricated test users. A FastAPI relying party uses an OIDC authorization code flow with PKCE and validates tokens; its own server performs demo authorization checks. This tests the protocol **not** national identity proofing or government-approved login.

**Native app:** Altinn App `ttd/nepal-licence` uses **LocalTest test users** and emulated platform Authentication / Authorization services. Its XACML policy uses Norwegian test roles, not Nepal's legal role model. It does not trust the simulator's Keycloak identity or grant table.

**Bridge:** the native app can send/receive synthetic data events via a separate local token. **A shared token between processes is not end-user single sign-on**, and events do not imply an authenticated link to a real Nagarik account.

## Future mobile + web login (not implemented)

1. Government confirms the responsible identity authority, admissible credentials, national ID linkage, inclusion/accessibility and relevant law.
2. A Nepal ID provider exposes a supported standards-based authentication mechanism, for example OIDC with appropriate assurance claims; any other permitted government IdP can be evaluated.
3. Mobile and future web apps independently initiate secure browser/system authentication; avoid shared passwords and embedded credential collection by service agencies.
4. The platform validates tokens, maps an **opaque stable user identifier** to an authorized party, and performs an authorization check for the requested action.
5. For a delegated business request, a trusted company/authority register or authorization service establishes representation and scope.
6. A service-specific backend processes the case, notifies the citizen through the approved channel, and maintains consent/audit/retention controls.

A web app will require origin rules, redirect URI registration, PKCE, short-lived sessions, CSRF protection where appropriate, access-control checks on every API, browser privacy protections and accessibility. A mobile app needs secure system-browser flows, safe redirect handling and device/storage protections. Both need secure account recovery and help for users without compatible devices.

**No assumption:** The current mobile Nagarik identity features are automatically compatible with Altinn. A real federation must be agreed with Nepal's responsible institution and tested.

## Separation-of-duties questions for the pilot

- Which authority is the identity issuer? What assurance does it give? What happens when identity data is wrong?
- How are people mapped to authoritative identity records without exposing full national IDs everywhere?
- How is a company representative verified? Who can grant, see, limit and revoke an accountant's access?
- How do officers receive role-based access, and how are conflicts of interest and internal approvals enforced?
- What can a citizen see on a shared/public computer? How are sessions terminated and devices lost?
- How do elderly, rural and low-connectivity users access assistance without losing security?
- What lawful basis permits the service to retrieve or store a particular registry field?

## Integration acceptance criteria

A production pilot must demonstrate that **wrong identity / wrong organisation / expired permission / revoked permission** yields access denied, that logs distinguish authentication from authorization decisions, and that both mobile and any web channel honor the same server-enforced permissions.

Further reading: [Architecture](ARCHITECTURE.md) · [Altinn component status](ALTINN_COMPONENT_STATUS.md) · [API contracts](INTEGRATION_CONTRACTS.md).
