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

# Injetar CSS customizado
try:
    from custom_css import get_custom_css
    st.markdown(get_custom_css(), unsafe_allow_html=True)
except ImportError:
    pass


# Título do dashboard
st.title("🤖 Cleudocodebot Dashboard")
st.markdown("---")

# Funções auxiliares para chamar a API
API_BASE_URL = "http://localhost:8501/api"
CLEUDO_API_URL = "http://localhost:8501/api"

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

def get_mission_control_status():
    try:
        response = requests.get(f"{API_BASE_URL}/mission-control/status")
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

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

import sqlite3

DB_PATH = '/root/.9router/storage.sqlite'

DEEPSEEK_PRICES = {
    "standard": {
        "deepseek-v4-flash": {"hit": 0.07, "miss": 0.27, "out": 1.10},
        "deepseek-v4-pro": {"hit": 0.28, "miss": 2.19, "out": 8.00},
        "deepseek-v4-flash-vision-exp": {"hit": 0.07, "miss": 0.27, "out": 1.10}
    },
    "offpeak": {
        "deepseek-v4-flash": {"hit": 0.035, "miss": 0.135, "out": 0.55},
        "deepseek-v4-pro": {"hit": 0.14, "miss": 1.095, "out": 4.00},
        "deepseek-v4-flash-vision-exp": {"hit": 0.035, "miss": 0.135, "out": 0.55}
    }
}

def get_current_pricing_period():
    from datetime import timedelta
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute
    limit_minutes = 16 * 60 + 30 # 16:30
    
    if current_minutes < limit_minutes:
        period = "standard"
        period_label = "Standard (00:00 - 16:30)"
        target = now.replace(hour=16, minute=30, second=0, microsecond=0)
        time_left = target - now
    else:
        period = "offpeak"
        period_label = "Off-peak (16:30 - 24:00)"
        target = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        time_left = target - now
        
    seconds = int(time_left.total_seconds())
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    time_left_str = f"{h:02d}:{m:02d}:{s:02d}"
    
    return period, period_label, time_left_str

