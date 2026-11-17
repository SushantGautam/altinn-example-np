# Meeting walkthrough

**Audience:** ministers, secretaries, agency leaders and technical partners  
**Duration:** about 10 minutes  
**Preparation:** run `./demo up`; confirm both local sites load before the meeting.

This demonstration is an independent reference project using fictional records. It is not connected to Nagarik App, a Nepal government register or a production Altinn platform.

## Opening (1 minute)

Nepal already has Nagarik App. The purpose here is not to build another citizen app. We want to test whether several government institutions can reuse the same service-building tools, permissions and processing infrastructure while retaining control of their own records.

The project has two windows. One runs an actual Altinn application with official local test services. The other is a Nepal-focused simulator that illustrates the citizen and agency experience. **They do not have shared sign-in or a single production workflow.**

## Window 1: what the citizen and officer see (3 minutes)

Open **http://localhost:8085**.

1. Sign in as `asha` with `Demo123!`. Submit a fictional driving-licence correction.
2. Sign out and sign in as `maya`. Show the transport officer's review and decision.
3. Return to `asha` to show the case status and simulated inbox.

Explain that the familiar front-end experience could eventually be available through approved government channels. This window is **not** the Nagarik mobile app, Nagarik Web or an official transport department system.

## Window 2: acting on behalf of a business (2 minutes)

Remain in the simulator.

1. Sign in as `raj`, a fictional company director.
2. Grant `priya`, an accountant, permission to submit a specified transport-permit application.
3. Sign in as `priya`, submit, then revoke the permission as `raj`.
4. Show that a further attempt is refused.

The important point is a limited, revocable permission without password sharing. This behavior is implemented in the simulator; it is **not yet genuine Altinn Access Management**.

## Window 3: native Altinn and agency connections (3 minutes)

Open **http://local.altinn.cloud:8000/ttd/nepal-licence/**.

Use an **Altinn LocalTest** identity, not the Keycloak accounts above. Show the real Altinn form, its application process and its test-data prefill. The native application uses Altinn .NET libraries, UI configuration, BPMN and XACML. Shared Storage, Authentication, Authorization and Register APIs are provided by the official **LocalTest emulators**.

If the test environment is stable, submit a sample form and inspect the task event through the local integration. The CI suite checks startup and integration contracts, but does not yet automate every native browser action.

For an engineering audience, open **http://localhost:8090** to show the synthetic interagency exchange dashboard. It uses separate Docker networks, locally generated certificates for mutual TLS, Keycloak service tokens and a demonstration event/audit flow. These are local examples, not government-accredited infrastructure.

## Close (1 minute)

A sensible next step would be a small technical pilot with one willing Nepali government institution, one service owner and a defined administrative process. The pilot should use test records and measure the time to build a service, the effort to reuse components, operational requirements and actual user benefit.

**Request at the meeting:** nominate a policy contact and technical counterpart to assess feasibility against Nepal's current digital-government plans. Do not ask for a nationwide platform commitment.

## Questions likely to arise

| Question | Short answer |
| --- | --- |
| Does this replace Nagarik App? | No. Nagarik can remain the mobile entry point. |
| Is BankID included? | No. Nepal would need an approved identity provider and federation work. |
| Is all of Altinn running here? | No. A genuine Altinn application runs against LocalTest emulators. |
| Can officers and accountants use this today? | Only in the synthetic local simulator. |
| Are agency records live? | No. All identities, companies, licences and decisions are fictional. |
| Who would operate it in Nepal? | That is a core question for a government-led pilot. |

## After the meeting

Run `./demo down` to stop the containers. It preserves local demonstration records. Use `./demo clean --yes` only when you intend to remove simulator data.

See [component status](ALTINN_COMPONENT_STATUS.md) and [architecture](ARCHITECTURE.md) for implementation details, and [pilot plan](PILOT_PLAN.md) for evaluation criteria.
