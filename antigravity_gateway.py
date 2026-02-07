import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests

# Carregar variáveis
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AntigravityGateway")

app = Flask(__name__)
CORS(app)

# Configurações
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:7b")
GATEWAY_TOKEN = os.getenv("GOOGLE_ANTIGRAVITY_TOKEN")

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    # 1. Validação de Token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized", "message": "Missing or invalid Authorization header"}), 401
    
    token = auth_header.split(" ")[1]
    if token != GATEWAY_TOKEN:
        logger.warning(f"Tentativa de acesso com token inválido: {token}")
        return jsonify({"error": "Unauthorized", "message": "Invalid token"}), 401

    # 2. Determina o Backend Real
    data = request.get_json()
    target_model = data.get('model')
    
    # Se o modelo for o do antigravity, mapeamos para o modelo real local
    if target_model == "google/antigravity-v1":
        target_model = DEEPSEEK_MODEL
        data['model'] = target_model

    logger.info(f"Recebida requisição para o modelo: {target_model}")

    try:
        # Se for um modelo GPT, usamos OpenAI
        if target_model.startswith("gpt-"):
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return jsonify({"error": "Config Error", "message": "OPENAI_API_KEY not configured on gateway"}), 500
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            response = requests.post(url, headers=headers, json=data, timeout=60)
        else:
            # Caso contrário, usamos Ollama
            url = f"{OLLAMA_HOST}/v1/chat/completions"
            response = requests.post(url, json=data, timeout=120)
            
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
             error_msg += f" - Response: {e.response.text}"
        logger.error(f"Erro ao contatar backend: {error_msg}")
        return jsonify({"error": "Backend Error", "message": error_msg}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ready", "token_configured": bool(GATEWAY_TOKEN)})

if __name__ == '__main__':
    port = int(os.getenv("CLEUDOCODE_GATEWAY_PORT", 18900))
    logger.info(f"🚀 Antigravity Gateway iniciado na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
