#!/bin/bash
# Script de Instalação Remota do Cleudocodebot para EasyPanel
# Este script deve ser executado na VPS via SSH

set -e  # Sai com erro se qualquer comando falhar

echo "==========================================="
echo "INSTALAÇÃO REMOTA DO CLEUDOCODEBOT PARA EASYPANEL"
echo "==========================================="

# Atualizar sistema
echo "Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências
echo "Instalando dependências..."
apt install -y python3 python3-pip python3-venv git curl wget ffmpeg unzip docker.io docker-compose

# Adicionar usuário ao grupo docker
usermod -aG docker cleudocode

# Criar diretório do projeto
PROJECT_DIR="/home/cleudocode/cleudocodebot"
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
echo "Criando arquivo de configuração padrão..."
cat > .env << EOF
# Configurações do Cleudocodebot para EasyPanel
OLLAMA_HOST=http://host.docker.internal:11434
DEEPSEEK_MODEL=qwen2.5-coder:7b
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5001
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
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

# Criar docker-compose.easypanel.yml
echo "Criando docker-compose.easypanel.yml..."
cat > docker-compose.easypanel.yml << EOF
version: '3.8'

services:
  cleudocodebot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cleudocodebot-easypanel
    restart: unless-stopped
    environment:
      - OLLAMA_HOST=\${OLLAMA_HOST:-http://host.docker.internal:11434}
      - DEEPSEEK_MODEL=\${DEEPSEEK_MODEL:-qwen2.5-coder:7b}
      - FLASK_RUN_HOST=0.0.0.0
      - FLASK_RUN_PORT=5001
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      - ./logs:/app/logs
      - ./exports:/app/exports
      - ./uploads:/app/uploads
      - ./memory_db:/app/memory_db
      - ./agents:/app/agents
    ports:
      - "3000:5001"    # API REST na porta 3000 (configurada para EasyPanel)
      - "3001:8501"    # Interface web na porta 3001
    networks:
      - cleudocode-network

networks:
  cleudocode-network:
    driver: bridge
EOF

# Criar script de inicialização
echo "Criando script de inicialização..."
cat > start_easypanel.sh << EOF
#!/bin/bash
# Script de inicialização para EasyPanel

cd $PROJECT_DIR
source venv/bin/activate

echo "Iniciando Cleudocodebot para EasyPanel..."

# Iniciar o sistema com docker-compose
docker-compose -f docker-compose.easypanel.yml up -d

echo "Cleudocodebot iniciado com sucesso!"
echo "Acesse:"
echo "  - API REST: http://localhost:3000"
echo "  - Interface Web: http://localhost:3001"
EOF

chmod +x start_easypanel.sh

# Configurar o serviço systemd para iniciar automaticamente
echo "Configurando serviço systemd para iniciar automaticamente..."
cat > /etc/systemd/system/cleudocodebot.service << EOF
[Unit]
Description=Cleudocodebot - Sistema de IA Autônoma
After=network.target
Wants=docker.service
After=docker.service

[Service]
Type=simple
User=cleudocode
Group=cleudocode
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/run_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recarregar daemon do systemd e habilitar o serviço
systemctl daemon-reload
systemctl enable cleudocodebot

echo "==========================================="
echo "INSTALAÇÃO REMOTA CONCLUÍDA!"
echo "==========================================="

echo
echo "O Cleudocodebot foi instalado com sucesso na VPS!"
echo
echo "Para iniciar o serviço manualmente:"
echo "  cd $PROJECT_DIR && ./start_easypanel.sh"
echo
echo "Para iniciar como serviço do sistema:"
echo "  systemctl start cleudocodebot"
echo
echo "O sistema está configurado para iniciar automaticamente com o servidor."
echo
echo "Acesse o sistema em:"
echo "  - API REST: http://144.91.118.78:3000"
echo "  - Interface Web: http://144.91.118.78:3001"
echo
echo "⚠️  LEMBRE-SE DE EDITAR O ARQUIVO .env E ADICIONAR SUAS CHAVES DE API REAIS!"
echo
echo "🎉 Cleudocodebot pronto para uso com EasyPanel na VPS!"