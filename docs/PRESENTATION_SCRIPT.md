# Government demonstration — a 12-minute story, not a code walkthrough

**Audience:** ministers, secretaries, senior civil servants, advisers and potential partners. The two windows use fictitious data. Introduce what is real and what is simulated before interacting with them.

## Opening in everyday language (about 1 minute)

> “Nepal already has Nagarik App on mobile. We are not bringing another app to replace it. We are exploring a common system *behind* government services: the citizen submits something once; the correct office receives it; authorized officials act; the citizen is informed. If Nepal adds Nagarik Web in future, it could use the same services, subject to approved login and security.”

A simple Nepali-language opening:

> “नागरिक एप अहिले मोबाइलमा छ। यसलाई बदल्ने होइन। सरकारी कार्यालयका पछाडिका काम—निवेदन, अभिलेख जाँच, स्वीकृति र सूचना—एउटै साझा प्रविधिबाट सजिलो बनाउन सकिन्छ कि भनेर यो नमुना देखाउँदैछौँ। भविष्यमा वेब बने पनि उही सेवाको आधार प्रयोग गर्न सकिन्छ।”

## Preparation

Launch the verified all-Docker showcase. Install Docker/Compose and the official `studioctl` CLI once; no host .NET SDK is needed:

```bash
./demo up
```

Open two browser windows:

- **Window A — Genuine Altinn App:** http://local.altinn.cloud:8000/ttd/nepal-licence/ (LocalTest users; official local platform emulators).
- **Window B — Nepal ecosystem *web simulator*:** http://localhost:8085 (Keycloak fictional users).

**Do not call Window B “Nagarik Web”.** Nagarik App is currently a mobile channel, while a web counterpart is a possible government evolution. The browser demonstration is simply a way for officials to **see the proposed ecosystem**.

## Part 1: Show the citizen and officer experience (3 minutes)

In Window B, use `asha / Demo123!` and explain that her licence details are fabricated. Submit a fake correction application. Switch identity to `maya / Demo123!` and show the government officer's review/decision. Switch back to `asha` and show the mock Nagarik inbox with the update.

**Say:** “This shows what citizens and the agency might experience.”

**Do not say:** “We have connected the real Nagarik App or DoTM” or “this officer workflow is already native Altinn.”

## Part 2: Show why permissions matter (2 minutes)

In Window B, `raj` is a fictional company director. He grants `priya` a **single service permission**, without giving his password. Priya submits a sample company permit. Raj revokes her permission; Priya tries again and the simulator rejects her request.

**Say:** “We want a government-wide way to manage who is allowed to act for a company, citizen or institution.”

**Do not say:** “The native Altinn Access Management service is already deployed here.” It is **simulated** in Window B.

## Part 3: Prove that actual Altinn code is involved (3 minutes)

Open Window A. Explain that the **native Altinn app** is not merely a mockup: it contains the official .NET app runtime, Altinn UI, BPMN process and XACML access policy. It is launched through **`studioctl`** with LocalTest API emulators, not national production microservices.

Log in using a LocalTest test identity (not Asha's Keycloak account). Show the licence form and fictional prefill. A native instantiation hook can call the protected **mock DoTM registry** when combined mode is enabled.

Submit synthetic data if the LocalTest UI allows completion in the meeting environment. **The automated pipeline currently verifies native startup and bridge endpoints; it does not verify the full browser form-to-callback journey.** If the submission cannot be completed, demonstrate the local test evidence rather than asserting that the callback fired.

The native BPMN hook *can* post an event to the simulator mock inbox when a data task ends. This is a **narrow synthetic bridge**, not verified person-to-person delivery or a real Nagarik notification API.

## Part 4: Show ecosystem and decision (2 minutes)

In Window B, select **Ecosystem map**. Explain each layer in plain language:

- Nagarik **mobile** today; possible government **web** channel later.
- Approved Nepal digital identity would be required for real authentication.
- Altinn-based shared service processing and rights could be evaluated.
- DoTM, civil and company registers remain the authoritative data owners.
- Citizens could receive results through channels authorized by government.

Conclude with a narrow request: one willing agency, one low-risk administrative process, a technical contact, test data, and permission to agree on identity and API contracts. Measure results before considering scale.

## Likely questions and direct answers

**“Why not just expand Nagarik App?”** — Nagarik App can remain the mobile front door and may expand to web. The issue to test is whether agencies benefit from common back-end services and authorization rather than separate custom processes.

**“Do we get BankID?”** — No. BankID is an external Norwegian identity provider. Nepal would need a legally accepted Nepal identity solution and configured federation.

**“Is this the complete Altinn Platform?”** — No. The native Altinn App is real, but LocalTest emulates shared infrastructure. Full production services require independent deployment and integration work.

**“Are the agency records real?”** — No. Every licence, ID, company and case in this showcase is fictional.

**“Can citizens use it today?”** — Not for any real government purpose. It is a demonstrator for design and evaluation.

After the meeting use `./demo down` to stop all runtime containers while preserving sample records. `./demo clean --yes` additionally removes the simulator data. See [Docker operations](DOCKER.md).

## Presenter safety checklist

Before a meeting, confirm both screens load, test accounts work, no real personal data is visible, the browser zoom fits the projector, and the [latest GitHub Actions](../.github/workflows/) are green. Use [component status](ALTINN_COMPONENT_STATUS.md) as the reference if a technical question goes beyond the demo.
