import streamlit as st
import requests
import json
import os
import datetime
from dotenv import load_dotenv
import base64
import rag_engine

# Carregar variáveis de ambiente
load_dotenv()

# === AUTENTICAÇÃO ===
# Importar middleware de autenticação
try:
    from core.auth_middleware import require_authentication, show_auth_status
    # Verificar autenticação antes de carregar o app
    require_authentication()
except ImportError:
    # Se não conseguir importar, continuar sem autenticação (fallback)
    st.warning("⚠️ Módulo de autenticação não encontrado. Rodando sem autenticação.")
    pass

# Configurações
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:7b")

# Importar tokens de design
from design_tokens import generate_streamlit_css

# Configuração da Página
st.set_page_config(
    page_title="Cleudocode - Chat AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar Design Tokens
st.markdown(generate_streamlit_css(), unsafe_allow_html=True)

# Inicialização do Estado (Histórico)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "Você é um especialista em código Python e ajuda o usuário a resolver problemas complexos."
if "last_selected_agent" not in st.session_state:
    st.session_state.last_selected_agent = "Customizado"

def encode_image_to_base64(uploaded_file):
    """Converte arquivo de imagem enviado para Base64"""
    try:
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode('utf-8')
        mime_type = uploaded_file.type
        return f"data:{mime_type};base64,{base64_str}"
    except Exception as e:
        st.error(f"Erro ao processar imagem: {e}")
        return None

def chat_with_ollama_stream(messages):
    """Fallback para Hub de LLMs (Sem Streaming real por enquanto, mas simulado)"""
    try:
        from core.llm_providers import llm_hub
        full_response = llm_hub.query(messages)
        
        # Simula streaming para compatibilidade com interface
        chunk_size = 10
        for i in range(0, len(full_response), chunk_size):
            yield full_response[i:i+chunk_size]
            
    except Exception as e:
        yield f"Erro ao contatar Hub de IA: {str(e)}"

import re

# Importar sandbox_manager opcionalmente (requer Docker)
try:
    from core import sandbox_manager
    SANDBOX_AVAILABLE = True
except ImportError:
    SANDBOX_AVAILABLE = False
    sandbox_manager = None

def parse_and_execute_tools_in_sandbox(llm_response):
    """
    Encontra tags <tool>, extrai seu conteúdo e o envia para execução no sandbox.
    """
    if not SANDBOX_AVAILABLE:
        return None  # Sandbox não disponível
    
    # A regex agora só precisa encontrar se existe alguma tag <tool>
    pattern = r'<tool code="[^"]+">.*?</tool>'
    match = re.search(pattern, llm_response, re.DOTALL)

    if not match:
        return None # Nenhuma ferramenta encontrada

    # Se encontrarmos, não nos importamos com o conteúdo aqui.
    # Enviamos a string *completa* da resposta do LLM para o sandbox.
    # O `sandbox_runner` fará o parsing detalhado.
    
    with st.spinner("Executando ferramentas no ambiente seguro (sandbox)..."):
        result = sandbox_manager.execute_in_sandbox(llm_response)
    
    if result["success"]:
        return result["log"]
    else:
        # Se falhar, retorna o log de erro do próprio sandbox manager
        st.error(f"Falha na execução do Sandbox: {result['log']}")
        return f"Erro no Sandbox: {result['log']}"

def save_history():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_history_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.messages, f, indent=2, ensure_ascii=False)
    return filename

