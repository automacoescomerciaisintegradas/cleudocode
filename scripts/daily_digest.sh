#!/usr/bin/env bash
# ============================================================
# Digest diário de status — envia ao grupo de alertas às 8h (America/Fortaleza)
# Cobertura: cleudocode-app, aci-suite (app/db/redis/rabbitmq/minio),
#            chatwoot (app/sidekiq/db/redis), aci-omnichannel (app/db),
#            evolution v2, n8n, aci-evolution, traefik, portainer, agents_postgres
# Uso: daily_digest.sh [--send]
#      Sem --send: imprime o resumo no stdout (para testar).
# Cron: horário com guarda de fuso (à prova de horário de verão europeu):
#       0 * * * * daily_digest.sh && só envia se em Fortaleza for 08h
# ============================================================
set -u

ENV_FILE="/root/cleudocode/.env"
LOG_FILE="/root/cleudocode/logs/monitor/daily-digest.log"
STATE_FILE="/root/cleudocode/logs/monitor/last_digest_date"
HOST_IP="185.190.143.17"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

# ---------- Flags (qualquer ordem): --send envia, --force ignora guardas ----------
SEND=0; FORCE=0
for arg in "$@"; do
    [ "$arg" = "--send" ] && SEND=1
    [ "$arg" = "--force" ] && FORCE=1
done

# ---------- Guarda de fuso: só roda às 08h de America/Fortaleza ----------
fh=$(TZ=America/Fortaleza date +%H)
if [ $FORCE -eq 0 ] && [ "$fh" != "08" ]; then
    exit 0
fi

# Só um digest por dia
today=$(TZ=America/Fortaleza date +%F)
if [ $FORCE -eq 0 ] && [ -f "$STATE_FILE" ] && [ "$(cat "$STATE_FILE")" = "$today" ]; then
    exit 0
fi
echo "$today" > "$STATE_FILE"

