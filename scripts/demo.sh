#!/usr/bin/env bash
# The official Altinn app + its LocalTest dependencies all run as containers.
# studioctl is the host-side control CLI; Docker Compose manages the Nepal UI.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/native-altinn/nepal-licence"
ENV_FILE="$ROOT/.demo.local.env"
PROJECT="altinn-nepal"
FEDERATION_PROJECT="altinn-federation"
APP_CONTAINER="localtest-app-nepal-licence"
NETWORK="${PROJECT}_default"

usage() {
  cat <<'MSG'
Nepal × Altinn demo — all runtime services in Docker

  ./demo up             Build and start all containers
  ./demo down           Stop all demo containers (keep data volumes)
  ./demo status         Show agency containers, gateways and LocalTest status
  ./demo logs           Show simulator and native Altinn logs
  ./demo clean --yes    Stop and remove ALL synthetic state volumes
  ./demo help           Show this help

Requires Docker Compose v2 + official studioctl preview CLI on the host.
Does NOT require .NET SDK or Python installed on the host.
The native Altinn app runs with studioctl --mode container.

Native Altinn: http://local.altinn.cloud:8000/ttd/nepal-licence/
Nepal visual portal: http://localhost:8085
Keycloak demo login: http://localhost:8081
MSG
}

require_runtime() {
  command -v docker >/dev/null || { echo >&2 "Docker is missing"; exit 2; }
  docker info >/dev/null 2>&1 || { echo >&2 "Docker daemon is unavailable. Start Docker Desktop/Engine."; exit 2; }
  docker compose version >/dev/null 2>&1 || { echo >&2 "Docker Compose v2 is required"; exit 2; }
  command -v studioctl >/dev/null || {
    echo >&2 "Official studioctl CLI missing."
    echo >&2 "Install: https://docs.altinn.studio/en/altinn-studio/v8/guides/development/local-dev/"
    exit 2
  }
}

ensure_state() {
  if [[ ! -f "$ENV_FILE" ]]; then
    local token
    token="$(od -An -N 32 -tx1 /dev/urandom | tr -d ' \n')"
    [[ "${#token}" -eq 64 ]] || { echo >&2 "Unable to create local demo token"; exit 1; }
    (umask 077; printf "PORTAL_PORT=8085\nPORTAL_BASE_URL=http://localhost:8085\nNATIVE_WEBHOOK_TOKEN=%s\n" "$token" > "$ENV_FILE")
  fi
  # This file is generated locally (chmod 600) and never checked into Git.
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
}

compose() {
  if [[ -f "$ENV_FILE" ]]; then
    docker compose --project-name "$PROJECT" --env-file "$ENV_FILE" "$@"
  else
    PORTAL_PORT=8085 PORTAL_BASE_URL=http://localhost:8085 docker compose --project-name "$PROJECT" "$@"
  fi
}

federation() {
  # The independent agency / integration Compose stack only joins the
  # externally named presentation network; records live in PRIVATE networks.
  if [[ -f "$ENV_FILE" ]]; then
    docker compose --project-name "$FEDERATION_PROJECT" \
      --env-file "$ENV_FILE" --file "$ROOT/infra/federation/compose.yml" "$@"
  else
    # Federation requires the ephemeral demo token and must not run with one
    # of the hard-coded development credentials for the Native Altinn bridge.
    echo >&2 "Federation environment missing: run ./demo up"
    return 2
  fi
}

ensure_native_connection() {
  docker container inspect "$APP_CONTAINER" >/dev/null 2>&1 || {
    echo >&2 "Could not find native Altinn app container '$APP_CONTAINER'"; exit 1;
  }
  docker network inspect "$NETWORK" >/dev/null 2>&1 || {
    echo >&2 "Could not find Nepal simulator network '$NETWORK'"; exit 1;
  }
  if ! docker inspect --format '{{json .NetworkSettings.Networks}}' "$APP_CONTAINER" | grep -Fq "\"$NETWORK\""; then
    docker network connect "$NETWORK" "$APP_CONTAINER"
  fi
  # The real Altinn app container and the mock portal now share a Docker-only
  # network. 'portal' is resolvable as a service name on that network.
  local tmp
  tmp="$(mktemp)"
  (umask 077; printf '{"Token":"%s","DotmUrl":"http://exchange-broker:8000/v1/native/dotm","NagarikUrl":"http://exchange-broker:8000/v1/native/events"}\n' "$NATIVE_WEBHOOK_TOKEN" > "$tmp")
  if ! docker cp "$tmp" "$APP_CONTAINER:/tmp/altinn-nepal-bridge.json"; then
    rm -f "$tmp"
    echo >&2 "Unable to inject synthetic bridge configuration"; exit 1
  fi
  rm -f "$tmp"
  docker exec --user root "$APP_CONTAINER" chown 1000:3000 /tmp/altinn-nepal-bridge.json
  docker exec --user root "$APP_CONTAINER" chmod 600 /tmp/altinn-nepal-bridge.json
}

