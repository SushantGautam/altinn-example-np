#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$HERE/native-altinn/nepal-licence"

if ! command -v studioctl >/dev/null 2>&1; then
  echo >&2 "studioctl is missing."
  echo >&2 "Install from the official instructions: https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/"
  exit 2
fi
if ! command -v dotnet >/dev/null 2>&1; then
  echo >&2 ".NET 10 SDK is required to run the native Altinn App."
  exit 2
fi
cd "$APP"
echo "Checking prerequisites for native Altinn Studio application..."
studioctl doctor
echo "Starting Altinn LocalTest platform (emulated auth/storage/authorization services)..."
studioctl env up
echo "Starting the genuine Altinn application runtime..."
studioctl run --detach
cat <<'MSG'

Native Altinn application:
  http://local.altinn.cloud:8000
  Log in with LocalTest test users, not the NepalID sandbox users.

Status:
  Altinn App (.NET + BPMN + data model + XACML): REAL
  Shared Storage/Auth/Authorization in LocalTest: EMULATED
  Nepal National ID / Nagarik / Registry: NOT CONNECTED

Stop:
  cd native-altinn/nepal-licence && studioctl stop && studioctl env down
MSG
