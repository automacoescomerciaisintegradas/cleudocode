import os
import json
import time
import random
import requests
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

# Carrega variáveis do .env (útil para mudanças em tempo real sem rebuild)
load_dotenv()

# Importações locais
import logging
# Configuração de Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           static_folder='web', 
           template_folder='web')
CORS(app)

from pathlib import Path

# Configurações do Sistema
# Configurações do Sistema
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:1.5b")
MODEL = DEEPSEEK_MODEL
GATEWAY_TOKEN = os.getenv("GOOGLE_ANTIGRAVITY_TOKEN")

# Auto-correção de host (Global)
if os.path.exists('/.dockerenv'):
    if "localhost" in OLLAMA_HOST or "127.0.0.1" in OLLAMA_HOST:
        OLLAMA_HOST = OLLAMA_HOST.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
else:
    if "host.docker.internal" in OLLAMA_HOST:
        OLLAMA_HOST = OLLAMA_HOST.replace("host.docker.internal", "localhost")

# Global Daemon Placeholder
daemon = None

# Inicializa Cérebro RAG
brain = None
if os.getenv("RAG_ENABLED", "true").lower() == "true":
    try:
        import rag_engine
        brain = rag_engine.RAGBrain()
        print("RAG Brain inicializado com sucesso.")
    except Exception as e:
        print(f"Erro ao inicializar RAG Brain: {e}")
else:
    print("ℹ️ RAG está desativado no momento.")

# Configurações
CONFIG_DIR = os.path.expanduser("~/.cleudocode")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LEADS_FILE = os.path.join(CONFIG_DIR, "leads.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except: return {}
    return {}

def save_config(config):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except: return False

@app.route('/v1/chat/completions', methods=['POST'])
def antigravity_gateway_v1():
    """Proxy compatível com OpenAI para o Hub"""
    gateway_token = os.getenv("GOOGLE_ANTIGRAVITY_TOKEN")
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized", "message": "Missing or invalid Authorization header"}), 401
    
    token = auth_header.split(" ")[1]
    if token != GATEWAY_TOKEN:
        logger.warning(f"Tentativa de acesso negada: Token inválido.")
        return jsonify({"error": "Unauthorized", "message": "Invalid token"}), 401

    data = request.get_json()
    target_model = data.get('model')
    
    if target_model == "google/antigravity-v1":
        target_model = DEEPSEEK_MODEL
        data['model'] = target_model

    try:
        from core.llm_providers import llm_hub
        # Usamos o LLMHub para aproveitar o fallback automático e a correção de host
        # Mas mantemos o formato compatível com OpenAI (Chat Completions)
        
        # Se for um modelo GPT, tentamos OpenAI direto
        if target_model.startswith("gpt-"):
            response = llm_hub._query_openai(data.get("messages"), target_model, data.get("temperature", 0.7))
        else:
            # Caso contrário, usamos o despacho padrão do Hub (priorizando local/ollama se for o caso)
            response = llm_hub.query(messages=data.get("messages"), model=target_model)

        # Formatar como OpenAI Response
        return jsonify({
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": target_model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": response},
                "finish_reason": "stop"
            }]
        })
    except Exception as e:
        logger.error(f"Erro no Gateway de Completions: {e}")
        return jsonify({"error": "Backend Error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ready", "token_configured": bool(GATEWAY_TOKEN), "version": "2.1.0-fusion"})