# ---------- Coleta ----------
send_telegram() {
    local token chat_id
    token=$(grep -E "^TELEGRAM_BOT_TOKEN=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
    chat_id=$(grep -E "^TELEGRAM_ALERT_CHAT_ID=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
    [ -z "$chat_id" ] && chat_id=$(grep -E "^TELEGRAM_CHAT_ID=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
    [ -z "$token" ] || [ -z "$chat_id" ] && { log "ERRO: token/chat_id ausentes"; return 1; }
    curl -s --max-time 20 -X POST "https://api.telegram.org/bot${token}/sendMessage" \
        -d chat_id="$chat_id" -d parse_mode="HTML" -d disable_web_page_preview="true" \
        --data-urlencode text="$1" > /dev/null 2>&1
}

# container_status <prefixo> -> "🟢 Up 4 days (healthy)" | "🔴 Exited (1)" | "⚪ ausente"
# Usa prefixo do nome: preferencia por container rodando (swarm task IDs mudam a cada restart)
container_status() {
    local name="$1"
    local st
    st=$(docker ps --filter "name=^${name}" --format "{{.Status}}" 2>/dev/null | head -1)
    if [ -z "$st" ]; then
        st=$(docker ps -a --filter "name=^${name}" --format "{{.Status}}" 2>/dev/null | head -1)
    fi
    if [ -z "$st" ]; then
        echo "⚪ ${name}: não encontrado"
    elif echo "$st" | grep -qE "^(Up [0-9]+ seconds|[0-9]+ seconds)" || echo "$st" | grep -q "^Up.*starting"; then
        echo "🟡 ${name}: ${st}"
    elif echo "$st" | grep -q "^Up"; then
        echo "🟢 ${name}: ${st}"
    else
        echo "🔴 ${name}: ${st}"
    fi
}

http_status() {
    # http_status <url> -> emoji + código
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 "$1" 2>/dev/null)
    if [ "$code" = "200" ]; then echo "🟢 ${code}"; else echo "🔴 ${code:-timeout}"; fi
}

# Serviços por nome de container
mapfile -t LINES < <(
    container_status "cleudocode-app"
    container_status "aci-suite_app"
    container_status "aci-suite_suite_db"
    container_status "aci-suite_redis"
    container_status "aci-suite_rabbitmq"
    container_status "aci-suite_minio"
    container_status "chatwoot_chatwoot_app"
    container_status "chatwoot_chatwoot_sidekiq"
    container_status "chatwoot_postgres"
    container_status "chatwoot_redis"
    container_status "aci-omnichannel_app"
    container_status "aci-omnichannel_postgres"
    container_status "evolution_v2_evolution_v2"
    container_status "aci-n8n"
    container_status "aci-evolution"
    container_status "aci_db_postgres"
    container_status "agents_postgres"
    container_status "pgvector_postgres"
    container_status "traefik"
    container_status "portainer_portainer"
)

SERVICE_LINES=$(printf '%s\n' "${LINES[@]}")

# Endpoints HTTP
CLEUDO_HTTP=$(http_status "http://localhost:8501/health")
SUITE_HTTP=$(http_status "http://localhost:3001/" )

# Recursos
DISK_PCT=$(df -h / | awk 'NR==2 {gsub(/%/,""); print $5}')
DISK_FREE=$(df -h / | awk 'NR==2 {print $4}')
MEM_PCT=$(free | awk '/^Mem:/ {printf "%.0f", $3/$2*100}')
LOAD=$(cut -d, -f1 /proc/loadavg)

# Containers com problemas (para linha de resumo)
# Containers com saída anormal (exclui Exited(0)/Created = historico de tasks antigas)
problems=$(docker ps -a --format "{{.Names}}|{{.Status}}" 2>/dev/null | grep -vE "\|(Up |Created|Exited \(0\))" | wc -l)

# ---------- Montagem ----------
SUMMARY="🟢 Tudo operacional"
if [ "$problems" -gt 0 ]; then
    SUMMARY="⚠️ ${problems} container(ns) com saída anormal (ex.: OOM/restart antigo)"
fi
if [ "$CLEUDO_HTTP" != "🟢 200" ]; then SUMMARY="🔴 Cleudocode FORA DO AR"; fi

MSG="📊 <b>DIGEST DIÁRIO — ${today}</b>
🖥️ $(hostname -s) (${HOST_IP})
${SUMMARY}

<b>🏁 Principais</b>
$(container_status cleudocode-app)
• HTTP health: ${CLEUDO_HTTP}
• aci-suite: app $(container_status aci-suite_app | cut -d' ' -f1) | db $(container_status aci-suite_suite_db | cut -d' ' -f1) | redis $(container_status aci-suite_redis | cut -d' ' -f1)
• chatwoot: app $(container_status chatwoot_chatwoot_app | cut -d' ' -f1) | db $(container_status chatwoot_postgres | cut -d' ' -f1)
• omnichannel: $(container_status aci-omnichannel_app | cut -d' ' -f1) | evolution: $(container_status evolution_v2_evolution_v2 | cut -d' ' -f1)
• n8n: $(container_status aci-n8n | cut -d' ' -f1) | traefik: $(container_status traefik | cut -d' ' -f1)

<b>🧩 Todos os serviços</b>
<pre>$(printf '%s\n' "${LINES[@]}" | sed 's/^/ /' | cut -c1-70)</pre>

<b>💻 Recursos</b>
• Disco: ${DISK_PCT}% usado (${DISK_FREE} livres)
• RAM: ${MEM_PCT}% | Load: ${LOAD}
• Uptime host: $(uptime -p | cut -c4-)

🕐 Gerado às $(TZ=America/Fortaleza date '+%H:%M') (Fortaleza)"

# ---------- Envio / stdout ----------
if [ $SEND -eq 1 ]; then
    send_telegram "$MSG"
    log "Digest enviado (${today})"
else
    echo "$MSG"
    echo
    echo "[dry-run] use --send para publicar no grupo"
fi
