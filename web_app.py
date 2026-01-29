import streamlit as st
import requests
import json
import os
import datetime
from dotenv import load_dotenv
import base64

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:7b")

# Configuração da Página
st.set_page_config(
    page_title="Chat P2P LLM",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada
st.markdown("""
<style>
    /* === GLOBAL THEME OVERRIDES === */
    /* Fundo Principal (Deepest Black) */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Header (Transparente para fundir com o fundo) */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Sidebar (Dark Gray separado) */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #333;
    }
    
    /* Textos Gerais */
    h1, h2, h3, p, span, div, label {
        color: #ececec !important;
    }
    
    /* === CHAT MESSAGES === */
    /* Container das mensagens */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important; 
        padding: 1.5rem !important; 
    }
    
    /* Ícones do Usuário/Avatar */
    .stChatMessage .stChatMessageAvatar {
        background-color: #19c37d !important; /* ChatGPT Greenish */
        color: white !important;
    }
    
    /* Mensagem do Assistente (Fundo levemente cinza para destacar) */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #000000 !important;
    }
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1a1a1a !important; /* Slight contrast line */
    }

    /* === INPUTS & TEXTAREAS === */
    /* Cor de fundo dos inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #2f2f2f !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
    }
    
    /* Placeholder color */
    ::placeholder {
        color: #888 !important;
    }

    /* === BUTTONS === */
    /* Primary Button (Enviar, Gerar) */
    .stButton button[kind="primary"] {
        background-color: #ececec !important;
        color: #000 !important;
        border: 1px solid #ececec !important;
        font-weight: bold !important;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #ccc !important;
        border-color: #ccc !important;
    }

    /* Secondary Button */
    .stButton button[kind="secondary"] {
        background-color: #333 !important;
        color: #fff !important;
        border: 1px solid #555 !important;
    }
    .stButton button[kind="secondary"]:hover {
        background-color: #444 !important;
        border-color: #666 !important;
    }
    
    /* Tabs Selection */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #000;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: #888 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #fff !important;
        border-bottom: 2px solid white !important;
    }
</style>
""", unsafe_allow_html=True)

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
    """Envia o histórico para o Ollama com Streaming (Suporte a Vision)"""
    url = f"{OLLAMA_HOST}/v1/chat/completions"
    
    api_messages = []
    for m in messages:
        if "images" in m and m["images"]:
            content_parts = [{"type": "text", "text": m["content"]}]
            for img_b64 in m["images"]:
                content_parts.append({"type": "image_url", "image_url": {"url": img_b64}})
            api_messages.append({"role": m["role"], "content": content_parts})
        else:
            api_messages.append({"role": m["role"], "content": m["content"]})
    
    payload = {
        "model": MODEL,
        "messages": api_messages,
        "stream": True,
        "temperature": 0.2 # Mais baixo para garantir comandos precisos
    }
    
    try:
        with requests.post(url, json=payload, stream=True, timeout=120) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[6:]
                        if json_str.strip() == '[DONE]': break
                        try:
                            json_data = json.loads(json_str)
                            if 'choices' in json_data and len(json_data['choices']) > 0:
                                delta = json_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except: continue
    except Exception as e:
        yield f"❌ Erro de Conexão: {str(e)}"

import re
import subprocess

def parse_and_execute_tools(llm_response):
    """Executa tags <tool code="...">...</tool> encontradas na resposta"""
    pattern = r'<tool code="([^"]+)">\s*(.*?)\s*</tool>'
    matches = re.finditer(pattern, llm_response, re.DOTALL)
    
    log = ""
    found = False
    for match in matches:
        found = True
        code = match.group(1)
        arg = match.group(2).strip()
        
        if code == "run_shell":
            log += f"\n> Executando comando: {arg}\n"
            # Tenta usar o venv se existir
            venv_python = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
            cmd = arg
            if os.path.exists(venv_python) and "python " in arg:
                cmd = arg.replace("python ", f'"{venv_python}" ')
            
            try:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                if res.stdout: log += f"STDOUT:\n{res.stdout}\n"
                if res.stderr: log += f"STDERR:\n{res.stderr}\n"
                log += f"Retorno: {res.returncode}\n"
            except Exception as e:
                log += f"Erro: {str(e)}\n"
                
        elif code == "write_file":
            parts = arg.split('\n', 1)
            if len(parts) >= 2:
                filename = parts[0].strip()
                content = parts[1]
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    log += f"✅ Arquivo '{filename}' gravado.\n"
                except Exception as e:
                    log += f"❌ Erro ao gravar: {str(e)}\n"
        
        elif code == "read_file":
            try:
                with open(arg, 'r', encoding='utf-8') as f:
                    log += f"📄 Conteúdo de {arg}:\n{f.read()}\n"
            except Exception as e:
                log += f"❌ Erro ao ler: {str(e)}\n"

    return log if found else None

def save_history():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_history_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.messages, f, indent=2, ensure_ascii=False)
    return filename

