#!/bin/bash
# =============================================================================
# CleudoCode Welcome Agent - Deploy Automático em Produção
# =============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funções de log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[ATENÇÃO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# =============================================================================
# VERIFICAÇÕES PRELIMINARES
# =============================================================================

echo "============================================================"
echo "  🚀 CleudoCode Welcome Agent - Deploy em Produção"
echo "============================================================"
echo ""

# Verificar se é root
if [ "$EUID" -ne 0 ]; then 
    log_error "Por favor, execute como root (sudo ./deploy_production.sh)"
    exit 1
fi

# Verificar sistema operacional
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
else
    OS="Unknown"
fi

log_info "Sistema operacional: $OS"

# =============================================================================
# INSTALAÇÃO DE DEPENDÊNCIAS
# =============================================================================

log_info "Verificando dependências..."

# Docker
if ! command -v docker &> /dev/null; then
    log_warn "Docker não encontrado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    log_success "Docker instalado!"
else
    log_success "Docker já instalado"
fi

# Docker Compose
if ! command -v docker compose &> /dev/null; then
    log_warn "Docker Compose não encontrado. Instalando..."
    apt-get update
    apt-get install -y docker-compose-plugin
    log_success "Docker Compose instalado!"
else
    log_success "Docker Compose já instalado"
fi

# Git
if ! command -v git &> /dev/null; then
    log_warn "Git não encontrado. Instalando..."
    apt-get update
    apt-get install -y git
    log_success "Git instalado!"
else
    log_success "Git já instalado"
fi

# =============================================================================
# CONFIGURAÇÃO DO AMBIENTE
# =============================================================================

echo ""
log_info "Configurando ambiente..."

# Verificar se está no diretório correto
if [ ! -f "telegram_welcome_bot.py" ]; then
    log_error "Por favor, execute este script no diretório /root/cleudocode"
    exit 1
fi

# Copiar .env se não existir
if [ ! -f ".env" ]; then
    log_info "Copiando .env.production para .env"
    cp .env.production .env
    log_success ".env criado!"
else
    log_warn ".env já existe. Pulando cópia."
fi

# =============================================================================
# CONFIGURAÇÃO DO TELEGRAM
# =============================================================================

echo ""
echo "============================================================"
echo "  📱 Configuração do Telegram Bot"
echo "============================================================"
echo ""

# Verificar se TOKEN está configurado
TELEGRAM_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" .env | cut -d '=' -f2)

if [ -z "$TELEGRAM_TOKEN" ] || [ "$TELEGRAM_TOKEN" == "seu_token_aqui" ]; then
    log_warn "TELEGRAM_BOT_TOKEN não configurado no .env"
    echo ""
    echo "Para obter o token do Telegram:"
    echo "  1. Abra @BotFather no Telegram"
    echo "  2. Envie /newbot"
    echo "  3. Siga as instruções"
    echo "  4. Copie o token"
    echo ""
    read -p "Cole o token do Telegram Bot aqui: " -s USER_TOKEN
    echo ""
    
    if [ -n "$USER_TOKEN" ]; then
        # Atualizar .env
        sed -i "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$USER_TOKEN|g" .env
        log_success "Token do Telegram configurado!"
    else
        log_warn "Token não fornecido. Você pode configurar manualmente depois."
    fi
else
    log_success "TELEGRAM_BOT_TOKEN já configurado"
fi

# =============================================================================
# CONFIGURAÇÃO DO OLLAMA
# =============================================================================

echo ""
echo "============================================================"
echo "  🤖 Configuração do Ollama"
echo "============================================================"
echo ""

# Verificar se Ollama está rodando
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    log_success "Ollama já está rodando"
else
    log_info "Ollama não está rodando. Iniciando..."
    
    # Verificar se Ollama está instalado
    if command -v ollama &> /dev/null; then
        # Iniciar como serviço
        nohup ollama serve > /var/log/ollama.log 2>&1 &
        sleep 5
        log_success "Ollama iniciado!"
    else
        log_warn "Ollama não está instalado. Vamos usar Docker..."
    fi
fi

# Baixar modelo
log_info "Verificando modelo llama3:8b..."
if curl -s http://localhost:11434/api/tags | grep -q "llama3:8b"; then
    log_success "Modelo llama3:8b já disponível"