# --- Sidebar (Controles) ---
with st.sidebar:
    st.title("⚙️ Controles")
    
    # Mostrar status de autenticação
    try:
        from core.auth_middleware import show_auth_status
        show_auth_status()
    except:
        pass
    
    # Branding Sidebar
    st.markdown("---")
    try:
        from design_tokens import COLORS
        brand_color = COLORS['brand']['primary']
    except:
        brand_color = "#FF5F5F"
        
    st.markdown(f"""
    <div style='
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    '>
        <div style='color: {brand_color}; font-weight: 900; font-size: 1.2rem; letter-spacing: -1px; margin-bottom: 5px;'>
            CLEUDOCODE 🤖🚀
        </div>
        <div style='color: #666; font-size: 0.75rem; line-height: 1.4;'>
            "© Automações Comerciais Integradas! 2026<br>
            Todos os direitos reservados."<br>
            <br>
            <a href='https://github.com/automacoescomerciaisintegradas/cleudocode' style='color: #888; text-decoration: none; border-bottom: 1px solid #333;'>GitHub Project</a><br>
            <span style='font-size: 0.7rem;'>contato@automacoescomerciais.com.br</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎭 Personalidade")
    
    # Carregar Agentes Disponíveis
    agents_dir = "agents"
    available_agents = ["Customizado"]
    if os.path.exists(agents_dir):
        available_agents += [f for f in os.listdir(agents_dir) if f.endswith(".md")]
        
    selected_agent = st.selectbox("Escolha um Agente:", available_agents)
    
    # Lógica de Carregamento de Agente
    if selected_agent != st.session_state.last_selected_agent:
        st.session_state.last_selected_agent = selected_agent
        if selected_agent != "Customizado":
            agent_path = os.path.join(agents_dir, selected_agent)
            try:
                with open(agent_path, "r", encoding="utf-8") as f:
                    loaded_prompt = f.read()
                st.session_state.system_prompt = loaded_prompt
                
                # --- NOVO: Saudação Automática ---
                with st.spinner(f"Ativando {selected_agent}..."):
                    # Prepara a mensagem para a LLM se apresentar
                    greet_messages = [
                        {"role": "system", "content": st.session_state.system_prompt},
                        {"role": "user", "content": "Olá! Quem é você e qual sua missão neste projeto? Apresente-se brevemente."}
                    ]
                    
                    # Gerar resposta da IA
                    from core.llm_providers import llm_hub
                    greeting = llm_hub.query(greet_messages)
                    st.session_state.messages.append({"role": "assistant", "content": greeting})
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao carregar agente: {e}")

    st.session_state.system_prompt = st.text_area(
        "Prompt do Sistema:",
        value=st.session_state.system_prompt,
        height=200,
        help="Defina como o assistente deve se comportar."
    )
    
    st.markdown("---")
    st.subheader("🧠 Inteligência")
    st.session_state.use_rag = st.checkbox("Ativar Memória (RAG)", value=True, help="Usa seus documentos indexados para responder.")
    
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    if st.button("💾 Salvar Histórico", use_container_width=True):
        filename = save_history()
        st.success(f"Salvo em: `{filename}`")
        
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 Carregar Arquivo de Texto", type=['txt', 'md', 'py', 'json'])
    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8")
        if st.button("📥 Adicionar ao Contexto"):
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Conteúdo do arquivo '{uploaded_file.name}':\n\n{content}"
            })
            st.success(f"Arquivo '{uploaded_file.name}' adicionado!")

# --- Inicialização RAG Brain ---
if "rag_brain" not in st.session_state:
    st.session_state.rag_brain = rag_engine.RAGBrain()

    # Branding header
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"""
            <div style='background: #FF5F5F; width: 80px; height: 80px; border-radius: 20px; 
                 display: flex; align-items: center; justify-content: center; transform: rotate(-5deg);'>
                <span style='font-size: 40px;'>🤖</span>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.title("Cleudocode")
        st.markdown(f"<p style='color: #FF5F5F; font-weight: 600; margin-top: -15px;'>THE AI THAT ACTUALLY DOES THINGS.</p>", unsafe_allow_html=True)



    st.markdown("""
    <!-- Window Header Decorator -->
    <div style='
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-bottom: none;
        border-radius: var(--radius-xl) var(--radius-xl) 0 0;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 4rem;
    '>
        <div style='width: 12px; height: 12px; border-radius: 50%; background-color: #FF5F5F; opacity: 0.8;'></div>
        <div style='width: 12px; height: 12px; border-radius: 50%; background-color: #FBBF24; opacity: 0.8;'></div>
        <div style='width: 12px; height: 12px; border-radius: 50%; background-color: #34D399; opacity: 0.8;'></div>
        <span style='color: #444; font-size: 0.7rem; font-family: var(--font-mono); margin-left: 10px; text-transform: uppercase;'>Mission Control v2.1 // System Active</span>
    </div>
""", unsafe_allow_html=True)

# --- Layout Principal com Abas (Navegação Mission Control) ---
tab_connect, tab_pulse, tab_market, tab_squad, tab_memory, tab_lab, tab_contato = st.tabs([
    "CONNECT", "PULSE", "MARKET", "SQUAD", "MEMORY", "LAB", "CONTATO"
])

with tab_connect:
    # Renderiza histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "images" in message and message["images"]:
                for img_data in message["images"]:
                    st.image(img_data, width=300)

    # Input Container (Estilo Imagem 2 - Dark Bar + Red Round Button)
    st.markdown("""
        <style>
        div[data-testid="stChatInput"] {
            border-radius: 50px !important;
            border: 1px solid #222 !important;
            background-color: #0A0A0A !important;
            padding: 5px 15px !important;
        }
        div[data-testid="stChatInput"] button {
            background-color: #FF5F5F !important;
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
            color: white !important;
            box-shadow: 0 0 15px rgba(255, 95, 95, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    prompt = st.chat_input("Defina sua próxima automação ...")

    if prompt:
        # Prepara a mensagem base
        msg_content = prompt
        msg_images = []
        
        # Processa anexo da sidebar se houver
        if "uploaded_file" in locals() and uploaded_file:
            file_type = uploaded_file.type
            if "image" in file_type:
                b64_image = encode_image_to_base64(uploaded_file)
                if b64_image: msg_images.append(b64_image)
            elif file_type == "application/pdf":
                pdf_text = rag_engine.extract_text_from_pdf(uploaded_file)
                msg_content += f"\n\n--- Conteúdo do PDF ({uploaded_file.name}) ---\n{pdf_text}\n"
            else:
                text_content = uploaded_file.read().decode("utf-8", errors="ignore")
                msg_content += f"\n\n--- Conteúdo do Arquivo ({uploaded_file.name}) ---\n{text_content}\n"
        
        # Adiciona e exibe mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": msg_content, "images": msg_images})
        with st.chat_message("user"):
            st.markdown(prompt)
            if msg_images: st.image(msg_images[0], width=300)
        
        # RAG Context
        rag_context = ""
        if st.session_state.get("use_rag", False):
            with st.spinner("Buscando na memória..."):
                snippets = st.session_state.rag_brain.search(prompt)
                if snippets:
                    rag_context = "\n\n=== CONTEXTO RECUPERADO DA MEMÓRIA ===\n" + "\n---\n".join(snippets) + "\n======================================\n"
                    with st.expander(f"🧠 {len(snippets)} memórias encontradas", expanded=False):
                        st.markdown(rag_context)

        # Resposta do Assistente
        with st.chat_message("assistant"):
            final_system_prompt = st.session_state.system_prompt
            if rag_context:
                final_system_prompt += f"\n\nUse o seguinte contexto recuperado para responder:\n{rag_context}"

            messages_to_send = [{"role": "system", "content": final_system_prompt}] + [
                m for m in st.session_state.messages if m["role"] != "system"
            ]
            
            response_stream = chat_with_ollama_stream(messages_to_send)
            full_response = st.write_stream(response_stream)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Sandbox Tools
            tool_log = parse_and_execute_tools_in_sandbox(full_response)
            if tool_log:
                with st.expander("🛠️ Ações do Agente", expanded=True):
                    st.code(tool_log)
                    st.session_state.messages.append({"role": "user", "content": f"Resultado das ferramentas:\n{tool_log}"})
                    if st.button("Continuar Execução Autônoma?"): st.rerun()

with tab_memory:
    st.markdown("""
        <div style='background: var(--bg-secondary); padding: 2rem; border-radius: var(--radius-2xl); border: 1px solid var(--border-subtle); margin-bottom: 2rem;'>
            <h2 style='margin: 0; color: white; display: flex; align-items: center; gap: 15px;'>
                <span style='color: var(--brand-primary);'>🧠</span> Gestão de Conhecimento
            </h2>
            <p style='color: var(--text-secondary); margin-top: 10px;'>Expanda a inteligência do sistema indexando documentos e páginas web.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- ÁREA 1: Upload Arquivos ---
    with st.form("upload_form"):
        upload_files = st.file_uploader("Upload Documentos (PDF, TXT, MD)", accept_multiple_files=True)
        btn_upload = st.form_submit_button("📥 Processar e Indexar Arquivos")
        
        if btn_upload:
            if not upload_files:
                st.warning("Selecione arquivos primeiro.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, file in enumerate(upload_files):
                    status_text.text(f"Lendo {file.name}...")
                    
                    text_content = ""
                    if file.name.endswith(".pdf"):
                        text_content = rag_engine.extract_text_from_pdf(file)
                    else:
                        text_content = file.read().decode("utf-8")
                    
                    status_text.text(f"Gerando Embeddings para {file.name}...")
                    success, msg = st.session_state.rag_brain.add_document(text_content, file.name, file.type)
                    
                    if success:
                        st.success(f"{file.name}: {msg}")
                    else:
                        st.error(f"{file.name}: {msg}")
                    
                    progress_bar.progress((idx + 1) / len(upload_files))
                status_text.text("Concluído!")

    st.markdown("---")
    
    # --- ÁREA 2: URL Scraping ---
    st.subheader("🌐 De uma Página Web")
    with st.form("url_form"):
        url_input = st.text_input("URL da página:", placeholder="https://exemplo.com/artigo")
        btn_scrape = st.form_submit_button("🕷️ Scrape & Indexar URL")
        
        if btn_scrape:
            if not url_input:
                st.warning("Digite uma URL válida.")
            else:
                with st.spinner(f"Baixando e indexando {url_input}..."):
                    success, msg = st.session_state.rag_brain.add_url(url_input)
                    if success:
                        st.success(f"URL Indexada: {msg}")
                    else:
                        st.error(f"Falha: {msg}")

    st.markdown("---")
    
    # --- ÁREA 3: Integrações ---
    st.subheader("🔄 Integrações")
    import integrations.notebooklm
    
    st.info("💡 Exporte sua base de conhecimento para usar no Google NotebookLM.")
    
    # Colunas para botões e links
    c_action, c_links = st.columns([1, 2])
    
    with c_action:
        if st.button("Sincronizar com NotebookLM (Gerar Fonte)"):
            with st.spinner("Gerando arquivo de sincronização..."):
                success, msg = integrations.notebooklm.export_memory_for_notebooklm(st.session_state.rag_brain)
                if success:
                    st.success("Sincronização OK!")
                    st.info(f"Arquivo gerado localmente em: `{msg}`")
                else:
                    st.error(msg)
                    
    with c_links:
        st.caption("Acesso Rápido (Fontes):")
        st.link_button("🌐 Google", "https://google.com")
        st.link_button("🤖 ChatGPT", "https://chat.openai.com")
        st.link_button("🤗 Outras LLMs (HuggingFace)", "https://huggingface.co")

with tab_lab:
    st.header("🧪 Playground")
    
    # 1. Configuração Lateral (Direita na imagem, aqui simulamos com colunas)
    col_play, col_config = st.columns([3, 1])
    
    with col_config:
        st.subheader("Parâmetros")
        p_temp = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="p_temp")
        p_tokens = st.number_input("Max Tokens", 64, 32000, 2048, step=128, key="p_tokens")
        p_top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.05, key="p_top_p")
        
        st.markdown("---")
        if st.button("🗑️ Resetar Playground"):
            st.session_state.playground_msgs = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": ""}
            ]
            st.rerun()

    # 2. Estado do Playground
    if "playground_msgs" not in st.session_state:
        st.session_state.playground_msgs = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": ""}
        ]

    with col_play:
        # Renderiza Blocos Editáveis
        indices_to_remove = []
        
        for i, msg in enumerate(st.session_state.playground_msgs):
            with st.container(border=True):
                c1, c2 = st.columns([1, 5])
                with c1:
                    new_role = st.selectbox(f"Role", ["system", "user", "assistant"], index=["system", "user", "assistant"].index(msg["role"]), key=f"role_{i}", label_visibility="collapsed")
                    st.session_state.playground_msgs[i]["role"] = new_role
                    
                    if st.button("🗑️", key=f"del_{i}"):
                        indices_to_remove.append(i)
                        
                with c2:
                    new_content = st.text_area(f"Content", value=msg["content"], height=100, key=f"content_{i}", label_visibility="collapsed")
                    st.session_state.playground_msgs[i]["content"] = new_content

        # Remove deletados
        if indices_to_remove:
            for idx in sorted(indices_to_remove, reverse=True):
                del st.session_state.playground_msgs[idx]
            st.rerun()

        # Botões de Ação
        c_add, c_gen = st.columns([1, 4])
        with c_add:
            if st.button("➕ Novo Bloco"):
                st.session_state.playground_msgs.append({"role": "user", "content": ""})
                st.rerun()
                
        with c_gen:
            if st.button("🚀 Gerar (Run)", type="primary", use_container_width=True):
                # Executa
                with st.spinner("Gerando..."):
                    # Prepara payload customizado
                    try:
                        from core.llm_providers import llm_hub
                        ans = llm_hub.query(model=MODEL, messages=st.session_state.playground_msgs, temperature=p_temp, max_tokens=p_tokens, top_p=p_top_p)
                        st.session_state.playground_msgs.append({"role": "assistant", "content": ans})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                    except Exception as e:
                        st.error(f"Erro de conexão: {e}")

