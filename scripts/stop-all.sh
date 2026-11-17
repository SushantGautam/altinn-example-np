#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PORTAL_PORT=8085 PORTAL_BASE_URL=http://localhost:8085 docker compose down
if command -v studioctl >/dev/null 2>&1; then
  cd native-altinn/nepal-licence
  studioctl stop || true
  studioctl env down || true
fi
