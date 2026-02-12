#!/bin/bash
# Script para iniciar o DANNET MASTER - Agente de Vendas Avançado da F.C.A. DE QUEIROZ (Automações Comerciais Integradas) 24/7

echo "🚀 Iniciando DANNET MASTER - Agente de Vendas Avançado da F.C.A. DE QUEIROZ (ACI)..."
echo "🤖 O DANNET MASTER responderá automaticamente às mensagens dos clientes no Telegram"
echo "📊 Com recursos avançados de menu interativo, geração de links de afiliado e IA"
echo "📞 Contato: +55 88 921567214"
echo "📅 $(date)"
echo "----------------------------------------"

# Iniciar o serviço em segundo plano
nohup python3 /root/cleudocode/shopee_telegram_agent.py > /root/cleudocode/dannet_master.log 2>&1 &

AGENT_PID=$!
echo $AGENT_PID > /root/cleudocode/dannet_master.pid

echo "✅ DANNET MASTER iniciado com PID: $AGENT_PID"
echo "📄 Log disponível em: /root/cleudocode/dannet_master.log"
echo ""
echo "💡 Para parar o DANNET MASTER, execute: pkill -f shopee_telegram_agent.py"
echo "   Ou: kill \$(cat /root/cleudocode/dannet_master.pid)"

echo ""
echo "🎉 Seu DANNET MASTER da F.C.A. DE QUEIROZ (Automações Comerciais Integradas) está ativo e funcionando 24/7!"
echo "   Empresa: F.C.A. DE QUEIROZ (Automações Comerciais Integradas ou ACI)"
echo "   CNPJ: 59.216.642/0001-75"
echo "   Endereço: Setor 1, Perímetro Irrigado Morada Nova, s/n, Morada Nova - CE"
echo "   Telefone: +55 88 921567214"
echo "   Ele responderá automaticamente às mensagens dos clientes no Telegram"
echo "   Com recursos avançados de:"
echo "   - Menu interativo com opções de navegação"
echo "   - Geração de links de afiliado Shopee"
echo "   - Criação de mensagens promocionais com IA"
echo "   - Conceito de Flywheel Effect (ciclo de crescimento)"
echo "   - Estudos de caso de empresas de sucesso"
echo "   - Recomendações inteligentes de produtos"
echo "   - Atendimento personalizado baseado em IA"