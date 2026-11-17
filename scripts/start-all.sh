#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
echo "Starting native Altinn App / official LocalTest..."
bash scripts/start-native.sh
echo "Starting separate Nepal presentation portal on 8085..."
PORTAL_PORT=8085 PORTAL_BASE_URL=http://localhost:8085 docker compose up --build -d
cat <<'MSG'

LOCAL SHOWCASE
Actual Altinn App: http://local.altinn.cloud:8000/ttd/nepal-licence/
Nepal presentation simulator: http://localhost:8085
Local Keycloak login: http://localhost:8081

Note: the simulator and native Altinn App run side by side, not via a shared
identity or data integration. LocalTest shared services are emulated.

Stop: bash scripts/stop-all.sh
MSG
