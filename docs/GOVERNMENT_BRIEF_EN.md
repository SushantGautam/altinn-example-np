# Exploring shared digital services for Nepal

**Discussion note for government leaders and implementation partners**

## The question

Nagarik App already gives people a familiar mobile entry point to government services. Behind each service, however, agencies still need forms, verified records, processing rules, staff permissions and a way to report decisions.

Could Nepal reuse common components for those tasks instead of every institution building and maintaining them separately?

Norway's Altinn is one possible reference. This project explores its application technology and the work required to connect shared services. **It does not propose replacing Nagarik App**, and it does not assume that Nepal lacks similar capabilities.

## An example

A resident needs to correct information on a driving licence. In a future authorized service, the resident would sign in using an approved Nepali identity system, review information already held by government, submit a correction, and receive a clear decision. The responsible department would remain in control of the record and its decision.

A related example concerns businesses. A company director could give an accountant permission to submit a specified form without handing over a password, and revoke that permission later.

These examples are useful because they test data access, representation, workflow and accountability—not just how a form looks.

## What we can show today

The repository contains a genuine Altinn .NET application running locally with Altinn's development emulators. It also has a separate browser-based Nepal service simulator showing citizen submissions, officer decisions, business delegation and a mock inbox. A limited connector passes synthetic data between the native application and mock services.

The simulator is **not Nagarik App or Nagarik Web**. Its officer and delegation features are **not backed by the production Altinn authorization platform**. There is no live Nepal identity, transport register or government integration. All demonstration records are fictional.

## Where the government would need to decide

| Question | Proposed approach |
| --- | --- |
| Does this duplicate existing programmes? | Compare components against the current national digital-transformation architecture before committing to a pilot. |
| Who owns the service and its data? | Keep an accountable Nepali agency as the process and record owner. |
| How would a person log in? | Integrate an approved Nepal identity provider; Norway's BankID is not part of this package. |
| Can one agency act for another? | Agree legal authority, registry access, service credentials, logging and audit requirements. |
| Who would run the platform? | Test hosting, security, operations, local engineering capacity and long-term cost. |
| How do we judge value? | Measure implementation effort, applicant and officer burden, reliability, accessibility and maintenance costs. |

## A sensible first step

Invite one willing institution to select a low-risk administrative service. Appoint a service owner and technical counterpart. Agree on synthetic or approved test records, an identity test environment, security responsibilities and success criteria.

Build and test one working end-to-end service, then a second small service that reuses the same components. Review the results before considering any wider adoption.

**Decision requested:** support a limited technical discovery and pilot design—not approval to replace national systems or deploy Altinn nationwide.

For technical detail, see the [architecture](ARCHITECTURE.md), [component status](ALTINN_COMPONENT_STATUS.md) and [pilot plan](PILOT_PLAN.md). A [Nepali-language brief](GOVERNMENT_BRIEF_NP.md) is also available.
