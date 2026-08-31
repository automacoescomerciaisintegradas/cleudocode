#!/bin/bash
# Rotina automática: sorteia produto + template, gera card e envia p/ WhatsApp + Telegram.
# Usa --skip-grok (rápido, sem limite do Grok) e varia o template a cada execução.
set -e
cd /root/cleudocode

if [ -f .env ]; then export $(grep -vE '^#|^$' .env | xargs); fi

# Respeita a flag do bot (bot_gate.sh on/off): só dispara com o bot ligado,
# conforme as janelas de disparo agendadas no cron.
if [ ! -f .bot_on ]; then
  echo "$(date '+%F %T') · rotina bloqueada (bot OFF)" >> logs/gerador_ofertas.log
  exit 0
fi

# sorteia um template dos disponíveis
mapfile -t TEMPLATES < <(ls templates/card_*.html | xargs -n1 basename)
TEMPLATE=${TEMPLATES[$((RANDOM % ${#TEMPLATES[@]}))]}
echo "$(date '+%F %T') · template sorteado: $TEMPLATE" >> logs/gerador_ofertas.log

./venv/bin/python3 gerador_ofertas_imagem.py \
  --template "$TEMPLATE" \
  --skip-grok \
  >> logs/gerador_ofertas.log 2>&1