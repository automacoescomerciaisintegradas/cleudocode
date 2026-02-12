#!/bin/bash
# Script para iniciar o Agente de Vendas Shopee 24/7

echo "🚀 Iniciando Agente de Vendas Shopee 24/7..."
echo "🤖 O agente responderá automaticamente às mensagens dos clientes no Telegram"
echo "📅 $(date)"
echo "----------------------------------------"

# Iniciar o serviço em segundo plano
nohup python3 /root/cleudocode/shopee_telegram_agent.py > /root/cleudocode/shopee_agent.log 2>&1 &

AGENT_PID=$!
echo $AGENT_PID > /root/cleudocode/shopee_agent.pid

echo "✅ Agente iniciado com PID: $AGENT_PID"
echo "📄 Log disponível em: /root/cleudocode/shopee_agent.log"
echo ""
echo "💡 Para parar o agente, execute: pkill -f shopee_telegram_agent.py"
echo "   Ou: kill \$(cat /root/cleudocode/shopee_agent.pid)"

echo ""
echo "🎉 Seu agente de vendas Shopee está ativo e funcionando 24/7!"
echo "   Ele responderá automaticamente às mensagens dos clientes no Telegram"