def load_omniroute_models():
    try:
        resp = requests.get("http://localhost:20128/v1/models", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and 'data' in data:
                return data['data']
            elif isinstance(data, list):
                return data
        return []
    except Exception as e:
        # Fallback para query no banco caso a API esteja lenta/offline
        try:
            conn = sqlite3.connect(DB_PATH)
            df_models = pd.read_sql_query("SELECT DISTINCT model, provider FROM usage_history", conn)
            conn.close()
            return [{"id": row['model'], "owned_by": row['provider'], "name": row['model']} for _, row in df_models.iterrows()]
        except:
            return []

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
        
        # Obter faixa e preços ativos
        
        raw = requests.get(f"http://localhost:8501/api/config/raw").json() if requests.get(f"http://localhost:8501/api/config/raw").status_code == 200 else {}
        show_pricing = raw.get('plugins', {}).get('pricing', False)

        if show_pricing:
            period, period_label, time_left_str = get_current_pricing_period()
            st.info(f"🕒 **Faixa:** {period_label}\n\n⏳ **Falta:** {time_left_str}")
        else:
            period = None
        
        # Seletor de modelo
        models_list = load_omniroute_models()
        active_model = config.get("llm_model", "qwen2.5-coder:7b")
        
        model_options = []
        default_index = 0
        
        for idx, m in enumerate(models_list):
            m_id = m.get("id")
            m_name = m.get("name")
            
            prices = DEEPSEEK_PRICES.get(period, {}).get(m_id)
            if show_pricing and prices:
                label = f"{m_name} (Hit: ${prices['hit']} | Miss: ${prices['miss']} | Out: ${prices['out']} /M)"
            else:
                label = m_name
                
            model_options.append(label)
            if m_id == active_model:
                default_index = idx
                
        if model_options:
            selected_model_label = st.selectbox("Modelo:", model_options, index=default_index)
            selected_model_id = models_list[model_options.index(selected_model_label)].get("id")
            
            if selected_model_id != active_model:
                config["llm_model"] = selected_model_id
                save_raw_config(config)
                st.success(f"Modelo alterado: {selected_model_id}")
                st.rerun()
        else:
            st.write(f"**Modelo:** {active_model}")
            
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🏠 Dashboard", "🚀 Leads VIP", "💬 Chat", "🔌 Gateways", "📋 Histórico", "🛠️ Config", "🌐 OmniRoute", "🤖 Esquadrão"])

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
        st.markdown("##### Extras e Debug")
        pricing_enabled = st.toggle("Mostrar Preços (Modelos)", value=plugins.get('pricing', False))
        if pricing_enabled != plugins.get('pricing', False):
            toggle_feature('pricing', pricing_enabled)
            st.rerun()
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

with tab7:
    st.header("🌐 Gateway OmniRoute - Roteamento & Consumo de IA")
    st.caption("Painel unificado de consumo em tempo real, catálogo de modelos ativos e roteamento de provedores.")

    import sqlite3
    
    DB_PATH = '/root/.9router/storage.sqlite'
    
    # Helpers para buscar dados
    def load_omniroute_stats():
        try:
            conn = sqlite3.connect(DB_PATH)
            # Total requests, tokens, success rate, latency
            query = """
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    SUM(tokens_input) as total_input,
                    SUM(tokens_output) as total_output,
                    AVG(latency_ms) as avg_latency
                FROM usage_history
            """
            df = pd.read_sql_query(query, conn)
            
            # Providers breakdown
            df_providers = pd.read_sql_query("""
                SELECT 
                    provider, 
                    COUNT(*) as requests,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    SUM(tokens_input) as tokens_input,
                    SUM(tokens_output) as tokens_output,
                    AVG(latency_ms) as avg_latency
                FROM usage_history
                GROUP BY provider
            """, conn)
            
            # Latest 15 requests
            df_latest = pd.read_sql_query("""
                SELECT timestamp, provider, model, tokens_input, tokens_output, latency_ms, success, error_code
                FROM usage_history
                ORDER BY timestamp DESC
                LIMIT 15
            """, conn)
            
            conn.close()
            return df.iloc[0], df_providers, df_latest
        except Exception as e:
            st.error(f"Erro ao conectar ao banco do OmniRoute: {e}")
            return None, None, None

    def load_omniroute_providers():
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("""
                SELECT provider, name, display_name, priority, is_active, last_used_at, test_status, last_error
                FROM provider_connections
                ORDER BY priority DESC, provider ASC
            """, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Erro ao carregar provedores: {e}")
            return pd.DataFrame()

    # Carregar os dados
    stats, providers_breakdown, latest_requests = load_omniroute_stats()
    providers_config = load_omniroute_providers()
    models_list = load_omniroute_models()

    if stats is not None:
        # Seção de Métricas Principais
        st.subheader("📊 Métricas de Consumo")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_reqs = int(stats['total_requests'] or 0)
        success_reqs = int(stats['success_count'] or 0)
        success_rate = (success_reqs / total_reqs * 100) if total_reqs > 0 else 0.0
        total_in = int(stats['total_input'] or 0)
        total_out = int(stats['total_output'] or 0)
        total_tokens = total_in + total_out
        avg_latency = float(stats['avg_latency'] or 0.0)
        
        # Custo estimado simplificado (média de $0.0015/$0.002 por 1k tokens)
        est_cost = (total_in * 0.0015 / 1000) + (total_out * 0.002 / 1000)
        
        with col1:
            st.metric("Total de Requisições", f"{total_reqs:,}")
        with col2:
            st.metric("Taxa de Sucesso", f"{success_rate:.1f}%")
        with col3:
            st.metric("Volume de Tokens", f"{total_tokens:,}", f"In: {total_in:,} | Out: {total_out:,}")
        with col4:
            st.metric("Latência Média", f"{avg_latency:.0f} ms")
        with col5:
            st.metric("Custo Estimado (USD)", f"${est_cost:,.4f}")

        st.markdown("---")
        
        # Sub-abas do OmniRoute
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📉 Consumo & Histórico", "🤖 Catálogo de Modelos", "🔌 Roteamento & Provedores"])
        
        with sub_tab1:
            st.subheader("Análise de Consumo por Provedor")
            
            if providers_breakdown is not None and not providers_breakdown.empty:
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.markdown("##### Requisições por Provedor")
                    st.bar_chart(providers_breakdown.set_index('provider')['requests'])
                    
                with col_chart2:
                    st.markdown("##### Consumo de Tokens por Provedor")
                    tokens_df = providers_breakdown.set_index('provider')[['tokens_input', 'tokens_output']]
                    st.bar_chart(tokens_df)
                
                # Tabela de detalhamento por provedor
                st.markdown("##### Detalhes de Consumo por Provedor")
                detail_df = providers_breakdown.copy()
                detail_df['taxa_sucesso'] = (detail_df['success_count'] / detail_df['requests'] * 100).round(1).astype(str) + "%"
                detail_df['tokens_total'] = detail_df['tokens_input'] + detail_df['tokens_output']
                detail_df['latencia_media_ms'] = detail_df['avg_latency'].round(0).astype(int)
                
                st.dataframe(
                    detail_df[['provider', 'requests', 'taxa_sucesso', 'tokens_total', 'latencia_media_ms']],
                    column_config={
                        "provider": "Provedor",
                        "requests": "Requisições",
                        "taxa_sucesso": "Taxa de Sucesso",
                        "tokens_total": "Total de Tokens",
                        "latencia_media_ms": "Latência Média (ms)"
                    },
                    use_container_width=True
                )
            else:
                st.info("Nenhum dado de provedor registrado.")
                
            st.markdown("---")
            st.subheader("📜 Histórico Recente de Requisições (Tempo Real)")
            if latest_requests is not None and not latest_requests.empty:
                display_latest = latest_requests.copy()
                display_latest['status'] = display_latest['success'].apply(lambda x: "🟢 Sucesso" if x == 1 else "🔴 Erro")
                display_latest['tokens_total'] = display_latest['tokens_input'] + display_latest['tokens_output']
                
                st.dataframe(
                    display_latest[['timestamp', 'status', 'provider', 'model', 'tokens_total', 'latency_ms', 'error_code']],
                    column_config={
                        "timestamp": "Data/Hora",
                        "status": "Status",
                        "provider": "Provedor",
                        "model": "Modelo",
                        "tokens_total": "Tokens",
                        "latency_ms": "Latência (ms)",
                        "error_code": "Cód. Erro"
                    },
                    use_container_width=True
                )
            else:
                st.info("Nenhuma requisição registrada no histórico.")

        with sub_tab2:
            st.subheader("🤖 Catálogo de Modelos Ativos no Gateway")
            if models_list:
                st.write(f"Total de modelos disponíveis: **{len(models_list)}**")
                
                parsed_models = []
                for m in models_list:
                    capabilities = m.get('capabilities', {})
                    parsed_models.append({
                        "id": m.get('id'),
                        "name": m.get('name') or m.get('id').split('/')[-1],
                        "owned_by": m.get('owned_by') or "Desconhecido",
                        "context_length": m.get('context_length') or 0,
                        "max_output_tokens": m.get('max_output_tokens') or 0,
                        "vision": "Sim" if capabilities.get('vision') else "Não",
                        "reasoning": "Sim" if capabilities.get('reasoning') else "Não",
                        "tool_calling": "Sim" if capabilities.get('tool_calling') else "Não",
                    })
                
                df_models = pd.DataFrame(parsed_models)
                
                search_term = st.text_input("🔍 Buscar modelo pelo ID ou Nome", "")
                if search_term:
                    df_models = df_models[df_models['id'].str.contains(search_term, case=False) | df_models['name'].str.contains(search_term, case=False)]
                
                st.dataframe(
                    df_models,
                    column_config={
                        "id": "Model ID / Path",
                        "name": "Nome de Exibição",
                        "owned_by": "Provedor Raiz",
                        "context_length": "Contexto (Tokens)",
                        "max_output_tokens": "Max Output",
                        "vision": "Visão (Multimodal)",
                        "reasoning": "Raciocínio",
                        "tool_calling": "Function Calling"
                    },
                    use_container_width=True
                )
            else:
                st.info("Nenhum modelo ativo encontrado ou gateway offline.")

        with sub_tab3:
            st.subheader("🔌 Roteamento & Status dos Provedores")
            if not providers_config.empty:
                st.write("Fila de prioridade e status de conexões ativas no roteador OmniRoute.")
                
                display_provs = providers_config.copy()
                display_provs['status'] = display_provs['is_active'].apply(lambda x: "🟢 Ativo" if x == 1 else "🔴 Inativo")
                display_provs['last_used'] = pd.to_datetime(display_provs['last_used_at']).dt.strftime('%d/%m/%Y %H:%M:%S').fillna("Nunca usado")
                display_provs['priority_badge'] = display_provs['priority'].apply(lambda x: f"Prioridade {x}")
                
                st.dataframe(
                    display_provs[['status', 'provider', 'display_name', 'priority_badge', 'last_used', 'test_status', 'last_error']],
                    column_config={
                        "status": "Status",
                        "provider": "Provedor ID",
                        "display_name": "Nome Amigável",
                        "priority_badge": "Prioridade",
                        "last_used": "Último Uso",
                        "test_status": "Status do Teste",
                        "last_error": "Último Erro"
                    },
                    use_container_width=True
                )
                
                st.info("""
                💡 **Como funciona o Roteamento OmniRoute:**
                O gateway tenta consultar os provedores com base na **prioridade** (do maior para o menor). 
                Caso ocorra um erro de cota (Quota/Rate Limit), falha de conexão (Timeout) ou erro interno (5xx), o roteador realiza um **failover automático** instantâneo para o próximo provedor disponível na fila.
                """)
            else:
                st.info("Nenhum provedor configurado no banco do OmniRoute.")
    else:
        st.warning("⚠️ Não foi possível carregar os dados do OmniRoute. Verifique se o arquivo de banco de dados existe e se a permissão de leitura está correta.")

with tab8:
    st.header("🤖 Esquadrão de Agentes (Mission Control)")
    st.caption("Status em tempo real das atividades e tarefas delegadas ao esquadrão de agentes.")
    
    squad_status = get_mission_control_status()
    
    if squad_status:
        agents = squad_status.get("agents", {})
        mission_history = squad_status.get("mission_history", [])
        
        # Métricas no topo
        col1, col2 = st.columns(2)
        total_agents = len(agents)
        active_agents = sum(1 for a in agents.values() if a.get("state") == "busy")
        
        with col1:
            st.metric("Total de Agentes no Kernel", total_agents)
        with col2:
            st.metric("Agentes Ativos no Momento", active_agents)
            
        st.markdown("---")
        
        # Grid dos agentes
        st.subheader("Esquadrão de Personas")
        if agents:
            # Converter para DataFrame para exibição estruturada
            agent_data = []
            for name, details in agents.items():
                last_active_epoch = details.get("last_active")
                last_active_str = "Nunca"
                if last_active_epoch:
                    try:
                        last_active_str = datetime.fromtimestamp(last_active_epoch).strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        pass
                
                agent_data.append({
                    "Nome": details.get("role", name.replace("-", " ").title()),
                    "Status": "🟢 Ocupado" if details.get("state") == "busy" else "💤 Inativo",
                    "Última Tarefa": details.get("last_task", "Aguardando ordens"),
                    "Progresso": f"{details.get('progress', 0)}%",
                    "Última Atividade": last_active_str
                })
            
            agent_df = pd.DataFrame(agent_data)
            st.dataframe(agent_df, use_container_width=True)
        else:
            st.info("Nenhum agente carregado no esquadrão.")
            
        st.markdown("---")
        
        # Histórico de Missões
        st.subheader("📋 Histórico de Missões Recentes")
        if mission_history:
            history_data = []
            for m in reversed(mission_history):
                timestamp_epoch = m.get("timestamp")
                timestamp_str = ""
                if timestamp_epoch:
                    try:
                        timestamp_str = datetime.fromtimestamp(timestamp_epoch).strftime('%H:%M:%S')
                    except:
                        pass
                
                history_data.append({
                    "Horário": timestamp_str,
                    "Tarefa": m.get("task"),
                    "Agente Responsável": m.get("agent", "").title(),
                    "Resultado": "✅ Sucesso" if m.get("status") == "success" else "❌ Falha"
                })
            st.dataframe(pd.DataFrame(history_data), use_container_width=True)
        else:
            st.info("Nenhuma missão recente registrada.")
    else:
        st.warning("⚠️ Não foi possível conectar ao Mission Control API. Certifique-se de que o servidor Flask está rodando na porta 8501.")

# Footer
st.markdown("---")
st.caption("Cleudocodebot Dashboard - Sistema de Monitoramento e Controle")