with tab_pulse:
    # === CSS Customizado para Terminal - Design System Integrado ===
    st.markdown("""
    <style>
        /* Terminal Header Card */
        .terminal-header {
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-xl);
            padding: 20px 24px;
            margin-bottom: 16px;
            font-family: var(--font-mono);
        }
        
        .terminal-header .title {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        }
        
        .terminal-header .prompt-symbol {
            color: var(--brand-primary);
            font-weight: bold;
        }
        
        .terminal-header .version {
            color: var(--text-muted);
            font-size: 13px;
        }
        
        .terminal-header .info-row {
            font-size: 13px;
            color: var(--text-secondary);
            margin: 4px 0;
        }
        
        .terminal-header .info-label {
            color: var(--text-muted);
        }
        
        .terminal-header .info-value {
            color: var(--brand-accent);
            margin-left: 8px;
        }
        
        /* Command List Card */
        .command-card {
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-xl);
            padding: 20px 24px;
            margin-bottom: 16px;
            font-family: var(--font-mono);
        }
        
        .command-card p {
            color: var(--text-secondary);
            margin-bottom: 16px;
            font-size: 14px;
        }
        
        .command-item .cmd {
            color: var(--brand-secondary);
            font-weight: 500;
        }
        
        .command-item .desc {
            color: var(--text-muted);
        }
    </style>
    """, unsafe_allow_html=True)

    
    # === Estado do Terminal ===
    if "terminal_history" not in st.session_state:
        st.session_state.terminal_history = []
    if "terminal_output" not in st.session_state:
        st.session_state.terminal_output = []
    
    # === Comandos Disponíveis ===
    CLI_COMMANDS = {
        "help": "Ver todos os comandos (ajuda)",
        "agentes": "Listar agentes disponíveis",
        "modelo": "Ver/trocar modelo de IA",
        "status": "Mostrar status da sessão",
        "design": "Assistente de UI/UX design",
        "stitch": "Sobre Google Stitch AI",
        "run": "Executar comando no terminal",
        "read": "Ler arquivo do projeto",
        "clear": "Limpar histórico do terminal",
        "sobre": "Informações da versão",
        "extensoes": "Ver extensões ativas",
        "sair": "Sair do terminal",
    }
    
    def execute_command(cmd_input):
        """Processa e executa comandos do terminal"""
        original_input = cmd_input.strip()
        parts = original_input.split(" ", 1)
        cmd = parts[0].lower().lstrip("/")
        args = parts[1] if len(parts) > 1 else ""
        
        # Aliases em português
        ALIASES = {
            "ajuda": "help",
            "ajudar": "help",
            "comandos": "help",
            "agentes": "agents",
            "agente": "agents",
            "listar": "agents",
            "lista": "agents",
            "modelo": "model",
            "modelos": "model",
            "limpar": "clear",
            "executar": "run",
            "rodar": "run",
            "ler": "read",
            "sobre": "about",
            "sair": "quit",
            "extensoes": "extensions",
            "extensões": "extensions",
        }
        
        # Detectar frases naturais
        input_lower = original_input.lower()
        if any(x in input_lower for x in ["lista de agentes", "listar agentes", "mostrar agentes", "ver agentes"]):
            cmd = "agents"
        elif any(x in input_lower for x in ["qual modelo", "trocar modelo", "mudar modelo"]):
            cmd = "model"
        elif any(x in input_lower for x in ["limpar tela", "limpar terminal", "clear"]):
            cmd = "clear"
        elif cmd in ALIASES:
            cmd = ALIASES[cmd]
        
        output = []
        
        # Define caminho do python no venv para comandos de shell
        venv_python = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
        
        if cmd == "help":
            output.append("📚 **Comandos CLI Disponíveis:**\n")
            for c, desc in CLI_COMMANDS.items():
                output.append(f"  `/{c}` — {desc}")
            output.append("\n💡 **Dica:** Você também pode descrever tarefas em linguagem natural!")
            
        elif cmd == "about":
            output.append("**🚀 CLEUDO CODE** (v0.50.0)")
            output.append(f"Model: `{MODEL}`")
            output.append(f"Host: `cleudocode.automacoescomerciais.com.br`")
            output.append(f"Directory: `{os.getcwd()}`")
            
        elif cmd == "status":
            output.append("**📊 Status da Sessão:**")
            output.append(f"  ✅ Servidor: Conectado (`cleudocode.automacoescomerciais.com.br`)")
            output.append(f"  🤖 Modelo: `{MODEL}`")
            output.append(f"  📁 Diretório: `{os.getcwd()}`")
            output.append(f"  💬 Mensagens no Chat: {len(st.session_state.messages)}")
            output.append(f"  🧠 Memória RAG: Ativa")
            
        elif cmd == "agents":
            if args == "manage" or args == "":
                output.append("**🤖 Agentes Disponíveis:**\n")
                agents_dir = "agents"
                if os.path.exists(agents_dir):
                    agents = [f for f in os.listdir(agents_dir) if f.endswith(".md")]
                    for agent in agents:
                        output.append(f"  • `{agent}`")
                    output.append(f"\n📌 **Using:** {len(agents)} agents")
                else:
                    output.append("  Nenhum agente encontrado.")
            else:
                output.append(f"Uso: `/agents` ou `/agents manage`")
                
        elif cmd == "model":
            output.append("**🔧 Seleção de Modelo:**")
            output.append(f"\n**Configuração Atual:**")
            output.append(f"  Modelo: `{MODEL}`")
            output.append(f"\n**🌐 Bonsai AI (Roteamento Inteligente — Frontier Models):**")
            output.append(f"  • `anthropic/claude-3-5-sonnet` — Claude Sonnet (padrão)")
            output.append(f"  • `openai/gpt-4o-mini` — GPT-4o Mini (rápido)")
            output.append(f"  • `anthropic/claude-3-5-sonnet-20241022` — Claude 200K ctx")
            output.append(f"  • `auto` — Bonsai escolhe o melhor modelo automaticamente")
            output.append(f"  ➡️  Configure `BONSAI_API_KEY` no `.env` para ativar")
            output.append(f"\n**🖥️ Ollama Local (Modelos Instalados):**")
            output.append(f"  • `GandalfBaum/llama3.1-claude3.7:latest` ✅ {'(ativo)' if 'llama3.1-claude3.7' in MODEL or 'GandalfBaum' in MODEL else ''}")
            output.append(f"  • `llama3:8b` ✅")
            output.append(f"\n**📦 Outros Modelos Ollama (instalar com `ollama pull`):**")
            output.append(f"  • `qwen2.5-coder:7b`  →  ollama pull qwen2.5-coder:7b")
            output.append(f"  • `deepseek-coder:6.7b`  →  ollama pull deepseek-coder:6.7b")
            output.append(f"  • `llava:7b`  →  ollama pull llava:7b (vision)")
            output.append(f"\n💡 **Para trocar**: Edite `DEEPSEEK_MODEL` e `OLLAMA_MODEL` no `.env`")
            output.append(f"🔗 **Bonsai**: npm install -g @bonsai-ai/cli && bonsai login && bonsai start claude")
            
        elif cmd == "clear":
            st.session_state.terminal_output = []
            output.append("✅ Terminal limpo!")
            
        elif cmd == "run":
            if not args:
                output.append("⚠️ Uso: `/run <comando>`")
            else:
                output.append(f"🔄 Executando: `{args}`")
                try:
                    # Tenta injetar o venv se for comando python
                    exec_cmd = args
                    if os.path.exists(venv_python) and "python " in args:
                        exec_cmd = args.replace("python ", f'"{venv_python}" ')
                    
                    result = subprocess.run(exec_cmd, shell=True, capture_output=True, text=True, timeout=60)
                    if result.stdout:
                        output.append(f"```\n{result.stdout}\n```")
                    if result.stderr:
                        output.append(f"⚠️ **STDERR:**\n```\n{result.stderr}\n```")
                    output.append(f"📋 Retorno: {result.returncode}")
                except Exception as e:
                    output.append(f"❌ Erro: {str(e)}")
                    
        elif cmd == "read":
            if not args:
                output.append("⚠️ Uso: `/read <arquivo>`")
            else:
                try:
                    with open(args, "r", encoding="utf-8") as f:
                        content = f.read()
                    output.append(f"📄 **Conteúdo de `{args}`:**\n```\n{content[:2000]}\n```")
                    if len(content) > 2000:
                        output.append(f"... (truncado, total: {len(content)} chars)")
                except Exception as e:
                    output.append(f"❌ Erro ao ler arquivo: {str(e)}")
                    
        elif cmd == "write":
            output.append("⚠️ Uso: `/write <arquivo>` - Use o Playground para edição de arquivos")
            
        elif cmd == "extensions":
            output.append("**🔌 Extensions:**")
            output.append("  • RAG Memory Engine (ativo)")
            output.append("  • NotebookLM Sync (ativo)")
            output.append("  • Vision Support (ativo)")
            
        elif cmd == "quit" or cmd == "exit":
            output.append("👋 Use Ctrl+C no terminal ou feche a aba para sair.")
        
        # Comandos de Design (local, não precisa de LLM)
        elif cmd == "design" or cmd == "prompt" or "pricing" in input_lower or "card" in input_lower or "dashboard" in input_lower:
            output.append("**🎨 Assistente de Design**")
            output.append("")
            output.append("Para criar designs de UI, recomendo usar o **Google Stitch**:")
            output.append("")
            output.append("🔗 **Acesse**: https://stitch.withgoogle.com")
            output.append("")
            output.append("**Exemplo de prompt para Pricing Card:**")
            output.append("```")
            output.append("Design a pricing card component with:")
            output.append("- Dark theme (#1a1a1a background)")
            output.append("- 3 tiers: Basic, Pro, Enterprise")
            output.append("- Price with monthly/yearly toggle")
            output.append("- Feature list with checkmarks")
            output.append("- CTA button with hover effect")
            output.append("- Popular badge on middle tier")
            output.append("- Rounded corners (12px)")
            output.append("- Subtle border and shadow")
            output.append("```")
            output.append("")
            output.append("💡 **Dica**: Selecione o agente `stitch-designer.md` na sidebar para mais ajuda!")
        
        elif cmd == "stitch" or "stitch" in input_lower:
            output.append("**🎨 Google Stitch**")
            output.append("")
            output.append("🔗 https://stitch.withgoogle.com")
            output.append("")
            output.append("O Stitch transforma texto em designs de UI usando Gemini 2.5.")
            output.append("")
            output.append("**Modos:**")
            output.append("  • Standard Mode (350 gerações/mês) - Texto → UI")
            output.append("  • Experimental Mode (50 gerações/mês) - Sketch → UI")
            output.append("")
            output.append("**Exportação:**")
            output.append("  • Copy to Figma")
            output.append("  • Download HTML/CSS")
            output.append("")
            output.append("💡 Use o agente `stitch-designer.md` para prompts otimizados!")
            
        else:
            # --- NOVO: Fallback para execução de Shell direta ---
            try:
                # Se for uma frase curta com extensão conhecida ou comando shell
                if len(original_input.split()) < 15: 
                    exec_cmd = original_input
                    # Injeta venv se for python
                    if os.path.exists(venv_python) and "python " in original_input:
                        exec_cmd = original_input.replace("python ", f'"{venv_python}" ')
                    
                    # Se for ./ ou .\ , Windows precisa tratar
                    result = subprocess.run(exec_cmd, shell=True, capture_output=True, text=True, timeout=60)
                    
                    if result.stdout or result.stderr or result.returncode == 0:
                        if result.stdout:
                            output.append(f"```\n{result.stdout}\n```")
                        if result.stderr:
                            output.append(f"⚠️ **STDERR:**\n```\n{result.stderr}\n```")
                        if not result.stdout and not result.stderr and result.returncode == 0:
                            output.append(f"✅ Executado com sucesso.")
                    else:
                        output.append(f"⚠️ Comando não reconhecido ou sem saída: `{original_input}`")
                else:
                    output.append(f"⚠️ Para conversar com a IA, use a aba **Chat**.")
            except Exception as e:
                output.append(f"❌ Erro terminal: {str(e)}")
        
        return output
    
    # === UI do Terminal ===
    
    # Header - Estilo Open WebUI
    st.markdown("""
    <div class="terminal-header">
        <div class="title">
            <span class="prompt-symbol">>_</span>
            <span>CLEUDO CODE</span>
            <span class="version">(v0.50.0)</span>
        </div>
        <div class="info-row">
            <span class="info-label">model:</span>
            <span class="info-value">""" + MODEL + """</span>
            <span class="info-action">/model to change</span>
        </div>
        <div class="info-row">
            <span class="info-label">directory:</span>
            <span class="info-value">""" + os.getcwd().replace("\\", "/") + """</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions - Estilo Open WebUI
    st.markdown("""
    <div class="command-card">
        <p>Para começar, experimente um destes comandos:</p>
        <div class="command-item"><span class="cmd">/help</span> <span class="desc">— ver todos os comandos</span></div>
        <div class="command-item"><span class="cmd">/agentes</span> <span class="desc">— listar agentes disponíveis</span></div>
        <div class="command-item"><span class="cmd">/design</span> <span class="desc">— ajuda com UI/UX design</span></div>
        <div class="command-item"><span class="cmd">/stitch</span> <span class="desc">— sobre Google Stitch AI</span></div>
        <div class="command-item"><span class="cmd">/status</span> <span class="desc">— mostrar status da sessão</span></div>
        <div class="command-item"><span class="cmd">/run</span> <span class="desc">— executar comando no terminal</span></div>
    </div>
    """, unsafe_allow_html=True)

    
    # Terminal Output Area
    st.subheader("📟 Output")
    
    output_container = st.container(height=350)
    with output_container:
        if st.session_state.terminal_output:
            for entry in st.session_state.terminal_output:
                if entry["type"] == "user":
                    st.markdown(f"**› {entry['content']}**")
                else:
                    st.markdown(entry["content"])
        else:
            st.markdown("""
**🚀 Bem-vindo ao Cleudocode Terminal!**

Este terminal permite executar comandos de forma interativa.
Digite `/help` para ver os comandos disponíveis.

**Dicas para começar:**
1. Faça perguntas, edite arquivos ou execute comandos.
2. Seja específico para melhores resultados.
3. `/help` para mais informações.

**Using:** 1 agent file (configurável na sidebar)
            """)
    
    # Input Area
    st.markdown("---")
    col_input, col_btn = st.columns([6, 1])
    
    with col_input:
        cmd_input = st.text_input(
            "Comando",
            placeholder="Digite um comando ou descreva uma tarefa...",
            label_visibility="collapsed",
            key="terminal_cmd_input"
        )
    
    with col_btn:
        btn_send = st.button("▶️", use_container_width=True)
    
    # Process Command
    if btn_send and cmd_input:
        # Add user input to output
        st.session_state.terminal_output.append({
            "type": "user",
            "content": cmd_input
        })
        
        # Execute and get response  
        response = execute_command(cmd_input)
        
        for line in response:
            st.session_state.terminal_output.append({
                "type": "system",
                "content": line
            })
        
        st.rerun()
    
    # Footer
    st.markdown("""
    <div class="terminal-footer">
        <span>100% contexto</span>
        <span>•</span>
        <span>? para atalhos</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick action buttons
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.terminal_output = []
            st.rerun()
    with c2:
        if st.button("📋 Copiar", use_container_width=True):
            st.info("Use Ctrl+C para copiar texto selecionado")
    with c3:
        if st.button("📊 Status", use_container_width=True):
            response = execute_command("/status")
            for line in response:
                st.session_state.terminal_output.append({"type": "system", "content": line})
            st.rerun()
    with c4:
        if st.button("❓ Help", use_container_width=True):
            response = execute_command("/help")
            for line in response:
                st.session_state.terminal_output.append({"type": "system", "content": line})
            st.rerun()

# --- Conteúdo Adicional das Abas ---

with tab_market:
    st.markdown("""
        <div style='max-width: 1000px; margin: 0 auto; padding: 2rem;'>
            <div style='text-align: center; margin-bottom: 3rem;'>
                <h2 style='color: white; font-family: Inter; font-weight: 900; font-style: italic; font-size: 3rem; letter-spacing: -2px; text-transform: uppercase;'>MARKETPLACE</h2>
                <p style='color: #666; font-size: 1rem;'>Expanda as capacidades do Cleudocode com módulos certificados.</p>
            </div>
            
            <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem;'>
                <!-- Card 1 -->
                <div style='padding: 2rem; background: #0A0A0A; border: 1px solid #111; border-radius: 24px; opacity: 0.6; filter: grayscale(1);'>
                    <div style='width: 40px; height: 40px; background: #FF5F5F; border-radius: 10px; margin-bottom: 1.5rem;'></div>
                    <h4 style='color: white; margin-bottom: 0.5rem;'>Automação ERP</h4>
                    <p style='color: #444; font-size: 0.8rem;'>Integração direta com sistemas de gestão comercial.</p>
                    <div style='margin-top: 1rem; color: #FF5F5F; font-size: 0.65rem; font-weight: 800; letter-spacing: 1px;'>EM BREVE</div>
                </div>
                <!-- Card 2 -->
                <div style='padding: 2rem; background: #0A0A0A; border: 1px solid #111; border-radius: 24px; opacity: 0.6; filter: grayscale(1);'>
                    <div style='width: 40px; height: 40px; background: #6366F1; border-radius: 10px; margin-bottom: 1.5rem;'></div>
                    <h4 style='color: white; margin-bottom: 0.5rem;'>Advanced Vision</h4>
                    <p style='color: #444; font-size: 0.8rem;'>Processamento de OCR e análise de imagens em massa.</p>
                    <div style='margin-top: 1rem; color: #FF5F5F; font-size: 0.65rem; font-weight: 800; letter-spacing: 1px;'>EM BREVE</div>
                </div>
                <!-- Card 3 -->
                <div style='padding: 2rem; background: #0A0A0A; border: 1px solid #111; border-radius: 24px; opacity: 0.6; filter: grayscale(1);'>
                    <div style='width: 40px; height: 40px; background: #10B981; border-radius: 10px; margin-bottom: 1.5rem;'></div>
                    <h4 style='color: white; margin-bottom: 0.5rem;'>Voice Engine</h4>
                    <p style='color: #444; font-size: 0.8rem;'>Interação por voz com latência ultra-baixa.</p>
                    <div style='margin-top: 1rem; color: #FF5F5F; font-size: 0.65rem; font-weight: 800; letter-spacing: 1px;'>EM BREVE</div>
                </div>
            </div>
            
            <div style='margin-top: 4rem; text-align: center; padding: 3rem; background: rgba(255,95,95,0.03); border: 1px solid rgba(255,95,95,0.1); border-radius: 30px;'>
                <p style='color: #FF5F5F; font-weight: 700; font-size: 1.2rem;'>Quer publicar sua própria Skill?</p>
                <p style='color: #666; font-size: 0.9rem;'>O ecossistema Cleudocode está crescendo. Inscreva-se para o Beta do Developer Portal.</p>
                <button style='background: #FF5F5F; color: white; border: none; padding: 12px 30px; border-radius: 50px; font-weight: 700; margin-top: 1.5rem; cursor: pointer;'>JOIN WAITLIST</button>
            </div>
        </div>
    """, unsafe_allow_html=True)

with tab_squad:
    st.markdown("""
        <div style='max-width: 1200px; margin: 0 auto; padding: 2.5rem;'>
            <div style='text-align: center; margin-bottom: 4.5rem; background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, transparent 100%); padding: 4rem; border-radius: 40px; border: 1px solid rgba(255,255,255,0.05);'>
                <h2 style='color: white; font-family: Inter; font-weight: 900; font-style: italic; font-size: 3rem; letter-spacing: -2px; text-transform: uppercase; margin: 0;'>AGENT SQUAD</h2>
                <p style='color: #FF5F5F; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 5px; margin-top: 1.5rem;'>System Orchestrator</p>
            </div>

            <div style='display: grid; grid-template-columns: 2fr 1fr; gap: 2rem;'>
                <!-- Main Status -->
                <div style='padding: 3rem; background: #080808; border: 1px solid #111; border-radius: 32px;'>
                    <h4 style='color: #444; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 2.5rem; font-weight: 800;'>Status da Orquestração</h4>

                    <div style='display: flex; flex-direction: column; gap: 2rem;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; padding-bottom: 1.25rem; border-bottom: 1px solid #151515;'>
                            <span style='color: #888;'>Capacidade de Resposta</span>
                            <span style='color: #34D399; font-weight: 800;'>98.4%</span>
                        </div>
                        <div style='display: flex; justify-content: space-between; align-items: center; padding-bottom: 1.25rem; border-bottom: 1px solid #151515;'>
                            <span style='color: #888;'>Latência Média</span>
                            <span style='color: #FBBF24; font-weight: 800;'>142ms</span>
                        </div>
                        <div style='display: flex; justify-content: space-between; align-items: center; padding-bottom: 1.25rem; border-bottom: 1px solid #151515;'>
                            <span style='color: #888;'>Agentes Ativos</span>
                            <span style='color: white; font-weight: 800;'>12 / 12</span>
                        </div>
                    </div>
                </div>

                <!-- Connection Status -->
                <div style='padding: 3rem; background: #0A0A0A; border: 1px solid #111; border-radius: 32px; text-align: center; display: flex; flex-direction: column; justify-content: center;'>
                    <div style='width: 15px; height: 15px; background: #FF5F5F; border-radius: 50%; box-shadow: 0 0 15px #FF5F5F; margin: 0 auto 2rem auto;'></div>
                    <h4 style='color: white; font-size: 0.9rem; margin-bottom: 1.25rem;'>SENTIENT GRID</h4>
                    <p style='color: #444; font-size: 0.7rem; margin-bottom: 2.5rem;'>SISTEMA OFFLINE</p>
                    <div style='font-size: 1.5rem; color: #111; font-weight: 900;'>DISCONNECTED</div>
                </div>
            </div>

            <div style='margin-top: 2rem; padding: 3rem; background: #080808; border: 1px solid #111; border-radius: 32px;'>
                <p style='color: #555; font-size: 0.8rem; line-height: 1.8;'>
                    O <b>Agent Squad</b> é o centro de comando que gerencia a colaboração entre instâncias especializadas.
                    A orquestração local permite que tarefas massivas sejam divididas e executadas simultaneamente sem perda de precisão.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with tab_contato:
    st.markdown("""
<div style='max-width: 1000px; margin: 0 auto; padding: 5rem; background: #080808; border: 1px solid rgba(255,255,255,0.03); border-radius: 32px; box-shadow: 0 40px 100px rgba(0,0,0,0.8);'>
    <div style='text-align: center; margin-bottom: 5rem;'>
        <h2 style='color: white; font-family: Inter; font-weight: 900; font-style: italic; font-size: 3.5rem; letter-spacing: -2px; text-transform: uppercase; margin: 0;'>CONTATO</h2>
        <div style='color: #FF5F5F; font-family: Inter; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 5px; margin-top: 1.5rem;'>
            CLEUDOCODE - THE AI THAT ACTUALLY DOES THINGS.
        </div>
    </div>

    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;'>
        <div style='padding: 3rem; background: #0A0A0A; border: 1px solid #111; border-radius: 24px;'>
            <h4 style='color: #444; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1.5rem; font-weight: 800;'>Suporte Técnico</h4>
            <p style='color: white; font-weight: 600; font-size: 1rem; font-family: var(--font-mono); margin-bottom: 1rem; line-height: 1.6;'>Assistência direta para implementação de agentes e resolução de conflitos de rede.</p>
            <p style='color: #888; font-size: 0.8rem; font-weight: 600; margin-bottom: 2rem;'>Automações Comerciais Integradas! ⚙️</p>
            <a href='mailto:contato@automacoescomerciais.com.br' style='color: #FF5F5F; text-decoration: none; font-weight: 700; font-size: 0.9rem;'>📧 Email: contato@automacoescomerciais.com.br</a>
        </div>
        <div style='padding: 3rem; background: #0A0A0A; border: 1px solid #111; border-radius: 24px;'>
            <h4 style='color: #444; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1.5rem; font-weight: 800;'>Comercial / Parcerias</h4>
            <p style='color: white; font-weight: 600; font-size: 1rem; font-family: var(--font-mono); margin-bottom: 2rem; line-height: 1.6;'>Parcerias estratégicas, licenciamento Enterprise e expansão do ecossistema.</p>
            <div style='display: flex; flex-direction: column; gap: 1rem;'>
                <a href='https://t.me/+9cdym9gvPQ9iOWNh' target='_blank' style='color: #6366F1; text-decoration: none; font-weight: 700; font-size: 0.9rem;'>💬 Telegram: Conectar agora</a>
                <a href='https://wa.me/558894227586' target='_blank' style='color: #10B981; text-decoration: none; font-weight: 700; font-size: 0.9rem;'>📱 WhatsApp: +55 88 94227586</a>
                <div style='margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #222;'>
                    <p style='color: #444; font-size: 0.6rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.75rem;'>Atendimento humano</p>
                    <a href='tel:+5588921567214' style='color: white; text-decoration: none; font-weight: 700; font-size: 0.9rem;'>📱 Telefone: +55 88 921567214</a>
                </div>
            </div>
        </div>
    </div>

    <div style='margin-top: 2.5rem; padding: 3rem; background: #0A0A0A; border: 1px solid #111; border-radius: 24px; text-align: center;'>
        <p style='color: #333; font-size: 0.9rem; line-height: 1.8;'>
            Desenvolvido por <b style='color: #555;'>Automações Comerciais Integradas</b><br>
            <span style='font-size: 0.8rem; letter-spacing: 1px; color: #222;'>SISTEMA DE MISSÃO CRÍTICA — © 2026</span>
        </p>
        <div style='margin-top: 2.5rem;'>
            <a href='http://localhost:18900' target='_blank' style='
                color: #FF5F5F;
                text-decoration: none;
                font-weight: 700;
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                border: 1px solid rgba(255,95,95,0.2);
                padding: 10px 35px;
                border-radius: 50px;
                transition: all 0.3s ease;
                display: inline-block;
            '>
                Acessar Página Principal de Contato
            </a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