# --- Sidebar (Controles) ---
with st.sidebar:
    st.title("⚙️ Controles")
    
    # Mascarar dados sensíveis
    display_host = "cleudocode.automacoescomerciais.com.br"
    st.write(f"**Servidor:** `{display_host}`")
    st.write(f"**Modelo:** `{MODEL}`")
    
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
                    payload = {
                        "model": MODEL,
                        "messages": greet_messages,
                        "stream": False
                    }
                    r = requests.post(f"{OLLAMA_HOST}/v1/chat/completions", json=payload)
                    if r.status_code == 200:
                        greeting = r.json()["choices"][0]["message"]["content"]
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
import rag_engine

# --- Inicialização RAG Brain ---
if "rag_brain" not in st.session_state:
    st.session_state.rag_brain = rag_engine.RAGBrain()

# --- Layout Principal com Abas ---
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "🧠 Memória", "🧪 Playground", "🖥️ Terminal"])

with tab1:
    # Renderiza histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Se tiver imagem, mostrar
            if "images" in message and message["images"]:
                for img_data in message["images"]:
                    # Remover header data:image... para exibir se necessário, ou usar st.image direto se for file
                    # Como guardamos base64 completo, st.image aceita se passarmos corretamente
                    st.image(img_data, width=300)

    # Input Container (Texto + Anexos)
    with st.container():
        c_prompt, c_upload = st.columns([6, 1])
        
        with c_upload:
            # Aceita Imagens E Documentos agora
            chat_file = st.file_uploader("📎", type=["png", "jpg", "jpeg", "pdf", "txt", "md", "py", "json"], label_visibility="collapsed")
            
        with c_prompt:
            prompt = st.chat_input("Digite sua mensagem...")

    if prompt:
        # Prepara a mensagem base
        msg_content = prompt
        msg_images = []
        
        # Processa Anexo se houver
        if chat_file:
            file_type = chat_file.type
            
            # 1. É Imagem?
            if "image" in file_type:
                b64_image = encode_image_to_base64(chat_file)
                if b64_image:
                     msg_images.append(b64_image)
            
            # 2. É PDF?
            elif file_type == "application/pdf":
                with st.spinner("Lendo PDF anexado..."):
                    pdf_text = rag_engine.extract_text_from_pdf(chat_file)
                    msg_content += f"\n\n--- Conteúdo do arquivo anexado ({chat_file.name}) ---\n{pdf_text}\n--- Fim do arquivo ---\n"
            
            # 3. É Texto/Código?
            else:
                text_content = chat_file.read().decode("utf-8", errors="ignore")
                msg_content += f"\n\n--- Conteúdo do arquivo anexado ({chat_file.name}) ---\n{text_content}\n--- Fim do arquivo ---\n"
        
        # Monta objeto da mensagem
        msg_data = {"role": "user", "content": msg_content}
        if msg_images:
            msg_data["images"] = msg_images
            
        # Adiciona ao histórico e exibe
        st.session_state.messages.append(msg_data)
        with st.chat_message("user"):
            st.markdown(prompt) # Mostra apenas o prompt original para ficar limpo visualmente
            
            # Mostra prévia do anexo
            if chat_file:
                if msg_images:
                    st.image(msg_images[0], width=300)
                else:
                    st.info(f"📎 Anexo enviado: **{chat_file.name}**")
        
        # Verifica se RAG está ativo
        rag_context = ""
        
        if st.session_state.get("use_rag", False):
            with st.spinner("Buscando na memória..."):
                snippets = st.session_state.rag_brain.search(prompt)
                if snippets:
                    rag_context = "\n\n=== CONTEXTO RECUPERADO DA MEMÓRIA ===\n" + "\n---\n".join(snippets) + "\n======================================\n"
                    with st.expander(f"🧠 {len(snippets)} memórias encontradas", expanded=False):
                        st.markdown(rag_context)

        # 3. Resposta do Assistente (Com Streaming)
        with st.chat_message("assistant"):
            final_system_prompt = st.session_state.system_prompt
            if rag_context:
                final_system_prompt += f"\n\nUse o seguinte contexto recuperado para responder à pergunta do usuário:\n{rag_context}"

            messages_to_send = [{"role": "system", "content": final_system_prompt}] + [
                m for m in st.session_state.messages if m["role"] != "system"
            ]
            
            response_stream = chat_with_ollama_stream(messages_to_send)
            full_response = st.write_stream(response_stream)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # --- EXECUÇÃO DE TOOLS ---
            tool_log = parse_and_execute_tools(full_response)
            if tool_log:
                with st.expander("🛠️ Ações do Agente", expanded=True):
                    st.code(tool_log)
                
                # Opcional: Enviar resultado de volta para o agente
                st.session_state.messages.append({"role": "user", "content": f"Resultado das ferramentas:\n{tool_log}"})
                # Re-executa se quiser que ele continue, mas por segurança vamos parar aqui ou dar um botão
                if st.button("Continuar Execução Autônoma?"):
                    st.rerun()

