#!/bin/bash
# Script de Instalação do Cleudocodebot para EasyPanel
# Este script instala e configura o Cleudocodebot para execução na EasyPanel

set -e  # Sai com erro se qualquer comando falhar

echo "==========================================="
echo "INSTALAÇÃO DO CLEUDOCODEBOT PARA EASYPANEL"
echo "==========================================="

# Verificar se o usuário é root
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Este script não deve ser executado como root"
   echo "Execute como um usuário regular com sudo disponível"
   exit 1
fi

# Atualizar sistema
echo "Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências
echo "Instalando dependências..."
sudo apt install -y python3 python3-pip python3-venv git curl wget ffmpeg

# Instalar Docker se não estiver presente
if ! command -v docker &> /dev/null; then
    echo "Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "⚠️  Docker instalado. Faça logout e login novamente para que as permissões do Docker sejam aplicadas."
fi

# Instalar Docker Compose se não estiver presente
if ! command -v docker-compose &> /dev/null; then
    echo "Instalando Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Criar diretório do projeto
PROJECT_DIR="$HOME/cleudocodebot"
echo "Criando diretório do projeto em $PROJECT_DIR..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Clonar o repositório
echo "Clonando repositório do Cleudocodebot..."
git clone https://github.com/automacoescomerciaisintegradas/cleudocode.git .
git checkout main

# Criar ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Instalar o pacote localmente
pip install -e .

# Criar arquivo .env com configurações padrão
echo "Criando arquivo de configuração..."
cat > .env << EOF
# Configurações do Cleudocodebot para EasyPanel
OLLAMA_HOST=http://localhost:11434
DEEPSEEK_MODEL=qwen2.5-coder:7b
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=3000
STREAMLIT_SERVER_PORT=3001
STREAMLIT_SERVER_ADDRESS=0.0.0.0
CLEUDO_CODE_DAEMON_PORT=5001
CLEUDO_CODE_API_PORT=5001
CLEUDO_CODE_WEB_PORT=8501

# Chaves de segurança (ALTERE ESTAS CHAVES PARA VALORES ÚNICOS EM PRODUÇÃO)
FLASK_SECRET_KEY=$(openssl rand -hex 32)
SECURITY_SECRET_KEY=$(openssl rand -hex 32)

# Configurações do sistema
CURRENT_PROFILE=production
DEBUG=false
EOF

echo "Configurações padrão criadas em .env"
echo "⚠️  LEMBRE-SE DE ADICIONAR SUAS CHAVES DE API REAIS NO ARQUIVO .env"

# Criar docker-compose.easypanel.yml
echo "Criando docker-compose.easypanel.yml..."
cat > docker-compose.easypanel.yml << EOF
version: '3.8'

services:
  cleudocode-web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cleudocode-web
    restart: unless-stopped
    environment:
      - OLLAMA_HOST=\${OLLAMA_HOST:-http://host.docker.internal:11434}
      - DEEPSEEK_MODEL=\${DEEPSEEK_MODEL:-qwen2.5-coder:7b}
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    volumes:
      - ./exports:/app/exports
      - ./uploads:/app/uploads
      - ./memory_db:/app/memory_db
      - ./agents:/app/agents
      - ./docs:/app/docs
      - ./data:/app/data
    ports:
      - "3001:8501"  # Porta configurada para EasyPanel
    networks:
      - cleudocode-network

  cleudocode-daemon:
    build:
      context: .
      dockerfile: Dockerfile.daemon
    container_name: cleudocode-daemon
    restart: unless-stopped
    environment:
      - OLLAMA_HOST=\${OLLAMA_HOST:-http://host.docker.internal:11434}
      - DEEPSEEK_MODEL=\${DEEPSEEK_MODEL:-qwen2.5-coder:7b}
      - FLASK_RUN_HOST=0.0.0.0
      - FLASK_RUN_PORT=5001
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      - ./logs:/app/logs
    ports:
      - "3000:5001"  # Porta configurada para EasyPanel
    networks:
      - cleudocode-network

networks:
  cleudocode-network:
    driver: bridge
EOF

echo "docker-compose.easypanel.yml criado com sucesso!"

# Criar script de inicialização
echo "Criando script de inicialização..."
cat > start_easypanel.sh << EOF
#!/bin/bash
# Script de inicialização para EasyPanel

cd $PROJECT_DIR
source venv/bin/activate

# Iniciar o sistema Cleudocodebot
echo "Iniciando Cleudocodebot para EasyPanel..."

# Iniciar o daemon em segundo plano
python run_daemon.py &

# Iniciar a interface web em segundo plano
streamlit run web_app.py --server.port=8501 --server.address=0.0.0.0 &

echo "Cleudocodebot iniciado!"
echo "Acesse:"
echo "  - API: http://localhost:3000"
echo "  - Web UI: http://localhost:3001"
EOF

chmod +x start_easypanel.sh

# Criar script de inicialização via Docker
echo "Criando script de inicialização Docker..."
cat > start_docker.sh << EOF
#!/bin/bash
# Script de inicialização Docker para EasyPanel

cd $PROJECT_DIR

# Iniciar os containers
docker-compose -f docker-compose.easypanel.yml up -d

echo "Containers Cleudocodebot iniciados!"
echo "Acesse:"
echo "  - API: http://localhost:3000"
echo "  - Web UI: http://localhost:3001"
EOF

chmod +x start_docker.sh

echo "==========================================="
echo "INSTALAÇÃO CONCLUÍDA!"
echo "==========================================="

echo
echo "Próximos passos:"
echo "1. Edite o arquivo .env e adicione suas chaves de API reais"
echo "2. Execute o sistema com um dos seguintes métodos:"
echo
echo "   MÉTODO 1 - Via Python (requer ambiente ativado):"
echo "     cd $PROJECT_DIR"
echo "     source venv/bin/activate"
echo "     ./start_easypanel.sh"
echo
echo "   MÉTODO 2 - Via Docker (recomendado para EasyPanel):"
echo "     cd $PROJECT_DIR"
echo "     ./start_docker.sh"
echo
echo "3. Acesse o sistema:"
echo "   - API REST: http://localhost:3000"
echo "   - Interface Web: http://localhost:3001"
echo
echo "4. Para parar o sistema:"
echo "   docker-compose -f docker-compose.easypanel.yml down"
echo
echo "⚠️  IMPORTANTE: Se o Docker não estiver funcionando corretamente,"
echo "   execute 'newgrp docker' ou faça logout/login para aplicar permissões."
echo
echo "Para mais informações sobre configuração de gateways (WhatsApp, Telegram, etc.),"
echo "consulte o README.md no diretório do projeto."