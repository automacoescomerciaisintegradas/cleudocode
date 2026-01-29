import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Cleudocodebot Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Título do dashboard
st.title("🤖 Cleudocodebot Dashboard")
st.markdown("---")

# Funções auxiliares para chamar a API
API_BASE_URL = "http://localhost:5001/api/v1"

def get_status():
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_gateways():
    try:
        response = requests.get(f"{API_BASE_URL}/gateways")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_config():
    try:
        response = requests.get(f"{API_BASE_URL}/config")
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

def send_message(message, sender="dashboard_user"):
    try:
        payload = {
            "message": message,
            "sender": sender
        }
        response = requests.post(f"{API_BASE_URL}/messages", json=payload)
        return response.json() if response.status_code == 200 else {"error": "Failed to send message"}
    except Exception as e:
        return {"error": str(e)}

def get_history():
    try:
        response = requests.get(f"{API_BASE_URL}/messages")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_stats():
    """Obtém estatísticas do sistema"""
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

# Barra lateral com informações do sistema
with st.sidebar:
    st.header("📊 Status do Sistema")
    
    # Obter status do sistema
    status = get_status()
    if status:
        st.success(f"✅ Status: {status.get('status', 'unknown')}")
        st.info(f"🕒 Última atualização: {status.get('timestamp', 'N/A')}")
        st.metric("Daemon", "Rodando" if status.get('daemon_running', False) else "Parado")
    else:
        st.error("❌ Não foi possível conectar ao daemon")
    
    st.markdown("---")
    
    # Informações de configuração
    st.header("⚙️ Configurações")
    config = get_config()
    if config:
        st.write(f"**LLM Provider:** {config.get('llm_provider', 'N/A')}")
        st.write(f"**Modelo:** {config.get('llm_model', 'N/A')}")
        st.write(f"**Debug:** {'Sim' if config.get('debug', False) else 'Não'}")
    else:
        st.write("Nenhuma configuração disponível")
    
    st.markdown("---")
    
    # Controles do sistema
    st.header("🎛️ Controles")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    with col2:
        if st.button("⏹️ Parar Daemon"):
            try:
                response = requests.post(f"{API_BASE_URL}/control/stop")
                if response.status_code == 202:
                    st.success("Daemon parado com sucesso!")
                else:
                    st.error("Falha ao parar o daemon")
            except:
                st.error("Erro ao comunicar com a API")

# Abas principais
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "💬 Chat", "🔌 Gateways", "📋 Histórico"])

with tab1:
    st.header("Visão Geral do Sistema")
    
    # Layout em colunas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("/Gateways Ativos")
        gateways = get_gateways()
        
        if gateways:
            gateway_df = pd.DataFrame(gateways)
            st.dataframe(gateway_df, use_container_width=True)
        else:
            st.info("Nenhum gateway encontrado ou não foi possível conectar à API")
    
    with col2:
        st.subheader("Configurações do Sistema")
        if config:
            # Criar cards com informações
            st.json(config)
        else:
            st.info("Nenhuma configuração disponível")

with tab2:
    st.header("💬 Interface de Chat")
    
    # Histórico de mensagens
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Exibir histórico de mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Campo de entrada para nova mensagem
    if prompt := st.chat_input("Digite sua mensagem..."):
        # Adicionar mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Exibir mensagem do usuário
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Enviar mensagem para o backend e obter resposta
        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                response = send_message(prompt)
                
                if "error" in response:
                    st.error(f"Erro: {response['error']}")
                    bot_response = "Desculpe, ocorreu um erro ao processar sua solicitação."
                else:
                    bot_response = response.get("reply", "Nenhuma resposta recebida.")
                
                st.markdown(bot_response)
        
        # Adicionar resposta do bot ao histórico
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

with tab3:
    st.header("🔌 Status dos Gateways")
    
    gateways = get_gateways()
    
    if gateways:
        for gateway in gateways:
            with st.container():
                status_color = "🟢" if gateway["running"] else "🔴"
                st.subheader(f"{status_color} {gateway['name']}")
                st.write(f"**Status:** {'Rodando' if gateway['running'] else 'Parado'}")
                st.markdown("---")
    else:
        st.info("Nenhum gateway encontrado ou não foi possível conectar à API")

with tab4:
    st.header("📋 Histórico de Mensagens")

    history = get_history()

    if history:
        # Converter o histórico para um DataFrame para melhor visualização
        df = pd.DataFrame(history)

        if not df.empty:
            # Mostrar tabela com as colunas relevantes
            display_df = df[['timestamp', 'sender_id', 'gateway', 'message']].copy()
            display_df = display_df.rename(columns={
                'timestamp': 'Data/Hora',
                'sender_id': 'Remetente',
                'gateway': 'Canal',
                'message': 'Mensagem'
            })

            st.dataframe(display_df, use_container_width=True)

            # Mostrar detalhes quando o usuário clicar
            if st.checkbox("Mostrar respostas"):
                for idx, msg in enumerate(history[:10]):  # Limitar a 10 para performance
                    with st.expander(f"Mensagem de {msg.get('sender_id', 'Desconhecido')} via {msg.get('gateway', 'Desconhecido')}"):
                        st.write("**Mensagem:**", msg.get('message', ''))
                        st.write("**Resposta:**", msg.get('response', ''))
                        st.write("**Data:**", msg.get('timestamp', ''))
        else:
            st.info("Nenhum histórico de mensagens disponível")
    else:
        st.info("Nenhum histórico de mensagens disponível")

# Footer
st.markdown("---")
st.caption("Cleudocodebot Dashboard - Sistema de Monitoramento e Controle")