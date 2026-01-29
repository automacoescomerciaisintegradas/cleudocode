from flask import Flask, send_from_directory, request, jsonify, url_for, redirect, session
import os
import requests
from dotenv import load_dotenv
import werkzeug.utils

# Carregar variáveis
load_dotenv()

# Absolute path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, 'web')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=WEB_DIR)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_dev_key_12345") # Change in production
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 # 1 hour

# Configurações do LLM
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:7b")

# Inicializa Cérebro RAG (lazy initialization)
rag_brain = None  # Will be initialized when first needed

# Histórico Simples em Memória
conversation_history = []

def get_rag_instance():
    """Get or create RAG instance"""
    global rag_brain
    if rag_brain is None:
        print("Initializing RAGBrain...")  # Debug print
        from rag_engine import RAGBrain
        rag_brain = RAGBrain()
        print("RAGBrain initialized successfully!")  # Debug print
    return rag_brain

@app.route('/')
def index():
    return send_from_directory(WEB_DIR, 'index.html')

# --- API ENDPOINTS ---

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Endpoint para conversar com o LLM (com ou sem RAG)"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Dados inválidos. JSON esperado."}), 400
        
        user_msg = data.get('message', '')
        use_rag = data.get('use_rag', False)
        system_prompt = data.get('system_prompt', "Você é um assistente útil.")

        context_str = ""
        if use_rag:
            print("Getting RAG instance for chat...")  # Debug print
            rag_instance = get_rag_instance()
            print("Searching in RAG...")  # Debug print
            snippets = rag_instance.search(user_msg)
            if snippets:
                context_str = "\nCONTEXTO RECUPERADO:\n" + "\n".join(snippets)

        # Monta mensagens
        messages = [
            {"role": "system", "content": system_prompt + context_str},
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
            print(f"Sending request to {url}")  # Debug print
            r = requests.post(url, json=payload)
            r.raise_for_status()

            reply = r.json()["choices"][0]["message"]["content"]

            # Salva no histórico
            conversation_history.append({"role": "user", "content": user_msg})
            conversation_history.append({"role": "assistant", "content": reply})

            return jsonify({"reply": reply, "context": context_str})

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
    print("Iniciando Nova Interface AI Platform na porta 5000...")
    app.run(port=5000, debug=True)