#!/bin/bash
# Script de Configuração do Cleudocodebot para EasyPanel
# Configuração para o projeto em: https://easypanel.automacoescomerciais.com.br/projects/vibecoding/create

set -e  # Sai com erro se qualquer comando falhar

echo "==========================================="
echo "CONFIGURAÇÃO DO CLEUDOCODEBOT PARA EASYPANEL"
echo "==========================================="

# Variáveis de configuração
PROJECT_NAME="cleudocodebot"
PROJECT_DIR="/home/container/$PROJECT_NAME"
PORT=3000
WEB_PORT=3001

echo "Criando estrutura de diretórios..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Criar Dockerfile para EasyPanel
cat > Dockerfile.easypanel << EOF
# Dockerfile para EasyPanel - Cleudocodebot
FROM python:3.11-slim

# Metadados
LABEL maintainer="cleudocode.automacoescomerciais.com.br"
LABEL description="Cleudocodebot - Sistema de IA Autônoma para EasyPanel"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://host.docker.internal:11434
ENV DEEPSEEK_MODEL=qwen2.5-coder:7b
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001
ENV STREAMLIT_SERVER_PORT=$WEB_PORT
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    git \\
    ffmpeg \\
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (para cache de camadas)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . .

# Instalar o pacote localmente
RUN pip install -e .

# Criar diretórios necessários
RUN mkdir -p /app/data /app/config /app/logs /app/exports /app/uploads /app/memory_db /app/agents

# Expor portas configuradas para EasyPanel
EXPOSE $PORT $WEB_PORT 5001

# Comando de inicialização
CMD ["sh", "-c", "python run_daemon.py & streamlit run web_app.py --server.port=$WEB_PORT --server.address=0.0.0.0"]
EOF

# Criar docker-compose.easypanel.yml
cat > docker-compose.easypanel.yml << EOF
version: '3.8'

services:
  cleudocodebot:
    build:
      context: .
      dockerfile: Dockerfile.easypanel
    container_name: cleudocodebot-easypanel
    restart: unless-stopped
    environment:
      - OLLAMA_HOST=\${OLLAMA_HOST:-http://host.docker.internal:11434}
      - DEEPSEEK_MODEL=\${DEEPSEEK_MODEL:-qwen2.5-coder:7b}
      - FLASK_RUN_HOST=0.0.0.0
      - FLASK_RUN_PORT=5001
      - STREAMLIT_SERVER_PORT=$WEB_PORT
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
      - "$PORT:5001"    # API REST na porta 3000 (configurada para EasyPanel)
      - "$WEB_PORT:8501"  # Interface web na porta 3001
    networks:
      - cleudocode-network

networks:
  cleudocode-network:
    driver: bridge
EOF

# Criar arquivo .env para EasyPanel
cat > .env.easypanel << EOF
# Configurações do Cleudocodebot para EasyPanel
OLLAMA_HOST=http://host.docker.internal:11434
DEEPSEEK_MODEL=qwen2.5-coder:7b
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5001
STREAMLIT_SERVER_PORT=$WEB_PORT
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

# Criar script de inicialização para EasyPanel
cat > start_easypanel.sh << EOF
#!/bin/bash
# Script de inicialização para EasyPanel

cd $PROJECT_DIR

echo "Iniciando Cleudocodebot para EasyPanel..."

# Iniciar os serviços com docker-compose
docker-compose -f docker-compose.easypanel.yml up -d

echo "Cleudocodebot iniciado com sucesso!"
echo "Acesse:"
echo "  - API REST: http://localhost:$PORT"
echo "  - Interface Web: http://localhost:$WEB_PORT"
EOF

chmod +x start_easypanel.sh

echo "==========================================="
echo "CONFIGURAÇÃO CONCLUÍDA!"
echo "==========================================="

echo
echo "Para configurar no EasyPanel:"
echo "1. Acesse: https://easypanel.automacoescomerciais.com.br/projects/vibecoding/create"
echo "2. Use as seguintes configurações:"
echo
echo "   Project Type: Docker Compose"
echo "   Repository URL: https://github.com/automacoescomerciaisintegradas/cleudocode.git"
echo "   Branch: main"
echo "   Working Directory: (deixe vazio ou use ./)"
echo "   Docker Compose File: docker-compose.easypanel.yml"
echo "   Port: $PORT"
echo
echo "3. Adicione as variáveis de ambiente:"
echo "   OLLAMA_HOST: URL do seu servidor Ollama"
echo "   DEEPSEEK_MODEL: Nome do modelo (ex: qwen2.5-coder:7b)"
echo
echo "4. O sistema estará disponível em:"
echo "   - API REST: http://seu-ip:$PORT"
echo "   - Interface Web: http://seu-ip:$WEB_PORT"
echo
echo "5. Para atualizar o sistema posteriormente:"
echo "   - No EasyPanel, vá até o projeto cleudocodebot"
echo "   - Clique em 'Update' para puxar as últimas alterações do repositório"
echo

echo "🎉 Configuração do Cleudocodebot para EasyPanel concluída!"
echo
echo "Para testar localmente antes de implantar no EasyPanel:"
echo "  docker-compose -f docker-compose.easypanel.yml up"