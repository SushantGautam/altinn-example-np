# Checklist before making the repository public

**Status: release preparation; not approved for publication.**

This is a maintainer checklist. A passing build does not replace source, history or license review.

## Must complete

- [x] Add a proposed MIT project license and preserve the Altinn Studio license in `THIRD_PARTY_NOTICES.md`.
- [ ] Confirm the original contributors have authority to license all original work, and review other third-party assets and package notices.
- [x] Inspect all 76 existing main-branch commit diffs for common private-key and service-token signatures (targeted manual/automated pattern check; no high-confidence match observed).
- [ ] **Run a dedicated full-history secret scan**, including deleted files and all refs; review any matches for credentials, confidential correspondence, personal data and third-party material. A pattern check on diffs is not sufficient.
- [ ] Run dedicated secret scanning (for example, `gitleaks git --repo-path . --log-opts=\"--all\"` with a recent Gitleaks release, or GitHub secret scanning) against all refs. Treat current example passwords as **public demo-only values**, never as secure defaults.
- [ ] If a real secret was ever committed, revoke or rotate it before publication. Rewriting history alone does not make the secret safe.
- [ ] Review sample datasets, Keycloak users, files and screenshots to confirm that every identity and record is synthetic and publication is authorized.
- [x] Confirm upstream Altinn Studio repository uses MIT licensing and preserve its complete notice.
- [ ] Record the exact upstream source revision used for the imported template, if available.
- [ ] Review external hyperlinks, vendor/product references and government programme claims with the project stakeholders.
- [ ] Enable private vulnerability reporting and confirm a contact route.
- [ ] Review commit author names and email addresses: publishing existing Git history exposes author metadata, including personally identifiable addresses.
- [ ] Verify the chosen GitHub visibility, issue and Actions permissions, branch protection and repository owner settings.

## Technical checks

- [ ] Check all current GitHub Actions workflows on the intended release commit.
- [ ] Rehearse `./demo up`, the government walkthrough and `./demo down` on a clean machine.
- [ ] Run a native Altinn browser submission through the configured BPMN process and verify the resulting test event. Until automated, keep this limitation visible.
- [ ] Confirm that the local federation services are not unintentionally reachable from public interfaces.
- [ ] Recheck Docker images and dependency versions for known vulnerabilities.
- [x] Add a tracked-file release hygiene check to CI for private keys, common tokens and generated credentials.
- [ ] Validate that private keys, temporary certificates, local SQLite databases and `.env` files are excluded from all refs and release archives.
- [ ] Ensure that all use of local tokens and HMAC checks is identified as demonstration-only.

## Editorial and stakeholder review

- [ ] Have a Nepali government-domain reviewer assess the English and Nepali briefs.
- [ ] Have an Altinn engineer verify descriptions of genuine Altinn components and LocalTest limitations.
- [ ] Confirm the demonstration reflects what is actually running, not merely a proposed architecture.
- [ ] Clearly state that this is an independent project without endorsement or live government connections.
- [ ] Record ownership, maintenance expectations and the process for external contributions.

## Release decision

A maintainer should approve publication only after reviewing the completed checklist. **Do not switch the repository to public solely because CI is green.**
