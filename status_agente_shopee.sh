#!/bin/bash
# Script para verificar o status do Agente de Vendas Shopee

PID_FILE="/root/cleudocode/shopee_agent.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null; then
        echo "✅ Agente de Vendas Shopee está ATIVO (PID: $PID)"
        echo "📄 Útimas 10 linhas do log:"
        tail -n 10 /root/cleudocode/shopee_agent.log
    else
        echo "❌ Agente de Vendas Shopee NÃO está rodando (PID file encontrado, mas processo não existe)"
        echo "💡 Execute 'bash /root/cleudocode/iniciar_agente_shopee.sh' para iniciar"
    fi
else
    echo "❌ Agente de Vendas Shopee NÃO está rodando (PID file não encontrado)"
    echo "💡 Execute 'bash /root/cleudocode/iniciar_agente_shopee.sh' para iniciar"
fi