#!/bin/bash
# ============================================================
# bot_gate.sh — Liga/desliga o 'bot' de disparo de ofertas.
#
# Usa uma flag em arquivo (.bot_on). Quando a flag existe, os
# disparos (rotina_ofertas.sh, disparo_campanha_ofertas.py)
# podem rodar; sem a flag, eles são bloqueados.
#
# Uso:
#   bot_gate.sh on    # liga o bot (cria a flag)
#   bot_gate.sh off   # desliga o bot (remove a flag)
#   bot_gate.sh       # mostra o estado atual (ON/OFF)
# ============================================================
set -u

BASE="/root/cleudocode"
FLAG="$BASE/.bot_on"
LOG="$BASE/logs/bot_gate.log"
mkdir -p "$BASE/logs"

case "${1:-}" in
  on)
    echo "ON $(date '+%Y-%m-%d %H:%M:%S')" > "$FLAG"
    echo "$(date '+%Y-%m-%d %H:%M:%S') · BOT ON" >> "$LOG"
    echo "🔵 Bot ligado (disparos liberados)"
    ;;
  off)
    rm -f "$FLAG"
    echo "$(date '+%Y-%m-%d %H:%M:%S') · BOT OFF" >> "$LOG"
    echo "⚪ Bot desligado (disparos bloqueados)"
    ;;
  *)
    if [ -f "$FLAG" ]; then
      echo "ON"
    else
      echo "OFF"
    fi
    ;;
esac