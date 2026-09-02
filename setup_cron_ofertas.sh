#!/bin/bash
echo "Configurando CRON para o Disparo de Ofertas Automático..."

# Cria um arquivo temp para o cron
CRON_FILE="/tmp/crontab_shopee"
crontab -l > $CRON_FILE 2>/dev/null

# Remove a linha antiga se existir
sed -i '/disparo_campanha_ofertas.py/d' $CRON_FILE

# Disparo diário às 10:00 da manhã
echo "0 10 * * * /root/cleudocode/venv/bin/python /root/cleudocode/disparo_campanha_ofertas.py >> /root/cleudocode/logs/cron_ofertas.log 2>&1" >> $CRON_FILE

crontab $CRON_FILE
echo "✅ Cronjob instalado com sucesso."
echo "O script será executado todos os dias às 10:00 da manhã."
