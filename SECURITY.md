# Security policy

## Intended use

This is a local development and demonstration environment. It contains deliberate test credentials and synthetic identity, registry and certificate infrastructure. It has not been security-reviewed for Internet-facing or production operation.

Do not use real citizen records, company records, national identity numbers, government accounts or live API secrets. Keep the service ports bound to localhost. Do not reuse the demo passwords, HMAC secrets or local certificate authority in another environment.

## Reporting a vulnerability

Please report vulnerabilities privately to the repository maintainer using GitHub's **Report a vulnerability** feature under the repository's **Security** tab, if enabled. If private vulnerability reporting is not enabled, contact the maintainer privately through an established channel. Do not publish exploit details or credentials in a GitHub issue.

Useful reports include affected commit, steps to reproduce, expected and actual behavior, and the impact. Use fictional data and a local instance.

## Supported versions

No production release is supported. Security fixes are made on the main development branch as resources permit.

## Important limitations

- Keycloak is configured for development use, with known demo accounts.
- LocalTest identities are not a national identity federation.
- The simulated permission model is not production Altinn Access Management.
- The local interagency PKI, service secrets and network boundaries illustrate concepts, not an accredited government security design.
- The native callback is not a durable, guaranteed-delivery event system.
- There is no independently audited deployment, disaster recovery, identity assurance or national data-protection review.

See [component status](docs/ALTINN_COMPONENT_STATUS.md) and [architecture](docs/ARCHITECTURE.md) for the full scope.
