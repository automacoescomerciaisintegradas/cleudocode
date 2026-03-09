# CLEUDOCODE - Dockerfile Multi-Stage Elite Soberana

# Build stage
FROM python:3.10-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev ffmpeg curl git \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /app/deps

# Runtime stage
FROM python:3.10-slim

RUN groupadd -r cleudocode && useradd -r -g cleudocode cleudocode

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/deps /app/deps
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/src:/app/deps"

COPY . .

RUN chmod +x *.sh || true

USER cleudocode

EXPOSE 18900 18901 18902 19000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:19000/health || exit 1

CMD ["python3", "web_server.py"]