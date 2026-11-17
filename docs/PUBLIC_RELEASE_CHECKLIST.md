# Checklist before making the repository public

**Status: release preparation; not approved for publication.**

This is a maintainer checklist. A passing build does not replace source, history or license review.

## Must complete

- [ ] **Choose a project license and add its full text.** Confirm the project's original contributors can grant it. Retain the upstream Altinn Studio template license and any required notices; confirm third-party assets and dependencies separately.
- [ ] **Review the entire Git history**, including deleted files, for secrets, keys, private credentials, personal data, confidential government correspondence and third-party material. Scanning the current working tree alone is not sufficient.
- [ ] Run secret scanning (for example, Gitleaks or GitHub secret scanning) against all refs. Treat current example passwords as **public demo-only values**, never as secure defaults.
- [ ] If a real secret was ever committed, revoke or rotate it before publication. Rewriting history alone does not make the secret safe.
- [ ] Review sample datasets, Keycloak users, files and screenshots to confirm that every identity and record is synthetic and publication is authorized.
- [ ] Confirm the native Altinn template's version and preserved attribution; record exact upstream source revision if available.
- [ ] Review external hyperlinks, vendor/product references and government programme claims with the project stakeholders.
- [ ] Enable private vulnerability reporting and confirm a contact route.
- [ ] Verify the chosen GitHub visibility, issue and Actions permissions, branch protection and repository owner settings.

## Technical checks

- [ ] Check all current GitHub Actions workflows on the intended release commit.
- [ ] Rehearse `./demo up`, the government walkthrough and `./demo down` on a clean machine.
- [ ] Run a native Altinn browser submission through the configured BPMN process and verify the resulting test event. Until automated, keep this limitation visible.
- [ ] Confirm that the local federation services are not unintentionally reachable from public interfaces.
- [ ] Recheck Docker images and dependency versions for known vulnerabilities.
- [ ] Validate that private keys, temporary certificates, local SQLite databases and `.env` files are excluded from commits.
- [ ] Ensure that all use of local tokens and HMAC checks is identified as demonstration-only.

## Editorial and stakeholder review

- [ ] Have a Nepali government-domain reviewer assess the English and Nepali briefs.
- [ ] Have an Altinn engineer verify descriptions of genuine Altinn components and LocalTest limitations.
- [ ] Confirm the demonstration reflects what is actually running, not merely a proposed architecture.
- [ ] Clearly state that this is an independent project without endorsement or live government connections.
- [ ] Record ownership, maintenance expectations and the process for external contributions.

## Release decision

A maintainer should approve publication only after reviewing the completed checklist. **Do not switch the repository to public solely because CI is green.**