with tab2:
    st.header("Gestão de Conhecimento")
    st.write("Adicione arquivos aqui para aumentar o 'cérebro' do seu Chat.")
    
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

with tab3:
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
                    url = f"{OLLAMA_HOST}/v1/chat/completions"
                    payload = {
                        "model": MODEL,
                        "messages": st.session_state.playground_msgs,
                        "temperature": p_temp,
                        "max_tokens": p_tokens,
                        "top_p": p_top_p,
                        "stream": False # Sem stream no playground para simplificar a adição do bloco final
                    }
                    try:
                        r = requests.post(url, json=payload)
                        if r.status_code == 200:
                            ans = r.json()["choices"][0]["message"]["content"]
                            st.session_state.playground_msgs.append({"role": "assistant", "content": ans})
                            st.rerun()
                        else:
                            st.error(f"Erro: {r.text}")
                    except Exception as e:
                        st.error(f"Erro de conexão: {e}")

with tab4:
    # === CSS Customizado para Terminal - Estilo Open WebUI ===
    st.markdown("""
    <style>
        /* === OPEN WEBUI DARK THEME === */
        
        /* Terminal Header Card */
        .terminal-header {
            background: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 16px;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        }
        
        .terminal-header .title {
            font-size: 15px;
            font-weight: 600;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        }
        
        .terminal-header .prompt-symbol {
            color: #22c55e;
            font-weight: bold;
        }
        
        .terminal-header .version {
            color: #6b7280;
            font-size: 13px;
            font-weight: normal;
        }
        
        .terminal-header .info-row {
            font-size: 13px;
            color: #9ca3af;
            margin: 4px 0;
        }
        
        .terminal-header .info-label {
            color: #6b7280;
        }
        
        .terminal-header .info-value {
            color: #22c55e;
            margin-left: 8px;
        }
        
        .terminal-header .info-action {
            color: #3b82f6;
            font-size: 12px;
            margin-left: 12px;
        }
        
        /* Command List Card */
        .command-card {
            background: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 16px;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .command-card p {
            color: #d1d5db;
            margin-bottom: 16px;
            font-size: 14px;
        }
        
        .command-item {
            margin: 10px 0;
            font-size: 13px;
            color: #9ca3af;
        }
        
        .command-item .cmd {
            color: #3b82f6;
            font-weight: 500;
        }
        
        .command-item .desc {
            color: #6b7280;
        }
        
        /* Footer */
        .terminal-footer {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 16px;
            margin-top: 16px;
            font-size: 12px;
            color: #6b7280;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .terminal-footer .separator {
            color: #4b5563;
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
            output.append(f"\n**📦 Modelos de Código:**")
            output.append(f"  • `qwen2.5-coder:7b` {'✅' if 'qwen' in MODEL else ''}")
            output.append(f"  • `deepseek-coder:6.7b`")
            output.append(f"  • `codellama:7b`")
            output.append(f"  • `starcoder2:7b`")
            output.append(f"\n**🤖 Modelos Gerais:**")
            output.append(f"  • `llama3:8b`")
            output.append(f"  • `mistral:7b`")
            output.append(f"  • `mixtral:8x7b`")
            output.append(f"\n**�️ Modelos Vision:**")
            output.append(f"  • `llava:7b`")
            output.append(f"  • `llava:13b`")
            output.append(f"\n💡 **Para trocar**: Edite `DEEPSEEK_MODEL` no arquivo `.env`")
            
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
**🚀 Bem-vindo ao cleudocode CLI Terminal!**

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
