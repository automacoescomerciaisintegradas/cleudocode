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
API_BASE_URL = "http://localhost:18900/api"
CLEUDO_API_URL = "http://localhost:18900/api"

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
        
def get_leads():
    """Obtém leads da lista VIP (CleudoPay)"""
    try:
        response = requests.get(f"{CLEUDO_API_URL}/leads")
        return response.json().get('data', []) if response.status_code == 200 else []
    except:
        return []

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

def save_raw_config(config_data):
    try:
        response = requests.post(f"{API_BASE_URL}/config/raw", json=config_data)
        return response.status_code == 200
    except: return False

def toggle_feature(feature_name, enabled):
    try:
        requests.post(f"{API_BASE_URL}/features", json={"feature": feature_name, "enabled": enabled})
        return True
    except: return False

def restart_system():
    try:
        requests.post(f"{API_BASE_URL}/system/restart")
        return True
    except: return False

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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Dashboard", "🚀 Leads VIP", "💬 Chat", "🔌 Gateways", "📋 Histórico", "🛠️ Config"])

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
            
        st.markdown("---")
        st.subheader("Últimos Leads (VIP)")
        leads = get_leads()
        if leads:
            st.dataframe(pd.DataFrame(leads).tail(5), use_container_width=True)
        else:
            st.caption("Nenhum lead registrado ainda.")
    
    with col2:
        st.subheader("Configurações do Sistema")
        if config:
            # Criar cards com informações
            st.json(config)
        else:
            st.info("Nenhuma configuração disponível")

with tab2:
    st.header("🚀 Leads VIP - CleudoPay")
    st.caption("Lista de interessados capturados via WhatsApp")
    
    leads = get_leads()
    
    if leads:
        df_leads = pd.DataFrame(leads)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            search = st.text_input("🔍 Buscar por nome/contato")
            
        if search:
            df_leads = df_leads[df_leads['name'].str.contains(search, case=False) | df_leads['contact'].str.contains(search, case=False)]
            
        st.dataframe(
            df_leads, 
            use_container_width=True,
            column_config={
                "name": "Nome",
                "contact": "Contato (Tel/Email)",
                "timestamp": "Data/Hora",
                "source": "Origem"
            }
        )
        
        st.download_button(
            label="📥 Exportar CSV",
            data=df_leads.to_csv(index=False).encode('utf-8'),
            file_name='leads_cleudopay_vip.csv',
            mime='text/csv',
        )
    else:
        st.info("🚀 Nenhuma lead capturada ainda. Divulgue o link!")

with tab3:
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

with tab4:
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

with tab5:
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

with tab6:
    st.header("🛠️ Configuração Avançada (OpenClaw Style)")
    
    st.info("⚠️ Cuidado: Alterações aqui afetam diretamente o comportamento do bot.")
    
    # 1. Feature Toggles
    st.subheader("🧩 Plugins e Features")
    config_data = get_config() # Reusing existing helper, but raw might be better
    # But get_config returns 'safe_config', we need raw.
    # We should implement load_raw_from_helpers or just use raw endpoint.
    raw_config = requests.get(f"{API_BASE_URL}/config/raw").json() if requests.get(f"{API_BASE_URL}/config/raw").status_code == 200 else {}
    
    plugins = raw_config.get('plugins', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### Autenticação")
        goog_auth = st.toggle("Google Antigravity Auth", value=plugins.get('google-antigravity-auth', False))
        if goog_auth != plugins.get('google-antigravity-auth', False):
            toggle_feature('google-antigravity-auth', goog_auth)
            st.rerun()

    with col2:
        st.markdown("##### Memória")
        rag_enabled = st.toggle("RAG (Memory Brain)", value=plugins.get('rag', True))
        if rag_enabled != plugins.get('rag', True):
            toggle_feature('rag', rag_enabled)
            st.rerun()
            
    with col3:
        st.markdown("##### Logging")
        debug_mode = st.toggle("Debug Verboso", value=raw_config.get('debug', False))

    st.markdown("---")

    # 2. Raw JSON Editor
    st.subheader("📝 Editor de Configuração (JSON)")
    json_str = st.text_area("config.json", value=json.dumps(raw_config, indent=2), height=300)
    
    if st.button("💾 Salvar Configuração Completa"):
        try:
            new_conf = json.loads(json_str)
            if save_raw_config(new_conf):
                st.success("Configuração salva com sucesso! Reinicie o Daemon para aplicar.")
            else:
                st.error("Erro ao salvar configuração.")
        except Exception as e:
            st.error(f"Erro de sintaxe JSON: {e}")

    st.markdown("---")
    
    # 3. System Controls
    st.subheader("⚠️ Zona de Perigo")
    if st.button("🔄 Reiniciar Daemon (Aplica Configs)"):
        if restart_system():
            st.success("Comando de reinício enviado. Aguarde alguns segundos...")
            time.sleep(2)
            st.rerun()
        else:
            st.error("Falha ao comunicar com o servidor.")

# Footer
st.markdown("---")
st.caption("Cleudocodebot Dashboard - Sistema de Monitoramento e Controle")