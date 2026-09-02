#!/usr/bin/env bash
# ============================================================
# Monitor do Cleudocode — container + health HTTP
# - Alerta no Telegram quando o container cair ou o /health falhar
# - Auto-restart via docker compose (e alerta de recuperação)
# - Anti-spam: re-alerta no máximo a cada RE ALERT_MINUTES enquanto estiver caído
# Uso: monitor_cleudocode.sh [--test-alert] [--no-restart]
# Cron: */2 * * * * (instalado)
# ============================================================
set -u

COMPOSE_DIR="/root/cleudocode"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.cloud.yml"
CONTAINER="cleudocode-app"
HEALTH_URL="http://localhost:8501/health"
ENV_FILE="$COMPOSE_DIR/.env"
STATE_DIR="$COMPOSE_DIR/logs/monitor"
LOG_FILE="$COMPOSE_DIR/logs/monitor/cleudocode-monitor.log"
REALERT_MINUTES=10
CURL_TIMEOUT=10

TEST_ALERT=0
DO_RESTART=1
[ "${1:-}" = "--test-alert" ] && TEST_ALERT=1
[ "${1:-}" = "--no-restart" ] && DO_RESTART=0

mkdir -p "$STATE_DIR"
DOWN_SINCE_FILE="$STATE_DIR/down_since"
LAST_ALERT_FILE="$STATE_DIR/last_alert"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

send_telegram() {
    # $1 = mensagem (suporta HTML)
    # Envia para o grupo de alertas (TELEGRAM_ALERT_CHAT_ID); fallback: TELEGRAM_CHAT_ID
    local token chat_id
    token=$(grep -E "^TELEGRAM_BOT_TOKEN=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
    chat_id=$(grep -E "^TELEGRAM_ALERT_CHAT_ID=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
    [ -z "$chat_id" ] && chat_id=$(grep -E "^TELEGRAM_CHAT_ID=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
    [ -z "$token" ] || [ -z "$chat_id" ] && { log "ERRO: token/chat_id ausentes no .env"; return 1; }

    curl -s --max-time 15 -X POST "https://api.telegram.org/bot${token}/sendMessage" \
        -d chat_id="$chat_id" \
        -d parse_mode="HTML" \
        -d disable_web_page_preview="true" \
        --data-urlencode text="$1" > /dev/null 2>&1
}

alert_down() {
    local reason="$1"
    local now=$(date +%s)
    local last_alert=0
    [ -f "$LAST_ALERT_FILE" ] && last_alert=$(cat "$LAST_ALERT_FILE" 2>/dev/null || echo 0)

    # Anti-spam: só re-alerta após REALERT_MINUTES
    if [ $((now - last_alert)) -lt $((REALERT_MINUTES * 60)) ]; then
        return 0
    fi
    echo "$now" > "$LAST_ALERT_FILE"

    local down_since=$(cat "$DOWN_SINCE_FILE" 2>/dev/null || echo "$now")
    local mins=$(( (now - down_since) / 60 ))
    local msg="🚨 <b>CLEUDOCODE FORA DO AR</b>
⏰ $(date '+%d/%m %H:%M:%S')
📍 Host: $(hostname -s) (185.190.143.17)
💬 Motivo: <code>${reason}</code>
⏱️ Caído há: ~${mins} min
🔧 Ação: $( [ $DO_RESTART -eq 1 ] && echo 'auto-restart disparado' || echo 'restart manual necessário')"

    send_telegram "$msg"
    log "ALERTA ENVIADO: $reason"
}

alert_recovery() {
    local downtime_mins="$1"
    local msg="✅ <b>CLEUDOCODE NOVAMENTE ONLINE</b>
⏰ $(date '+%d/%m %H:%M:%S')
⏱️ Indisponibilidade: ~${downtime_mins} min
✔️ Health check respondendo normalmente"
    send_telegram "$msg"
    log "RECUPERAÇÃO — downtime ~${downtime_mins}min"
}

# ---------- Modo teste ----------
if [ $TEST_ALERT -eq 1 ]; then
    send_telegram "🧪 <b>Teste do monitor Cleudocode</b>
⏰ $(date '+%d/%m %H:%M:%S')
Se você recebeu esta mensagem, os alertas estão funcionando."
    log "TESTE de alerta enviado"
    exit 0
fi

# ---------- Checagens ----------
reason=""

# 1) Container em execução?
container_running=$(docker ps --filter "name=^/${CONTAINER}$" --filter "status=running" -q 2>/dev/null)
if [ -z "$container_running" ]; then
    reason="container não está running"
fi

# 2) Health endpoint responde OK?
if [ -z "$reason" ]; then
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $CURL_TIMEOUT --retry 1 "$HEALTH_URL" 2>/dev/null)
    if [ "$http_code" != "200" ]; then
        reason="health check falhou (HTTP ${http_code:-sem resposta})"
    fi
fi

now=$(date +%s)

# ---------- Caiu ----------
if [ -n "$reason" ]; then
    if [ ! -f "$DOWN_SINCE_FILE" ]; then
        echo "$now" > "$DOWN_SINCE_FILE"
        log "FALHA detectada: $reason"
    fi
    alert_down "$reason"

    if [ $DO_RESTART -eq 1 ]; then
        log "Auto-restart: docker compose up -d $CONTAINER"
        (cd "$COMPOSE_DIR" && docker compose -f "$COMPOSE_FILE" up -d "$CONTAINER" >> "$LOG_FILE" 2>&1)
    fi
    exit 1
fi

# ---------- Saudável ----------
if [ -f "$DOWN_SINCE_FILE" ]; then
    down_since=$(cat "$DOWN_SINCE_FILE")
    alert_recovery $(( (now - down_since) / 60 ))
    rm -f "$DOWN_SINCE_FILE" "$LAST_ALERT_FILE"
fi
exit 0
