#!/bin/bash
# =============================================================================
# Community Welcome Agent - Inicialização Rápida
# =============================================================================

cd "$(dirname "$0")"

echo "============================================================"
echo "  🤗 Community Welcome Agent - CleudoCode"
echo "  Acolhimento Inteligente para Comunidades de IA"
echo "============================================================"
echo ""

# Menu de opções
echo "Escolha uma opção:"
echo ""
echo "  [1] 🧪 Demonstração (Sem dependências)"
echo "  [2] 💻 Chat Interativo Local (Requer Ollama)"
echo "  [3] 📱 Bot Telegram (Requer token)"
echo "  [4] 📖 Ver documentação"
echo "  [5] ❌ Sair"
echo ""

read -p "Opção: " option

case $option in
    1)
        echo ""
        echo "🚀 Iniciando demonstração..."
        echo ""
        python3 welcome_agent_demo.py
        ;;
    2)
        echo ""
        echo "💻 Iniciando chat interativo local..."
        echo ""
        python3 welcome_agent_chat.py
        ;;
    3)
        echo ""
        # Verifica se tem token
        if grep -q "TELEGRAM_BOT_TOKEN=" .env 2>/dev/null; then
            echo "📱 Iniciando Bot Telegram..."
            echo ""
            pip3 install python-telegram-bot 2>/dev/null
            python3 telegram_welcome_bot.py
        else
            echo "❌ TELEGRAM_BOT_TOKEN não configurado!"
            echo ""
            echo "Para configurar:"
            echo "  1. Crie um bot no Telegram via @BotFather"
            echo "  2. Copie o token"
            echo "  3. Adicione ao .env:"
            echo "     TELEGRAM_BOT_TOKEN=seu_token_aqui"
            echo ""
        fi
        ;;
    4)
        echo ""
        echo "📖 Documentação:"
        echo ""
        echo "  - WELCOME_AGENT_SUMMARY.md (Resumo executivo)"
        echo "  - WELCOME_AGENT_GUIDE.md (Guia completo)"
        echo "  - agents/welcome_agent.md (Persona do agente)"
        echo ""
        read -p "Abrir resumo? (s/n): " open_doc
        if [ "$open_doc" = "s" ]; then
            cat WELCOME_AGENT_SUMMARY.md | less
        fi
        ;;
    5)
        echo ""
        echo "👋 Até logo!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac
