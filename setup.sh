#!/bin/bash

# Script de Setup Automático para Cleudocode
# Autor: Automações Comerciais Integradas
# Versão: 1.0

set -e  # Sai se qualquer comando falhar

echo "==========================================="
echo "  CLEUDOCODE - Setup Automático"
echo "==========================================="

# Detecta o sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
}

# Verifica se o Python está instalado
check_python() {
    if command -v python3 &> /dev/null; then
        echo "✅ Python3 encontrado: $(python3 --version)"
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        echo "✅ Python encontrado: $(python --version)"
        PYTHON_CMD="python"
    else
        echo "❌ Python não encontrado!"
        if [[ "$OS" == "linux" ]]; then
            echo "Instalando Python3..."
            sudo apt update
            sudo apt install python3 python3-pip python3-venv -y
        elif [[ "$OS" == "macos" ]]; then
            echo "Instalando Python3 com Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            brew install python3
        fi
        PYTHON_CMD="python3"
    fi
}

# Verifica se o Git está instalado
check_git() {
    if ! command -v git &> /dev/null; then
        echo "❌ Git não encontrado!"
        if [[ "$OS" == "linux" ]]; then
            sudo apt install git -y
        elif [[ "$OS" == "macos" ]]; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            brew install git
        fi
    fi
    echo "✅ Git encontrado: $(git --version)"
}

# Verifica se o Docker está instalado (opcional)
check_docker() {
    if command -v docker &> /dev/null; then
        echo "✅ Docker encontrado: $(docker --version)"
        DOCKER_INSTALLED=true
    else
        echo "⚠️  Docker não encontrado (funcionalidade opcional)"
        DOCKER_INSTALLED=false
    fi
}

# Cria ambiente virtual
setup_venv() {
    echo "🔧 Criando ambiente virtual..."
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
    fi
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
}

# Instala dependências
install_deps() {
    echo "📦 Instalando dependências..."
    pip install --upgrade pip
    pip install flask flask-cors python-dotenv requests psutil pyyaml pypdf
    
    # Tenta instalar outros pacotes importantes
    pip install click colorama
    echo "✅ Dependências instaladas"
}

# Configura variáveis de ambiente
setup_env() {
    if [ ! -f ".env" ]; then
        echo "📝 Configurando arquivo .env..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo "✅ Arquivo .env criado a partir do .env.example"
        else
            echo "⚠️  Arquivo .env.example não encontrado, criando .env básico..."
            cat > .env << EOF
# Configuração Cleudocode Telegram Relay

# --- TELEGRAM ---
# Obtenha com o @BotFather no Telegram
TELEGRAM_BOT_TOKEN=
# Obtenha com o @userinfobot ou @IDBot
TELEGRAM_USER_ID=

# --- PERSONALIZAÇÃO ---
USER_NAME=Seu Nome
USER_TIMEZONE=America/Sao_Paulo

# --- TRANSCRIÇÃO DE VOZ E LLM ---
# "gemini" ou "local"
VOICE_PROVIDER=gemini
GEMINI_API_KEY=
# AIDEV-NOTE: Configurado para usar Gemini 2.0 Flash conforme pedido do usuário
LLM_MODEL=gemini-2.0-flash

# --- OLLAMA SERVER CONFIGURATION (opcional) ---
OLLAMA_HOST=http://localhost:11434
DEEPSEEK_MODEL=llama3:8b

# Gateway Token (usado para autenticação)
CLEUDOCODE_GATEWAY_TOKEN=cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce

# WhatsApp (Evolution API)
WHATSAPP_API_TOKEN_INSTANCE=

# Telegram
TELEGRAM_BOT_TOKEN_OLD=

# AI API Keys (opcional - para fallback)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GROQ_API_KEY=
EOF
        fi
        echo "⚠️  Configure seu .env com credenciais válidas!"
    fi
}

# Menu de opções
show_menu() {
    echo ""
    echo "🔧 O que você gostaria de fazer?"
    echo "1) Instalar e configurar ambiente básico"
    echo "2) Instalar e configurar com Docker (se disponível)"
    echo "3) Apenas ativar ambiente virtual"
    echo "4) Executar diagnóstico"
    echo "5) Sair"
    echo ""
    read -p "Escolha uma opção [1-5]: " choice
    
    case $choice in
        1)
            echo "🚀 Instalando ambiente básico..."
            check_python
            check_git
            setup_venv
            install_deps
            setup_env
            echo ""
            echo "🎉 Instalação básica concluída!"
            echo "💡 Para executar: source venv/bin/activate && python web_server.py"
            ;;
        2)
            echo "🐳 Instalando com Docker..."
            check_python
            check_git
            check_docker
            if [ "$DOCKER_INSTALLED" = true ]; then
                setup_venv
                install_deps
                setup_env
                echo ""
                echo "🔄 Construindo containers Docker..."
                docker compose up --build -d
                echo "🎉 Instalação com Docker concluída!"
                echo "💡 Containers em execução:"
                docker compose ps
            else
                echo "❌ Docker não está instalado. Execute opção 1 para instalação básica."
            fi
            ;;
        3)
            echo "🔌 Ativando ambiente virtual..."
            setup_venv
            echo "✅ Ambiente virtual ativado. Execute: source venv/bin/activate"
            ;;
        4)
            echo "🔍 Executando diagnóstico..."
            check_python
            check_git
            check_docker
            echo "📄 Verificando arquivos importantes..."
            if [ -f "web_server.py" ]; then
                echo "✅ web_server.py encontrado"
            else
                echo "❌ web_server.py NÃO encontrado"
            fi
            if [ -f "cli/main.py" ]; then
                echo "✅ cli/main.py encontrado"
            else
                echo "❌ cli/main.py NÃO encontrado"
            fi
            echo "🔧 Diagnóstico concluído!"
            ;;
        5)
            echo "👋 Até logo!"
            exit 0
            ;;
        *)
            echo "❌ Opção inválida!"
            show_menu
            ;;
    esac
}

# Função principal
main() {
    detect_os
    echo "💻 Sistema operacional detectado: $OS"
    echo ""
    
    show_menu
}

# Executa o script
main