# CLEUDOCODE - Dockerfile Multi-Stage Elite Soberana

# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev ffmpeg curl git \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /app/deps

# Runtime stage
FROM python:3.12-slim

RUN groupadd -r cleudocode && useradd -r -g cleudocode cleudocode

WORKDIR /app

# Deps de sistema do Chromium (Playwright) + curl/ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ffmpeg libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/deps /app/deps
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/src:/app/deps"
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

COPY . .

RUN chmod +x *.sh || true

# Browsers do Playwright (paridade com o ambiente local que funciona)
RUN python3 -m playwright install chromium

# Roda como root: o ambiente local roda como root e os volumes do compose
# (/app/memory_db, /app/uploads, ...) são root-owned — com USER cleudocode o
# RAG ficava readonly e o CONFIG_DIR (/home/cleudocode) não existia.
# (Removido USER cleudocode em 2026-08-23.)
USER root

EXPOSE 18900 18901 18902 19000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:19000/health || exit 1

CMD ["python3", "web_server.py"]