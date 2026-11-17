# Contributing

This repository is a reference implementation and technical discussion project. Contributions that make its behavior easier to verify, reproduce or understand are welcome.

## Before opening a pull request

1. Open an issue for changes that affect the architecture, service contracts or public-facing claims.
2. Keep the distinction between **native Altinn**, **official LocalTest emulators**, and **project-specific simulators** explicit.
3. Use synthetic records only. Do not commit personal data, access tokens, certificates, private keys, passwords for real services or organization-specific endpoints.
4. Update the relevant documentation when changing a service, port, API contract or demo behavior.
5. Add regression tests for changes to authentication, permissions, delegation or interagency communication.

## Local checks

Start with the instructions in [README.md](README.md) and [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md). The CI workflows under `.github/workflows/` cover the Python simulator, native Altinn build, local emulators, integration examples and Docker lifecycle.

Run the checks relevant to your change. In particular, verify that `./demo up` and `./demo down` work before proposing changes to the launcher or container configuration.

## Code review

Prefer focused pull requests with a clear description of behavior changed, how it was tested and known limitations. Avoid broad rewrites that obscure provenance or make it harder to review security-sensitive code.

Security issues should follow [SECURITY.md](SECURITY.md), not public issues.

## Scope and attribution

This project is not an official government integration. Do not imply sponsorship by Altinn, Digdir or Nepal government bodies. Keep upstream Altinn attribution intact; see [UPSTREAM.md](native-altinn/nepal-licence/UPSTREAM.md).

Project-wide licensing terms are still subject to maintainer review. Do not assume that upstream licenses automatically establish a license for all original files in this repository.
