from flask import Flask, send_from_directory, request, jsonify, url_for, redirect, session
import os
import requests
from dotenv import load_dotenv

# Carregar variáveis
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_dev_key_12345")

# Configurações do LLM
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:7b")

# Histórico Simples em Memória
conversation_history = []

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Endpoint para conversar com o LLM (sem RAG inicialmente)"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Dados inválidos. JSON esperado."}), 400
        
        user_msg = data.get('message', '')
        use_rag = data.get('use_rag', False)  # Ignorar RAG por enquanto
        system_prompt = data.get('system_prompt', "Você é um assistente útil.")

        # Monta mensagens
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        # Adiciona histórico recente (simplificado)
        messages.extend(conversation_history[-5:])
        messages.append({"role": "user", "content": user_msg})

        try:
            url = f"{OLLAMA_HOST}/v1/chat/completions"
            payload = {
                "model": MODEL,
                "messages": messages,
                "stream": False
            }
            r = requests.post(url, json=payload)
            r.raise_for_status()

            reply = r.json()["choices"][0]["message"]["content"]

            # Salva no histórico
            conversation_history.append({"role": "user", "content": user_msg})
            conversation_history.append({"role": "assistant", "content": reply})

            return jsonify({"reply": reply, "context": ""})

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Erro na requisição para o Ollama: {str(e)}"}), 500
        except KeyError as e:
            return jsonify({"error": f"Formato de resposta inesperado do Ollama: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"Erro interno no processamento: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Erro no processamento da requisição: {str(e)}"}), 400

# Error handlers to ensure JSON responses
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("Iniciando teste simplificado na porta 5000...")
    app.run(port=5000, debug=True)