else
    log_info "Baixando modelo llama3:8b (pode demorar alguns minutos)..."
    
    if command -v ollama &> /dev/null; then
        ollama pull llama3:8b
        log_success "Modelo baixado!"
    else
        log_warn "Ollama não disponível via Docker. O modelo será baixado no primeiro uso."
    fi
fi

# =============================================================================
# DEPLOY COM DOCKER
# =============================================================================

echo ""
echo "============================================================"
echo "  🐳 Deploy com Docker Compose"
echo "============================================================"
echo ""

# Verificar se docker-compose.welcome.yml existe
if [ ! -f "docker-compose.welcome.yml" ]; then
    log_error "docker-compose.welcome.yml não encontrado!"
    exit 1
fi

log_info "Iniciando containers..."

# Build e start
docker compose -f docker-compose.welcome.yml up -d --build

if [ $? -eq 0 ]; then
    log_success "Deploy realizado com sucesso!"
else
    log_error "Falha no deploy. Verifique os logs."
    docker compose -f docker-compose.welcome.yml logs
    exit 1
fi

# =============================================================================
# VERIFICAÇÃO DE SAÚDE
# =============================================================================

echo ""
log_info "Aguardando inicialização dos serviços (30s)..."
sleep 30

echo ""
echo "============================================================"
echo "  🏥 Verificação de Saúde"
echo "============================================================"
echo ""

# Verificar containers
log_info "Status dos containers:"
docker compose -f docker-compose.welcome.yml ps

# Verificar gateway
echo ""
log_info "Testando Gateway..."
if curl -s http://localhost:18900/health > /dev/null 2>&1; then
    log_success "Gateway está online!"
    curl -s http://localhost:18900/health | python3 -m json.tool 2>/dev/null || true
else
    log_warn "Gateway pode estar indisponível. Verifique os logs."
fi

# Verificar Ollama
echo ""
log_info "Testando Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    log_success "Ollama está online!"
    curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Modelos disponíveis: {len(d[\"models\"])}')" 2>/dev/null || true
else
    log_warn "Ollama pode estar indisponível."
fi

# =============================================================================
# INSTRUÇÕES FINAIS
# =============================================================================

echo ""
echo "============================================================"
echo "  ✅ Deploy Concluído!"
echo "============================================================"
echo ""

log_success "Community Welcome Agent está em produção!"

echo ""
echo "📱 **Próximos Passos:**"
echo ""
echo "  1. Configure o bot no Telegram:"
echo "     - Abra @BotFather no Telegram"
echo "     - Configure os comandos:"
echo "       /setcommands"
echo "       cleudocode_welcome_bot"
echo "       start - Iniciar acolhimento"
echo "       help - Ajuda"
echo "       status - Ver status"
echo "       reset - Reiniciar conversa"
echo ""
echo "  2. Teste o bot:"
echo "     - Busque pelo seu bot no Telegram"
echo "     - Envie /start"
echo ""
echo "  3. Monitore os logs:"
echo "     docker compose -f docker-compose.welcome.yml logs -f"
echo ""

echo "🔗 **URLs de Acesso:**"
echo ""
echo "  - Gateway:    http://localhost:18900"
echo "  - Ollama:     http://localhost:11434"
echo "  - Health:     http://localhost:18900/health"
echo ""

echo "📚 **Documentação:**"
echo ""
echo "  - DEPLOY_PRODUCTION.md - Guia completo"
echo "  - WELCOME_AGENT_GUIDE.md - Guia do agente"
echo "  - WELCOME_AGENT_SUMMARY.md - Resumo"
echo ""

echo "🛠️ **Comandos Úteis:**"
echo ""
echo "  # Ver logs"
echo "  docker compose -f docker-compose.welcome.yml logs -f"
echo ""
echo "  # Reiniciar"
echo "  docker compose -f docker-compose.welcome.yml restart"
echo ""
echo "  # Parar"
echo "  docker compose -f docker-compose.welcome.yml down"
echo ""
echo "  # Atualizar"
echo "  git pull && docker compose -f docker-compose.welcome.yml up -d --build"
echo ""

echo "============================================================"
echo "  🎉 Bem-vindo à produção!"
echo "============================================================"
echo ""
