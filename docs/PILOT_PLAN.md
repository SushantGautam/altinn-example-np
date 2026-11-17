# Proposed Nepal–Altinn proof-of-value pilot

**Purpose:** Test whether a reusable service platform reduces duplicate work and improves accountability **without replacing Nagarik App**.

## Start with one agreed service

A licence-information correction is the current **illustrative workflow**. Actual selection must involve a willing Nepali government service owner and legal/process assessment. It should be a low-risk administrative task that can be simulated without production identity or citizen records.

**Pilot participants:** sponsoring institution, responsible service owner, ICT/identity team, registry-owning agency, agency officer, local software/operations team, Norwegian technical counterparts, privacy/security reviewer, and representative users. The World Bank or other partners may be invited if relevant; no funding commitment is assumed.

## Minimum scope

1. A working native Altinn App with one form, validated fields and an auditable BPMN process.
2. A lawful, sandbox-only identity integration or explicitly labelled test identities; do not imply real Nepal eID before approval.
3. A replaceable registry connector reading **approved sample data**; no uncontrolled copying of population records.
4. Agency officer processing owned by the agency, with demonstrable permissions and separation of duties.
5. Status tracking and a notification callback to an agreed test interface, with test delivery acknowledgements and retries.
6. A second small service reusing components to measure actual development effort.

The current repository already covers only a **subset**: item 1 in native Altinn LocalTest, synthetic adapter/event examples from items 3 and 5, and *simulated* versions of other roles. Native approval, enterprise authorization and production identity are subsequent engineering work.

## Demonstration acceptance criteria

| What to measure | Evidence to collect | Status now |
|---|---|---|
| Native Altinn starts | reproducible `studioctl` run + CI logs | Verified by CI |
| Native model, XACML and BPMN compile/configure | .NET build and schema check | Verified by CI |
| Mock registry contract responds | authenticated local stub test | Verified by CI |
| Mock inbox accepts idempotent event | token and duplicate tests | Verified by CI |
| Native user's end-to-end submission to inbox | automated browser test through actual BPMN transition | **Not yet verified** |
| Shared Nepal identity trust | approved issuer, token and assurance test | **Not built** |
| Real agency approval / role policy | native approval task and tests | **Not built** |
| Native business representation and revocation | actual Altinn Access Management checks | **Not built** |
| Reuse across two services | recorded effort for both services | **Not measured** |
| Reliability, security and operating cost | independent pilot report | **Not measured** |

## Illustrative phases, not delivery commitments

- **Discovery:** select an agency, legal basis, data fields, existing government systems, accountable owners, measurement plan.
- **Technical sandbox:** settle identity/service/registry contracts, native Altinn extension points and test identities.
- **Service pilot:** implement real officer flow and notification delivery; test unauthorized requests and failures.
- **Evaluation:** compare against the agency's current workflow using documented evidence; assess whether to expand or stop.

Avoid promising a 30-day deployment or a nationwide adoption schedule without understanding institutional approvals and integration dependencies.

## Non-technical success questions

- Does the applicant fill in less information or visit fewer counters?
- Can an officer find the case and explain who approved it?
- Can the agency reuse the same technology for a second service?
- Does the government retain control of identities, records and operations?
- Can rights be revoked without sharing passwords?
- Is the cost, security burden and maintenance workload acceptable?

**Decision gate:** approve only a further, scoped evaluation if benefits are measured and owners accept security, operational and legal requirements.

[Government brief](GOVERNMENT_BRIEF_EN.md) · [Technical due diligence](ALTINN_COMPONENT_STATUS.md).
