# 12-minute live walkthrough for Nepal government

**Two windows, clearly labelled**: Window A is genuine Altinn App running with
LocalTest service emulators. Window B is the standalone Nepal ecosystem simulator.

## Window A: Actual Altinn software (6 minutes)

1. Start locally with `bash scripts/start-native.sh`; open
   `http://local.altinn.cloud:8000`.
2. Log in as a **LocalTest** test user. Explain that this is a stand-in for a
   future Nepal-issued government identity; not BankID and not Nagarik SSO.
3. Open `ttd/nepal-licence` through LocalTest and show native Altinn frontend.
4. Show the licence reference prefilled through `IInstantiationProcessor`,
   from the **synthetic** DoTM adapter in `App/logic/NepalRegistryPrefill.cs`.
5. Enter a fabricated corrected address and explanation and submit the
   application. Altinn's own app runtime processes the BPMN steps, and LocalTest
   emulates the Storage/Auth/Authorization APIs.
6. Open `App/config/process/process.bpmn` and
   `App/config/authorization/policy.xml` if technical staff want evidence.

**Demonstrated:** genuine native app runtime/form/BPMN/policy, LocalTest contracts,
custom prefill extension. **Not demonstrated:** Nepal eID, native production
Storage/Auth/Authorization services, national delegation, real officer approval.

## Window B: Nepal multi-agency scenario (6 minutes)

1. Run `docker compose up --build -d`; open `http://localhost:8000`.
2. Use `asha / Demo123!`, submit a synthetic licence correction.
3. Switch to `maya / Demo123!` and record an approval in the **simulated**
   agency workflow.
4. Switch back to `asha`; inspect the simulated Nagarik inbox.
5. Switch to `raj`, delegate transport-permit access to `priya`.
6. Switch to `priya`, submit, revoke from `raj`, then verify denied access.
7. Switch to `kiran` for cross-system activity and audit visualization.
8. Select the **Native Altinn** tab in the simulator for the real app link.

**Demonstrated:** intended service journey and tested sandbox enforcement.
**Not demonstrated:** native Altinn delegation, actual Nepal systems, API
interoperability between this simulator and the native app.

## Decision request

Ask for one participating agency, a non-sensitive pilot workflow, a technical
focal person, identity-provider sandbox access and written API contracts. Then
build the genuinely integrated version and independently verify its permissions,
data protection, availability and operational costs.

## Official references

- https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/
- https://docs.altinn.studio/en/technology/architecture/altinn-landscape/
- https://docs.altinn.studio/en/authorization/reference/system/development-architecture/
