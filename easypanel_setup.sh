#!/bin/bash
# Script de Configuração do Projeto Cleudocodebot para EasyPanel
# Configuração para EasyPanel na porta 3000

set -e  # Sai com erro se qualquer comando falhar

echo "==========================================="
echo "CONFIGURAÇÃO DO PROJETO CLEUDOCODEBOT NO EASYPANEL"
echo "==========================================="

PROJECT_NAME="cleudocodebot"
PROJECT_DIR="/home/container/$PROJECT_NAME"
PORT=3001  # Usando porta 3001 em vez de 3000 (3000 já usada pelo EasyPanel)

echo "Criando estrutura de diretórios..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Criar Dockerfile para EasyPanel
cat > Dockerfile << EOF
# Dockerfile para EasyPanel - Cleudocodebot
FROM python:3.11-slim

# Metadados
LABEL maintainer="cleudocode.automacoescomerciais.com.br"
LABEL description="Cleudocodebot - Sistema de IA Autônoma para EasyPanel"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=$PORT
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (para cache de camadas)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . .

# Instalar o pacote localmente
RUN pip install -e .

# Criar diretórios necessários
RUN mkdir -p /app/data /app/config /app/logs /app/exports /app/uploads /app/memory_db /app/agents

# Expor porta configurada para EasyPanel
EXPOSE $PORT

# Comando de inicialização
CMD ["sh", "-c", "python run_daemon.py & streamlit run web_app.py --server.port=$PORT --server.address=0.0.0.0"]
EOF

# Criar docker-compose.easypanel.yml
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
      - STREAMLIT_SERVER_PORT=$PORT
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
      - "$PORT:$PORT"
    networks:
      - cleudocode-network

networks:
  cleudocode-network:
    driver: bridge
EOF

# Criar arquivo de configuração padrão
cat > easypanel_config.json << EOF
{
  "projectName": "$PROJECT_NAME",
  "port": $PORT,
  "envVars": [
    {
      "name": "OLLAMA_HOST",
      "value": "http://host.docker.internal:11434",
      "secret": false
    },
    {
      "name": "DEEPSEEK_MODEL",
      "value": "qwen2.5-coder:7b",
      "secret": false
    },
    {
      "name": "FLASK_SECRET_KEY",
      "value": "$(openssl rand -hex 32)",
      "secret": true
    },
    {
      "name": "SECURITY_SECRET_KEY",
      "value": "$(openssl rand -hex 32)",
      "secret": true
    }
  ],
  "dockerComposeFile": "docker-compose.easypanel.yml",
  "autoDeploy": true,
  "buildArgs": [],
  "volumes": [
    {
      "hostPath": "./data",
      "containerPath": "/app/data"
    },
    {
      "hostPath": "./config",
      "containerPath": "/app/config"
    },
    {
      "hostPath": "./logs",
      "containerPath": "/app/logs"
    }
  ]
}
EOF

echo "Arquivos de configuração para EasyPanel criados com sucesso!"

echo
echo "==========================================="
echo "INSTRUÇÕES PARA DEPLOY NO EASYPANEL"
echo "==========================================="
echo
echo "1. Acesse o EasyPanel em: https://easypanel.automacoescomerciais.com.br/projects/vibecoding/create"
echo
echo "2. No painel EasyPanel, crie um novo projeto com as seguintes configurações:"
echo "   - Project Type: Docker Compose"
echo "   - Repository URL: https://github.com/automacoescomerciaisintegradas/cleudocode.git"
echo "   - Branch: main"
echo "   - Working Directory: (deixe vazio ou use ./)"
echo "   - Docker Compose File: docker-compose.easypanel.yml"
echo "   - Port: $PORT"
echo
echo "3. Adicione as variáveis de ambiente:"
echo "   OLLAMA_HOST: Seu servidor Ollama (ex: http://host.docker.internal:11434)"
echo "   DEEPSEEK_MODEL: Nome do modelo (ex: qwen2.5-coder:7b)"
echo "   FLASK_SECRET_KEY: Sua chave secreta (gerada automaticamente)"
echo "   SECURITY_SECRET_KEY: Sua chave de segurança (gerada automaticamente)"
echo
echo "4. Clique em Deploy e o sistema será iniciado automaticamente"
echo
echo "5. Após o deploy, acesse:"
echo "   - API REST: http://localhost:$PORT/api/v1/status"
echo "   - Interface Web: http://localhost:$PORT"
echo
echo "6. Para atualizar o sistema posteriormente:"
echo "   - No EasyPanel, vá até o projeto cleudocodebot"
echo "   - Clique em 'Update' para puxar as últimas alterações do repositório"
echo
echo "==========================================="
echo "INFORMAÇÕES ADICIONAIS"
echo "==========================================="
echo
echo "O sistema Cleudocodebot inclui:"
echo "• Daemon com API REST em /api/v1/"
echo "• Interface web com chat e agentes especializados"
echo "• Sistema de persistência de dados"
echo "• Integração com múltiplos canais (WhatsApp, Telegram, Discord, etc.)"
echo "• Sistema de segurança avançado com tokens JWT"
echo "• Dashboard de monitoramento"
echo
echo "Para mais informações sobre configuração de canais de comunicação,"
echo "consulte o README.md no repositório do projeto."