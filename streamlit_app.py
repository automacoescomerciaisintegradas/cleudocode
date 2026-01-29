import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()                     # carrega .env
API_URL = "http://127.0.0.1:5000" # Flask base URL

# -------------------------------------------------
# UI – estilos premium
# -------------------------------------------------
st.set_page_config(
    page_title="🧠 Antigravity AI Hub",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Tipografia Inter (via Google Fonts)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    .stButton>button {background: linear-gradient(135deg, #6a11cb, #2575fc);
                      color:white; border:none; border-radius:8px;
                      padding:0.5rem 1rem; font-weight:600;}
    .stButton>button:hover {opacity:0.9;}
    .card {background: rgba(255,255,255,0.07); border-radius:12px;
           padding:1rem; margin:0.5rem 0; backdrop-filter: blur(8px);}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Sidebar – controle de parâmetros
# -------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configurações")
    use_rag = st.checkbox("Usar RAG (recuperar contexto)", value=False)
    top_k = st.slider("Número de resultados de skill", 1, 10, 5)
    st.markdown("---")
    st.caption("🔗 Conectado ao Flask em `http://127.0.0.1:5000`")

# -------------------------------------------------
# Tabs principais
# -------------------------------------------------
tab_chat, tab_search, tab_playground = st.tabs(["💬 Chat", "🔍 Busca de Skills", "🛠️ Playground"])

# -------------------  Chat -------------------
with tab_chat:
    st.subheader("Chat com LLM")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe histórico
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Entrada do usuário
    prompt = st.chat_input("Digite sua mensagem…")
    if prompt:
        # adiciona ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # chamada à API Flask
        payload = {
            "message": prompt,
            "use_rag": use_rag,
            "system_prompt": "Você é um assistente útil."
        }
        try:
            resp = requests.post(f"{API_URL}/api/chat", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            reply = data.get("reply", "⚠️ Resposta vazia")
        except Exception as e:
            reply = f"❌ Erro na API: {e}"

        # adiciona resposta ao histórico
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

# -------------------  Busca de Skills -------------------
with tab_search:
    st.subheader("Busca de Skills (antigravity‑awesome‑skills)")
    query = st.text_input("O que você quer encontrar?", placeholder="ex.: “gerar prompt para UI”")
    if st.button("Buscar", use_container_width=True):
        if not query:
            st.warning("⚠️ Digite algo para buscar.")
        else:
            payload = {"query": query, "top_k": top_k}
            try:
                r = requests.post(f"{API_URL}/api/skill_search", json=payload, timeout=30)
                r.raise_for_status()
                results = r.json().get("results", [])
            except Exception as e:
                st.error(f"❌ Falha na busca: {e}")
                results = []

            if results:
                for r in results:
                    st.markdown(
                        f"""
                        <div class=\"card\">
                        <strong>{r.get('title','Sem título')}</strong><br/>
                        <small>{r.get('path','')}</small><br/>
                        <em>{r.get('snippet','')}</em>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("🔎 Nenhum resultado encontrado.")

# -------------------  Playground -------------------
with tab_playground:
    st.subheader("Playground – teste parâmetros LLM")
    system_prompt = st.text_area(
        "System Prompt",
        value="Você é um assistente útil.",
        height=100,
    )
    user_msg = st.text_area("User Message", height=120)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    max_tokens = st.number_input("Max tokens", min_value=1, max_value=4096, value=1024, step=1)
    top_p = st.slider("Top‑p", 0.0, 1.0, 0.9, 0.05)

    if st.button("Enviar ao LLM"):
        if not user_msg.strip():
            st.warning("⚠️ Mensagem do usuário vazia.")
        else:
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
                "options": {
                    "temperature": temperature,
                    "max_predict": max_tokens,
                    "top_p": top_p,
                },
            }
            try:
                r = requests.post(f"{API_URL}/api/playground", json=payload, timeout=30)
                r.raise_for_status()
                reply = r.json().get("reply", "⚠️ Resposta vazia")
                st.markdown(f"**Resposta:**\n\n{reply}")
            except Exception as e:
                st.error(f"❌ Erro no Playground: {e}")

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.caption("🛠️ Construído com Streamlit + Flask + Qdrant + Ollama – Antigravity AI Platform")