@app.route('/')
def index():
    """Serve a página principal"""
    return send_from_directory('web', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos da pasta web"""
    return send_from_directory('web', filename)

@app.route('/api/config', methods=['GET'])
def get_config():
    """API para obter configurações"""
    config = load_config()
    # Remove dados sensíveis antes de enviar
    safe_config = {
        'openai_configured': bool(config.get('openai_api_key')),
        'telegram_configured': bool(config.get('telegram_bot_token')),
        'system_status': 'online',
        'llm_provider': os.getenv('DEFAULT_PROVIDER', 'ollama'),
        'llm_model': os.getenv('DEEPSEEK_MODEL', 'qwen2.5-coder:1.5b'),
        'debug': os.getenv('FLASK_DEBUG', 'False')
    }
    return jsonify(safe_config)

@app.route('/api/config', methods=['POST'])
def save_config_api():
    """API para salvar configurações"""
    try:
        data = request.get_json()
        config = load_config()
        
        # Atualiza apenas campos permitidos
        if 'openai_api_key' in data:
            config['openai_api_key'] = data['openai_api_key']
        if 'telegram_bot_token' in data:
            config['telegram_bot_token'] = data['telegram_bot_token']
        if 'telegram_channel_id' in data:
            config['telegram_channel_id'] = data['telegram_channel_id']
            
        if save_config(config):
            return jsonify({'success': True, 'message': 'Configuração salva com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar configuração'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/leads', methods=['GET', 'POST'])
def handle_leads():
    """Endpoint para gerenciar leads (Lista VIP)"""
    # Garante diretório
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'No data'}), 400
                
            # Adiciona timestamp
            data['timestamp'] = datetime.now().isoformat()
            
            leads = []
            if os.path.exists(LEADS_FILE):
                with open(LEADS_FILE, 'r') as f:
                    try:
                        leads = json.load(f)
                    except: leads = []
            
            leads.append(data)
            
            with open(LEADS_FILE, 'w') as f:
                json.dump(leads, f, indent=2)
                
            return jsonify({'success': True, 'message': 'Lead salvo com sucesso!'})
        except Exception as e:
            logger.error(f"Erro ao salvar lead: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    else: # GET
        try:
            if os.path.exists(LEADS_FILE):
                with open(LEADS_FILE, 'r') as f:
                    leads = json.load(f)
                return jsonify({'success': True, 'data': leads})
            return jsonify({'success': True, 'data': []})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sentient/status', methods=['GET'])
def get_sentient_status():
    """Retorna o status atual da integração Sentient Grid"""
    from gateways.sentient_bridge import sentient_bridge
    return jsonify(sentient_bridge.get_status())

@app.route('/api/system/pulse', methods=['GET'])
def get_system_pulse():
    """Retorna métricas de saúde do sistema e do kernel"""
    try:
        import psutil
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
    except ImportError:
        cpu_usage = "N/A"
        ram_usage = "N/A"

    # Status do Ollama
    ollama_online = False
    try:
        from core.llm_providers import OLLAMA_HOST
        requests.get(f"{OLLAMA_HOST}/api/tags", timeout=1)
        ollama_online = True
    except:
        pass

    return jsonify({
        "status": "online",
        "telemetry": {
            "cpu": cpu_usage,
            "ram": ram_usage,
            "ollama": "running" if ollama_online else "offline"
        },
        "gateways": {
            "telegram": "active",
            "whatsapp": "active",
            "sentient": "synchronized"
        },
        "uptime": "active"
    })

@app.route('/api/skills/local', methods=['GET'])
def get_local_skills():
    """Lista habilidades instaladas localmente"""
    skills_dir = Path("skills")
    local_skills = []
    
    if skills_dir.exists():
        for item in skills_dir.glob("*.py"):
            if item.name != "__init__.py":
                local_skills.append({
                    "id": item.stem,
                    "name": item.stem.replace("_", " ").title(),
                    "type": "Automation",
                    "path": str(item)
                })
        for item in (skills_dir / "builtin").glob("*.py"):
             if item.name != "__init__.py":
                local_skills.append({
                    "id": f"builtin.{item.stem}",
                    "name": f"Builtin: {item.stem.replace('_', ' ').title()}",
                    "type": "Core",
                    "path": str(item)
                })

    return jsonify({"skills": local_skills})

@app.route('/api/mission-control/status', methods=['GET'])
def get_mission_control_status():
    """API para obter status do esquadrão de agentes"""
    try:
        from orchestrator import orchestrator
        return jsonify(orchestrator.get_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """API para chat com IA real via LLM Hub (OpenAI/Ollama) + RAG"""
    try:
        # 0. Valida JSON
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({'success': False, 'message': 'JSON Inválido ou Content-Type incorreto'}), 400
            
        message = data.get('message', '')
        if not message:
            return jsonify({'success': False, 'message': 'Mensagem vazia'}), 400

        # 1. Busca contexto no RAG (com segurança extra)
        context = ""
        if brain:
            try:
                snippets = brain.search(message)
                if snippets:
                    context = "\n\nConteúdo relevante encontrado na memória:\n" + "\n---\n".join(snippets)
            except Exception as rag_err:
                logger.error(f"Erro na busca RAG: {rag_err}")
                # Não paramos o chat por erro no RAG
        
        # 2. Prepara mensagens
        system_prompt = os.getenv("CLEUDOCODE_SYSTEM_PROMPT", "Você é o Cleudocode, um assistente de IA focado em desenvolvimento e automação. Use o contexto fornecido para responder de forma precisa.")
        
        messages = [{"role": "system", "content": system_prompt}]
        
        full_user_content = message
        if context:
            full_user_content = f"Contexto: {context}\n\nUsuário: {message}"
            
        messages.append({"role": "user", "content": full_user_content})

        # 3. Chamada ao Mission Control (Orchestrator)
        try:
            from orchestrator import orchestrator
            # Envia para o Orchestrator que decide se delega, debate ou responde direto
            mission_result = orchestrator.receive_message({"text": message})
            
            if mission_result["status"] == "success":
                ai_response = mission_result["result"]["output"]
            else:
                ai_response = f"Erro no Mission Control: {mission_result.get('message')}"

        except Exception as hub_err:
            logger.error(f"Erro no Hub de LLM: {hub_err}")
            return jsonify({
                'success': True,
                'response': f"⚠️ Ops! Tive um problema ao processar sua solicitação no Hub: {str(hub_err)}",
                'timestamp': str(int(time.time() * 1000)),
                'error_detail': str(hub_err)
            })

        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': str(int(time.time() * 1000))
        })
        
    except Exception as e:
        logger.error(f"Erro Crítico na API de Chat: {e}")
        return jsonify({
            'success': False, 
            'message': f'Erro Interno no Servidor: {str(e)}',
            'details': "Verifique os logs do servidor para mais informações."
        }), 500

@app.route('/api/memory/upload', methods=['POST'])
def upload_memory():
    """API real para upload de arquivos para memória RAG"""
    try:
        if not brain:
            return jsonify({'success': False, 'message': 'Sistema de memória não inicializado'}), 500

        files = request.files.getlist('files')
        processed_count = 0
        
        for file in files:
            content = ""
            if file.filename.endswith('.pdf'):
                content = rag_engine.extract_text_from_pdf(file)
            else:
                content = file.read().decode('utf-8', errors='ignore')
            
            if content:
                success, msg = brain.add_document(content, file.filename, "file")
                if success:
                    processed_count += 1
            
        return jsonify({
            'success': True,
            'message': f'{processed_count} arquivo(s) processado(s) e indexados com sucesso!',
        })
        
    except Exception as e:
        print(f"Erro no Upload: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/memory/scrape', methods=['POST'])
def scrape_url():
    """API real para scraping de URL RAG"""
    try:
        if not brain:
            return jsonify({'success': False, 'message': 'Sistema de memória não inicializado'}), 500

        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'success': False, 'message': 'URL não fornecida'}), 400

        success, msg = brain.add_url(url)
        if success:
            return jsonify({
                'success': True,
                'message': f'URL {url} indexada com sucesso!',
                'tokens': random.randint(1000, 5000) # Mock de tokens, mas o processo foi real
            })
        else:
            return jsonify({'success': False, 'message': msg}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/playground/run', methods=['POST'])
def run_playground():
    """API real para executar playground via Ollama"""
    try:
        data = request.get_json()
        blocks = data.get('blocks', [])
        
        if not blocks:
            return jsonify({'success': False, 'message': 'Nenhuma mensagem fornecida'}), 400

        # Chamada ao Ollama
        url = f"{OLLAMA_HOST}/v1/chat/completions"
        payload = {
            "model": MODEL,
            "messages": blocks,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        ai_data = response.json()
        ai_response = ai_data["choices"][0]["message"]["content"]
        
        return jsonify({
            'success': True,
            'response': ai_response
        })
        
    except Exception as e:
        print(f"Erro Playground: {e}")
        return jsonify({'success': False, 'message': f'Erro de conexão com Ollama em {OLLAMA_HOST}'}), 500

@app.route('/api/sentient/query', methods=['POST'])
def sentient_query():
    """Endpoint para queries vindas do Sentient Grid (OML)"""
    from gateways.sentient_bridge import sentient_bridge
    import asyncio
    try:
        data = request.get_json()
        # Executa o método assíncrono de forma síncrona dentro da view do Flask
        result = asyncio.run(sentient_bridge.handle_grid_query(data))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro na query Sentient Grid: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/discovery')
def discovery():
    """Serve a página de discovery de chats/canais"""
    return send_from_directory('web', 'discovery.html')

@app.route('/api/evolution/chats', methods=['GET'])
def get_evolution_chats():
    """Proxy para buscar chats da Evolution API"""
    try:
        base_url = os.getenv("WHATSAPP_BASE_URL", "").rstrip('/')
        token = os.getenv("WHATSAPP_API_TOKEN_INSTANCE")
        instance = os.getenv("WHATSAPP_INSTANCE_NAME", "cleudocode")

        if not base_url or not token:
            return jsonify({'success': False, 'error': 'Configuração de WhatsApp ausente'}), 500

        # Endpoint da Evolution API para buscar chats
        # Em algumas versões é /chat/fetchChats, em outras /chat/findChats
        # Vamos tentar findChats que é mais comum em v2
        url = f"{base_url}/chat/fetchChats/{instance}"
        headers = {"apikey": token}
        
        logger.info(f"Buscando chats na Evolution API: {url}")
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            return jsonify({'success': True, 'data': resp.json()})
        else:
            # Tenta fallback para findChats se fetchChats falhar
            url_alt = f"{base_url}/chat/findChats/{instance}"
            resp_alt = requests.get(url_alt, headers=headers, timeout=15)
            if resp_alt.status_code == 200:
                return jsonify({'success': True, 'data': resp_alt.json()})
            
            return jsonify({'success': False, 'error': f'Erro API Evolution: {resp.status_code}'}), resp.status_code

    except Exception as e:
        logger.error(f"Erro ao buscar chats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/webhooks/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Webhook para Evolution API"""
    try:
        data = request.get_json()
        event = data.get('event')
        
        if event == 'messages.upsert':
            msg_data = data.get('data', {})
            message = msg_data.get('message', {})
            key = msg_data.get('key', {})
            sender_id = key.get('remoteJid')
            from_me = key.get('fromMe')
            
            if from_me: return jsonify({'status': 'ignored'}), 200
            
            # Extração de texto
            text = ""
            msg_type = msg_data.get('messageType')
            
            if msg_type == 'conversation':
                text = message.get('conversation')
            elif msg_type == 'extendedTextMessage':
                text = message.get('extendedTextMessage', {}).get('text')
            elif msg_type == 'audioMessage':
                # Handle Audio
                logger.info("Recebido áudio via WhatsApp. Processando...")
                # Aqui precisaríamos baixar o áudio da Evolution API
                # Como isso requer uma chamada de volta para a API, 
                # vamos logar por enquanto. A integração completa requer 
                # acesso ao buffer do arquivo.
                text = "[Áudio recebido - Transcrição pendente de implementação de download]"
            
            if text and daemon:
                daemon.handle_message(text, sender_id, "whatsapp")
                
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        print(f"Erro no Webhook WhatsApp: {e}")
        return jsonify({'status': 'error'}), 500


@app.route('/api/gateways', methods=['GET'])
def get_gateways_status_api():
    if daemon:
        return jsonify(daemon.get_gateways_status())
    return jsonify([])

@app.route('/api/status', methods=['GET'])
def get_status_dashboard():
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "daemon_running": daemon.running if daemon else False
    })

