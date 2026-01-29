
from flask import Flask, send_from_directory, request, jsonify, url_for, redirect, session
import os
import requests
from dotenv import load_dotenv
from rag_engine import RAGBrain
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

# OAuth Setup
from authlib.integrations.flask_client import OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={
        'scope': 'email profile',
        'token_endpoint_auth_method': 'client_secret_post'
    }
)

# Admin Whitelist
ADMIN_EMAILS = ['automacoescomerciais@gmail.com']

# Inicializa Cérebro RAG
rag_brain = RAGBrain() # Usará memory_db na pasta local

# Histórico Simples em Memória
conversation_history = []

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user:
            return jsonify({"error": "Unauthorized", "redirect": "/login"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/callback')
def authorize():
    try:
        google = oauth.create_client('google')  # create the google oauth client
        token = google.authorize_access_token()  # Access token from google (needed to get user info)
        resp = google.get('userinfo')  # userinfo contains stuff you specificed in the scrope
        user_info = resp.json()
        
        # Validation
        email = user_info.get('email')
        if email not in ADMIN_EMAILS:
            return f"Acesso Negado: O email {email} não é administrador.", 403
            
        session['user'] = user_info
        session.permanent = True  # make the session permanent so it keeps existing after browser closes
        return redirect('/')
    except Exception as e:
        return f"Erro no login: {str(e)}", 500

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/api/user')
def get_user():
    user = session.get('user')
    if user:
        return jsonify(user)
    return jsonify({"error": "Guest"}), 401

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(WEB_DIR, path)

# --- API ENDPOINTS ---

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Endpoint para conversar com o LLM (com ou sem RAG)"""
    data = request.json
    user_msg = data.get('message', '')
    use_rag = data.get('use_rag', False)
    system_prompt = data.get('system_prompt', "Você é um assistente útil.")
    
    context_str = ""
    if use_rag:
        snippets = rag_brain.search(user_msg)
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
        r = requests.post(url, json=payload)
        r.raise_for_status()
        
        reply = r.json()["choices"][0]["message"]["content"]
        
        # Salva no histórico
        conversation_history.append({"role": "user", "content": user_msg})
        conversation_history.append({"role": "assistant", "content": reply})
        
        return jsonify({"reply": reply, "context": context_str})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Endpoint para upload e indexação de arquivos"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    filename = werkzeug.utils.secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Processa RAG
    try:
        if filename.endswith('.pdf'):
            from rag_engine import extract_text_from_pdf
            with open(filepath, 'rb') as f:
                content = extract_text_from_pdf(f)
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
        success, msg = rag_brain.add_document(content, filename, "uploaded_file")
        if success:
            return jsonify({"message": msg, "filename": filename})
        else:
            return jsonify({"error": msg}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_history():
    global conversation_history
    conversation_history = []
    return jsonify({"message": "Histórico limpo"})

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """Lista os agentes disponíveis na pasta agents/"""
    agents_dir = os.path.join(BASE_DIR, 'agents')
    agents = []
    if os.path.exists(agents_dir):
        for f in os.listdir(agents_dir):
            if f.endswith(".md"):
                agents.append(f)
    return jsonify({"agents": agents})

@app.route('/api/agent/<filename>', methods=['GET'])
def get_agent(filename):
    """Lê o conteúdo de um arquivo de agente"""
    agents_dir = os.path.join(BASE_DIR, 'agents')
    filepath = os.path.join(agents_dir, werkzeug.utils.secure_filename(filename))
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return jsonify({"content": content})
    return jsonify({"error": "Agente não encontrado"}), 404

@app.route('/api/history', methods=['GET', 'POST'])
def manage_history():
    """Salva ou recupera histórico"""
    if request.method == 'POST':
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        
        # Em um app real, salvaríamos no disco. Aqui retornamos o nome.
        # Poderíamos salvar o conversation_history atual em arquivo.
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                import json
                json.dump(conversation_history, f, indent=2, ensure_ascii=False)
            return jsonify({"message": f"Histórico salvo com sucesso em {filename}", "filename": filename})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify(conversation_history)

@app.route('/api/memory/stats', methods=['GET'])
def memory_stats():
    """Retorna estatísticas reais do RAG"""
    try:
        count = rag_brain.collection.count()
        # Estimativa simples
        return jsonify({
            "documents": count, 
            "tokens_approx": count * 200, # estimativa
            "size_mb": "Unknown" 
        })
    except:
        return jsonify({"documents": 0, "tokens_approx": 0})

@app.route('/api/integrations/notebooklm', methods=['POST'])
def export_notebooklm():
    """Exporta memória para NotebookLM"""
    try:
        import integrations.notebooklm
        success, msg = integrations.notebooklm.export_memory_for_notebooklm(rag_brain)
        if success:
            return jsonify({"message": msg})
        return jsonify({"error": msg}), 500
    except ImportError:
         return jsonify({"error": "Módulo de integração não encontrado"}), 500

@app.route('/api/scrape', methods=['POST'])
def scrape_url_api():
    """Endpoint para extrair texto de URL"""
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL é obrigatária"}), 400
        
    try:
        success, msg = rag_brain.add_url(url)
        if success:
            return jsonify({"message": msg})
        return jsonify({"error": msg}), 500
    except Exception as e:
        return jsonify({"error": "Erro no servidor: " + str(e)}), 500

@app.route('/api/playground', methods=['POST'])
def playground_api():
    """Endpoint para o Playground - execute prompts customizados com parâmetros LLM"""
    data = request.json
    messages = data.get('messages', [])
    options = data.get('options', {})
    
    if not messages:
        return jsonify({"error": "Nenhuma mensagem fornecida"}), 400
    
    # Extrai parâmetros LLM
    temperature = options.get('temperature', 0.7)
    num_predict = options.get('num_predict', 2048)
    top_p = options.get('top_p', 0.9)
    
    try:
        url = f"{OLLAMA_HOST}/v1/chat/completions"
        payload = {
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "temperature": temperature,
            "max_tokens": num_predict,
            "top_p": top_p
        }
        r = requests.post(url, json=payload)
        r.raise_for_status()
        
        reply = r.json()["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Iniciando Nova Interface AI Platform na porta 5000...")
    app.run(port=5000, debug=True)
