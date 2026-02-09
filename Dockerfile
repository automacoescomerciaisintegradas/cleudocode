# ============================================
# CLEUDO CODE - Dockerfile
# LLM P2P Chat System
# ============================================

FROM ubuntu:24.04

# Metadados
LABEL maintainer="cleudocode.automacoescomerciais.com.br"
LABEL version="0.51.0"
LABEL description="CLEUDO CODE - LLM P2P Chat System"

# Variáveis de ambiente
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema e Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    ca-certificates \
    build-essential \
    ffmpeg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    && rm -rf /var/lib/apt/lists/*
    
# Deps Playwright via playwright install-deps (mais seguro)
# RUN playwright install-deps chromium

# Configurar Ambiente Python Seguro (Venv)
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copiar requirements primeiro (para cache de camadas)
COPY requirements.txt .

# Atualizar pip e instalar dependências
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir playwright pytest-playwright

# Instalar navegadores Playwright
RUN playwright install chromium

# Copiar código da aplicação
COPY app.py .
COPY web_server.py .
COPY web_app.py .
COPY streamlit_app.py .
COPY gerenciador_contatos.py .
COPY agent_loop.py .
COPY tool_box.py .
COPY rag_engine.py .
COPY descobrir_instancias.py .
COPY core ./core
COPY skills ./skills
COPY gateways ./gateways
COPY integrations ./integrations
COPY web ./web
COPY agents ./agents
COPY cli ./cli
COPY orchestrator.py .
COPY docs ./docs
COPY agent-browser ./agent-browser

# Expor porta principal
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# Comando de inicialização
CMD ["python", "web_server.py"]