up() {
  require_runtime
  ensure_state
  cd "$ROOT"
  echo "Starting Nepal presentation portal and Keycloak in Docker..."
  compose up --build -d
  echo "Building one reusable agency exchange image for all seven isolated roles..."
  docker build --tag altinn-nepal/federation:local "$ROOT/federation"
  echo "Starting three independently networked fictional agency registries and OAuth-protected exchange..."
  federation up -d
  echo "Starting official Altinn LocalTest platform containers..."
  (cd "$APP" && studioctl env up)
  echo "Building and running the genuine Altinn application as a container..."
  (cd "$APP" && studioctl run --mode container --detach)
  echo "Connecting the native Altinn container to synthetic Nepal registry/inbox endpoints..."
  ensure_native_connection
  # Attaching a secondary Docker network can briefly interrupt LocalTest's
  # app proxy. If curl is installed, wait until its public route recovers.
  if command -v curl >/dev/null 2>&1; then
    local status="000"
    for ((tries=1; tries<=25; tries++)); do
      status="$(curl --silent --output /dev/null --write-out '%{http_code}' --header 'Host: local.altinn.cloud' http://127.0.0.1:8000/ttd/nepal-licence/ || true)"
      if [[ "$status" =~ ^(200|301|302|303|307|308)$ ]]; then
        break
      fi
      sleep 2
    done
    if [[ ! "$status" =~ ^(200|301|302|303|307|308)$ ]]; then
      echo >&2 "Note: Altinn returned HTTP $status; inspect ./demo logs if the browser route remains unavailable."
    fi
  fi
  cat <<'MSG'

All demo runtime services are containerized.
  Native Altinn:  http://local.altinn.cloud:8000/ttd/nepal-licence/
  Nepal portal:   http://localhost:8085
  Agency exchange dashboard: http://localhost:8090
  Keycloak:       http://localhost:8081

Three agency private networks and a separate exchange network now isolate the
fictional transport, civil and company registries. Gateways validate signed
OAuth machine tokens issued by local Keycloak. Native Altinn connects ONLY
to the exchange bridge, which calls agency APIs.

LocalTest still emulates Altinn's national shared services; none of the mock
agency records, ID providers or Nagarik UI are real government connections.

Stop: ./demo down
Erase simulator data: ./demo clean --yes
MSG
}

down() {
  cd "$ROOT"
  # The Altinn App is also attached to the portal's Compose network in
  # combined mode; remove it BEFORE asking Compose to remove that network.
  if command -v studioctl >/dev/null; then
    (cd "$APP" && { studioctl stop || true; studioctl env down || true; })
  else
    echo >&2 "studioctl unavailable: LocalTest-managed containers may remain running."
  fi
  if command -v docker >/dev/null && docker compose version >/dev/null 2>&1; then
    if [[ -f "$ENV_FILE" ]]; then
      federation down --remove-orphans || true
    fi
    compose down --remove-orphans || true
  fi
  rm -f "$ENV_FILE"
  echo "Stopped Nepal simulator and Altinn LocalTest containers; data volumes retained."
}

status() {
  cd "$ROOT"
  compose ps
  if [[ -f "$ENV_FILE" ]]; then federation ps; fi
  if command -v studioctl >/dev/null; then
    (cd "$APP" && studioctl env status) || true
  fi
  docker ps --filter "name=$APP_CONTAINER" --format 'Native app: {{.Names}} {{.Status}}'
}

logs() {
  cd "$ROOT"
  compose logs --tail 60 portal identity || true
  if [[ -f "$ENV_FILE" ]]; then federation logs --tail 60 exchange-broker transport-edge civil-edge company-edge || true; fi
  if command -v studioctl >/dev/null; then
    (cd "$APP" && studioctl app logs) || true
  fi
}

clean() {
  if [[ "${1:-}" != "--yes" ]]; then
    echo >&2 "Destructive action: removes simulator, exchange audit, and all synthetic agency record volumes."
    echo >&2 "Confirm with: ./demo clean --yes"
    exit 2
  fi
  # Remove named volumes from BOTH of our synthetic Compose projects.
  # This must work even after ./demo down removed the ephemeral secret file.
  # The placeholder is passed ONLY to docker compose for variable expansion.
  cd "$ROOT"
  if command -v studioctl >/dev/null; then
    (cd "$APP" && { studioctl stop || true; studioctl env down || true; })
  fi
  if [[ -f "$ENV_FILE" ]]; then
    federation down --volumes --remove-orphans
  else
    NATIVE_WEBHOOK_TOKEN=cleanup-not-a-credential docker compose \
      --project-name "$FEDERATION_PROJECT" \
      --file "$ROOT/infra/federation/compose.yml" \
      down --volumes --remove-orphans
  fi
  compose down --volumes --remove-orphans
  rm -f "$ENV_FILE"
  echo "Removed simulated portal, separate agency-registry and broker audit volumes."
  echo "Altinn LocalTest data remains owned by studioctl; review its reset tools separately."
}

case "${1:-help}" in
  up) up ;;
  down) down ;;
  status) status ;;
  logs) logs ;;
  clean) clean "${2:-}" ;;
  help|-h|--help) usage ;;
  *) usage; exit 2 ;;
esac
