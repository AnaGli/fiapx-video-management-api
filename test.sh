#!/usr/bin/env bash

set -euo pipefail

# ==================================================
# CONFIGURAÇÃO
# ==================================================

BASE_URL="http://a445fd18510e04d0e81ee7306254d0a7-428545198.us-east-1.elb.amazonaws.com"

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc3OTgxNDQ3Nn0.YGPDca8OUFOLdPvJZa_xXwZcPTSFlkObGk-5BCQVfXs"

TOTAL_ORDERS=50

# ==================================================
# DELAYS
# ==================================================

# Teste rápido:
MIN_DELAY=10
MAX_DELAY=30

# Produção realista:
# MIN_DELAY=30
# MAX_DELAY=180

# ==================================================
# PARALELISMO
# ==================================================

MAX_PARALLEL=3

# ==================================================
# DADOS FIXOS
# ==================================================

CLIENT_ID=2
VEHICLE_ID=2

# ==================================================
# FLUXO DE STATUS
# ==================================================

STATUSES=(
  "EM_DIAGNOSTICO"
  "AGUARDANDO_APROVACAO"
  "EM_EXECUCAO"
  "FINALIZADA"
  "ENTREGUE"
)

# ==================================================
# HEADERS
# ==================================================

AUTH_HEADER="Authorization: Bearer ${TOKEN}"

# ==================================================
# LOGGING
# ==================================================

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

# ==================================================
# RANDOM DELAY
# ==================================================

random_delay() {

  local delay

  delay=$((RANDOM % (MAX_DELAY - MIN_DELAY + 1) + MIN_DELAY))

  log "⏳ Waiting ${delay}s..."

  sleep "${delay}"
}

# ==================================================
# CREATE SERVICE ORDER
# ==================================================

create_service_order() {

  local response
  local order_id

  response=$(curl -sS \
    --connect-timeout 10 \
    --max-time 30 \
    -X POST \
    "${BASE_URL}/service-orders/" \
    -H "accept: application/json" \
    -H "${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    -d "{
      \"client_id\": ${CLIENT_ID},
      \"vehicle_id\": ${VEHICLE_ID}
    }")

  order_id=$(echo "${response}" | sed -n 's/.*"id":[[:space:]]*\([0-9]*\).*/\1/p' | head -1)

  if [[ -z "${order_id}" ]]; then
    log "❌ Failed to create service order"
    log "Response: ${response}"
    return 1
  fi

  echo "${order_id}"
}

# ==================================================
# UPDATE STATUS
# ==================================================

update_status() {

  local order_id="$1"
  local status="$2"

  local http_code

  http_code=$(curl -sS \
    --connect-timeout 10 \
    --max-time 30 \
    -o /dev/null \
    -w "%{http_code}" \
    -X PUT \
    "${BASE_URL}/service-orders/${order_id}/status" \
    -H "accept: application/json" \
    -H "${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    -d "{
      \"status\": \"${status}\"
    }")

  if [[ "${http_code}" != "200" ]]; then
    log "❌ Failed to update order ${order_id} -> ${status} (HTTP ${http_code})"
    return 1
  fi

  log "🔄 Order ${order_id} -> ${status}"
}

# ==================================================
# PROCESS ORDER
# ==================================================

process_order() {

  local index="$1"

  log "🚗 Starting workflow #${index}"

  local order_id

  order_id=$(create_service_order)

  log "✅ Created order ${order_id}"

  for status in "${STATUSES[@]}"; do

    random_delay

    update_status "${order_id}" "${status}"

  done

  log "🏁 Workflow completed for order ${order_id}"
}

# ==================================================
# MAIN
# ==================================================

main() {

  log "=================================================="
  log "SERVICE ORDER LOAD TEST"
  log "=================================================="

  log "Total orders: ${TOTAL_ORDERS}"
  log "Parallel workers: ${MAX_PARALLEL}"
  log "Delay range: ${MIN_DELAY}s - ${MAX_DELAY}s"

  local running=0

  for ((i=1; i<=TOTAL_ORDERS; i++)); do

    process_order "${i}" &

    ((running+=1))

    sleep 1

    if [[ "${running}" -ge "${MAX_PARALLEL}" ]]; then

      wait

      running=0
    fi

  done

  wait

  log "=================================================="
  log "TEST FINISHED"
  log "=================================================="
}

main