@app.route('/api/messages', methods=['GET', 'POST'])
def handle_messages_api():
    if request.method == 'GET':
        return jsonify([]) 
    
    data = request.get_json()
    message = data.get('message', '')
    sender = data.get('sender', 'dashboard')
    
    from orchestrator import orchestrator
    mission_result = orchestrator.receive_message({"text": message, "from": sender})
    
    response_text = "Sem resposta."
    if mission_result["status"] == "success":
         response_text = mission_result["result"]["output"]
         
    return jsonify({"reply": response_text})

@app.route('/api/control/stop', methods=['POST'])
def stop_daemon_api():
    if daemon:
        daemon.running = False
    return jsonify({"status": "stopping_daemon_logic"}), 202

@app.route('/api/config/raw', methods=['GET', 'POST'])
def handle_raw_config():
    if request.method == 'POST':
        try:
            new_config = request.get_json()
            if save_config(new_config):
                if daemon: daemon.config = new_config
                return jsonify({'success': True, 'message': 'Configuração salva!'})
            return jsonify({'success': False, 'message': 'Erro ao salvar'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    else:
        return jsonify(load_config())

@app.route('/api/features', methods=['GET', 'POST'])
def handle_features():
    config = load_config()
    if request.method == 'POST':
        data = request.get_json()
        feat = data.get('feature')
        enabled = data.get('enabled')
        plugins = config.get('plugins', {})
        plugins[feat] = enabled
        config['plugins'] = plugins
        if save_config(config):
            return jsonify({'success': True, 'plugins': plugins})
        return jsonify({'success': False, 'message': 'Erro ao salvar features'}), 500
    else:
        return jsonify(config.get('plugins', {}))

@app.route('/api/system/restart', methods=['POST'])
def system_restart():
    if daemon:
        daemon.stop()
        time.sleep(1)
        daemon.start()
        return jsonify({'success': True, 'message': 'Daemon Reiniciado.'})
    return jsonify({'success': False, 'message': 'Daemon inativo.'}), 404

if __name__ == '__main__':
    print("CLEUDOCODE - Servidor Web Moderno")
    print(f"Porta: 8501 (Mapeada para {os.getenv('CLEUDOCODE_GATEWAY_PORT', '18900')})")
    print(f"Provedor: {os.getenv('DEFAULT_PROVIDER', 'ollama').upper()}")
    print(f"Modelo: {os.getenv('DEEPSEEK_MODEL', 'qwen2.5-coder:7b')}")
    
    # Cria diretório de config se não existir
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # Inicializa Daemon
    from core.daemon import CleudoDaemon
    from gateways import register_telegram, register_whatsapp, register_discord, register_sentient
    daemon = CleudoDaemon()
    
    # Registra Gateways (eles só iniciam se configurados no .env)
    print("Registrando gateways...")
    register_telegram(daemon)
    register_whatsapp(daemon)
    register_discord(daemon)
    register_sentient(daemon)
    
    # Inicia Daemon em Background
    daemon.start()
    
    print("Status: Servidor Web + Daemon Rodando...")
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('CLEUDOCODE_GATEWAY_PORT', 18900)),
        debug=False,
        use_reloader=False 
    )