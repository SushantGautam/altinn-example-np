# Nepal agency adapters — suggested integration contracts

These interfaces are **illustrative**, not approved APIs of the Nepali government. No live connection exists.

## Adapter boundaries

| Institution | Data/service | Current demonstration | Intended production adapter |
|---|---|---|---|
| National identity / Nepali ID provider | OIDC verified identity, stable subject, assurance claims | Keycloak realm with synthetic identities | Approved government/federated OIDC identity provider; attribute and assurance mapping |
| Population / civil registry | Verify identity and address with a lawful purpose | `connectors.get_person()` | Read-only authenticated registry API, minimal disclosure, legal basis |
| Company registry | Company registration, authorized representatives | `connectors.get_company()` | Authoritative enterprise register API; authorized signatories, delegation lifecycle |
| DoTM | Licence lookup and application decision exchange | `connectors.get_licence()` and local officer workflow | DoTM API with case IDs, validation, callback and reconciliation |
| Nagarik App | Application launch and notification inbox | `/api/inbox` | Approved portal API or notification/event/webhook integration |
| Altinn Platform | Authentication, authorization, applications, events, storage | **Not connected.** Demo equivalents are in `main.py` | Genuine Altinn component deployment, adapters, authorization policies and Altinn Apps |

## Example request/response shapes (simulated)

Identity claim after approved authentication:

```json
{"sub":"government-stable-pseudonymous-id","iss":"https://identity.example.gov.np","acr":"government-approved-assurance-level"}
```

Registry lookup:

```http
GET /v1/people/{opaque-id}
Authorization: Bearer <service-access-token>
```

```json
{"person_id":"NP-DEMO-001","full_name":"Asha Shrestha","district":"Lalitpur","verified":true}
```

Transport licence:

```http
GET /v1/licences/DL-09418
Authorization: Bearer <service-access-token>
```

```json
{"licence_id":"DL-09418","holder_id":"NP-DEMO-001","category":"B","status":"valid"}
```

Nagarik event/callback:

```json
{"event_id":"generated-uuid","service":"licence-correction","reference":"NP-EXAMPLE","status":"approved","recipient":"opaque-subject","occurred_at":"ISO-8601"}
```

These are **proposed schemas**, not contracts published by the agencies.

## Security requirements before any production connection

- Trust identity providers only after issuer, audience, signing key, nonce, token lifetime, assurance claims, and redirect validation.
- Do not derive government roles solely from a user-controlled browser attribute. Validate organization and representation via authoritative registries and the authorization service.
- Use purpose limitation, minimum data disclosure, lawfully justified access, and per-agency audit trails; avoid indiscriminate central copies of citizen records.
- Use mutual TLS or other government-approved service authentication, network controls, secret rotation and operational monitoring.
- Define asynchronous retry, idempotent event IDs, delivery acknowledgements and reconciliation for agency integrations.
- Respect the existing Nagarik App architecture, governmental interoperability programme and national legal requirements.
- Use fake/synthetic identities and records in all demos until appropriate agreements and security controls are in place.

## Integration acceptance tests to develop with government partners

1. Verified citizen identity can be mapped to a permitted service without revealing unnecessary attributes.
2. A company director can delegate only a specific action to a named representative.
3. After revocation, a previously permitted API call is rejected.
4. A citizen application reaches the agency's actual case handler and receives a traceable callback.
5. A notification is delivered to the existing citizen channel without exposing case details to unrelated users.
6. Every cross-agency request has trace and correlation IDs, with operator accountability.
7. Outages or errors in one institution do not silently cause fraudulent approvals or lost applications.
