# A common foundation for government services in Nepal

**Brief for government officials, secretaries, parliamentarians, advisers, and potential implementation partners**

## The idea in one minute

Nepal has **Nagarik App on mobile phones**. People can use one familiar place to reach different government services. But every office still needs reliable systems behind the screen: collect an application, check records, verify authority, send it to the right officer, make a decision and inform the applicant.

**We are not asking Nepal to replace Nagarik App.** We are exploring whether reusable components from Norway's **Altinn** could help agencies build and operate these behind-the-scenes processes more consistently.

Today, Nagarik App is mobile-focused. In the future, **Nagarik Web** could offer the same services through a browser, subject to government plans, trustworthy login, privacy and approval. Both channels can use common government services; the mobile app need not be discarded.

> **Plain-language example:** A citizen corrects a driving licence address. Their trusted login confirms who they are. The transport department receives the request, checks existing records, an authorized officer reviews it, and the citizen receives a result in their service inbox. The person should not have to carry the same document from one office to another.

## What would be new?

| Today / common challenge | Proposed shared capability | Why a ministry might care |
|---|---|---|
| Each service may build a separate form and process | Reusable service builder and processing workflow | Agencies can reuse components rather than rebuild everything |
| Identity is checked in multiple places | Government-approved identity integration | The same trusted identity can be recognized across eligible services |
| Someone needs to apply for a business | Permission to act on behalf of a company | An accountant can be authorized **without sharing the director's password** |
| An application moves between desks | Visible status, review tasks and event history | Easier follow-up and accountability |
| Existing records sit in other systems | Controlled connections to agency registries | Less repeated data entry, while agencies remain owners of their records |
| Citizens use different devices | Mobile today, and possibly web later | One service back end can serve several approved access channels |

This is a **potential architecture**, not proof that these problems have all been solved by the current demonstration or that no similar Nepal solution exists.

## The demonstration we built

**Part A — Genuine Altinn application:** a working Altinn App using its own .NET runtime, form, BPMN process and access policy. For local development, Altinn's official **LocalTest** software stands in for several national shared services.

**Part B — Nepal public-service illustration:** a web page on a presentation laptop shows the experiences of a citizen, transport officer, business director, accountant and government observer. It uses made-up records and a local demonstration login. **It is not Nagarik Web.**

**Small connection between them:** native Altinn can ask a mock transport registry for a licence reference and send a minimal task-completion notification to a mock Nagarik inbox.

The presentation can demonstrate a realistic **journey**, but not live national integration, real licence issuance, actual Nepal digital identity, or genuine Altinn business-delegation services.

## A low-risk first pilot

Consider **one voluntary agency** and **one administrative service** with a legally permissible digital workflow, a clear process owner and test data.

For a licence-correction *example*, the team would:

1. Show identity verification with fictional accounts; agree how an approved Nepal identity provider would replace it.
2. Show prefilled data from a synthetic public/transport registry.
3. Submit a request through a real Altinn app form.
4. Show a workflow step and the connection to a mock notification inbox.
5. Add agency review and genuine business delegation only after the responsible institutions agree on requirements, authority and API access.

Measure **time to build a second service**, applicant effort, processing effort, accessibility, support load, reliability and operating cost. Do **not** promise a numerical savings percentage without measuring it.

## What a Nepal institution must decide

- Who would own and operate shared services and the data they process?
- Which ministry/agency can authorize the pilot and provide an accountable service owner?
- Which Nepal identity provider can legally confirm users and organisations, at what assurance level?
- How does this fit current Nagarik App and national digital-transformation efforts?
- What records may be shared, and under which legal and security controls?
- What must remain in the transport department versus common infrastructure?
- How will Nepal train engineers, maintain the software, and avoid long-term dependence on external vendors?

## What is **not** being claimed

This repository does **not** contain a complete, independently operated production version of all Norway's Altinn shared microservices. It does **not** include BankID, Nepal's national identity provider, live Nagarik App integration, or real DoTM/registry APIs. The existing multi-role officer and delegated-access flow is still an **illustrative simulator**.

It is a **working technical starting point** for evaluating the possible architecture, not a government procurement decision or a finished national system.

## Proposed next meeting outcome

Ask for agreement on a **small technical discovery and pilot design**, not immediate nationwide adoption: one agency, a named technical counterpart, a test identity environment, agreed non-sensitive data/API contracts, and measurable acceptance criteria.

**Further reading:** [Nepali-language brief](GOVERNMENT_BRIEF_NP.md) · [Presenter guide](PRESENTATION_SCRIPT.md) · [Engineering status](ALTINN_COMPONENT_STATUS.md).
