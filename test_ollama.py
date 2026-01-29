#!/usr/bin/env python3
import requests
import sys
from pathlib import Path

# Carregar .env
env = {}
env_path = Path(".env")
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")

host = env.get("OLLAMA_HOST", "http://localhost:11434")
print(f"Testing Ollama at: {host}")

try:
    resp = requests.get(f"{host.rstrip('/')}/api/tags", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    print("✅ Conectado com sucesso!")
    print(f"Modelos disponíveis: {[m['name'] for m in data.get('models', [])]")
except Exception as e:
    print(f"❌ Falha ao conectar: {e}")
    sys.exit(1)