#!/usr/bin/env bash
# The official Altinn app + its LocalTest dependencies all run as containers.
# studioctl is the host-side control CLI; Docker Compose manages the Nepal UI.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/native-altinn/nepal-licence"
ENV_FILE="$ROOT/.demo.local.env"
PROJECT="altinn-nepal"
APP_CONTAINER="localtest-app-nepal-licence"
NETWORK="${PROJECT}_default"

usage() {
  cat <<'MSG'
Nepal × Altinn demo — all runtime services in Docker

  ./demo up             Build and start all containers
  ./demo down           Stop all demo containers (keep data volumes)
  ./demo status         Show running containers and LocalTest status
  ./demo logs           Show simulator and native Altinn logs
  ./demo clean --yes    Stop and remove simulator data volume
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
  (umask 077; printf '{"Token":"%s","DotmUrl":"http://portal:8000/api/stubs/dotm/licence","NagarikUrl":"http://portal:8000/api/integrations/native-altinn/events"}\n' "$NATIVE_WEBHOOK_TOKEN" > "$tmp")
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
  Keycloak:       http://localhost:8081

Identity systems are separate. LocalTest emulates shared Altinn national
services. Government APIs, Nagarik mobile app and national identity are
NOT connected. Test users and records are synthetic.

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
    compose down --remove-orphans || true
  fi
  rm -f "$ENV_FILE"
  echo "Stopped Nepal simulator and Altinn LocalTest containers; data volumes retained."
}

status() {
  cd "$ROOT"
  compose ps
  if command -v studioctl >/dev/null; then
    (cd "$APP" && studioctl env status) || true
  fi
  docker ps --filter "name=$APP_CONTAINER" --format 'Native app: {{.Names}} {{.Status}}'
}

logs() {
  cd "$ROOT"
  compose logs --tail 60 portal identity || true
  if command -v studioctl >/dev/null; then
    (cd "$APP" && studioctl app logs) || true
  fi
}

clean() {
  if [[ "${1:-}" != "--yes" ]]; then
    echo >&2 "Destructive action: removes only the Nepal simulator's persisted Docker volume."
    echo >&2 "Confirm with: ./demo clean --yes"
    exit 2
  fi
  down
  cd "$ROOT"
  compose down --volumes --remove-orphans
  echo "Nepal simulator volume deleted. Official LocalTest's separately managed data may remain."
  echo "To reset LocalTest too, consult: studioctl env reset --help"
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
