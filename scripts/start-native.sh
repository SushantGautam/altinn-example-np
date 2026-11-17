#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v studioctl >/dev/null; then
  echo >&2 "Install studioctl from https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/"
  exit 2
fi
cd "$ROOT/native-altinn/nepal-licence"
studioctl env up
studioctl run --mode container --detach
cat <<'MSG'
Genuine Altinn App container: http://local.altinn.cloud:8000/ttd/nepal-licence/
Shared Altinn platform services are official LocalTest emulators.
For the combined Nepal demo: ./demo up
To stop: cd native-altinn/nepal-licence && studioctl stop && studioctl env down
MSG
