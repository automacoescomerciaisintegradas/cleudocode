"""
Authentication middleware for Cleudocode Dashboard
Similar to OpenClaw's token-based authentication
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config_manager import get_config_manager


def check_authentication():
    """
    Check if user is authenticated via token
    Returns True if authenticated, False otherwise
    """
    # Get token from query params
    query_params = st.query_params
    url_token = query_params.get("token", None)
    
    # Get stored token
    config_manager = get_config_manager()
    stored_token = config_manager.get_or_create_token()
    
    # Check if already authenticated in session
    if "authenticated" in st.session_state and st.session_state.authenticated:
        return True
    
    # Check URL token
    if url_token and url_token == stored_token:
        st.session_state.authenticated = True
        st.session_state.token = url_token
        return True
    
    # Check session token
    if "token" in st.session_state and st.session_state.token == stored_token:
        st.session_state.authenticated = True
        return True
    
    return False


def require_authentication():
    """
    Decorator/function to require authentication
    Shows login page if not authenticated
    """
    if not check_authentication():
        show_login_page()
        st.stop()


def show_login_page():
    """Show authentication page"""
    st.set_page_config(
        page_title="Cleudocode - Login",
        page_icon="🔐",
        layout="centered"
    )
    
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Logo/Title
        st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <h1 style='color: white; font-size: 3rem; margin-bottom: 0.5rem;'>
                    🤖 Cleudocode
                </h1>
                <p style='color: rgba(255,255,255,0.8); font-size: 1.2rem;'>
                    Personal AI Assistant
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Login card
        with st.container():
            st.markdown("""
                <div style='background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 40px rgba(0,0,0,0.2);'>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🔐 Autenticação Necessária")
            st.markdown("Insira seu token de acesso para continuar.")
            
            # Token input
            token_input = st.text_input(
                "Gateway Token",
                type="password",
                placeholder="Digite seu token aqui...",
                help="Use o comando 'cleudocode dashboard' para obter o token automaticamente"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🚀 Entrar", use_container_width=True, type="primary"):
                    config_manager = get_config_manager()
                    stored_token = config_manager.get_or_create_token()
                    
                    if token_input == stored_token:
                        st.session_state.authenticated = True
                        st.session_state.token = token_input
                        st.success("✅ Autenticado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Token inválido!")
            
            with col_btn2:
                if st.button("📋 Copiar Comando", use_container_width=True):
                    st.code("cleudocode dashboard", language="bash")
                    st.info("Execute este comando no terminal para abrir o dashboard automaticamente")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Help section
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("❓ Como obter o token?"):
            st.markdown("""
                **Método 1: Usar o CLI (Recomendado)**
                ```bash
                cleudocode dashboard
                ```
                Este comando abrirá o dashboard automaticamente com autenticação.
                
                **Método 2: Localizar o token manualmente**
                O token está armazenado em:
                ```
                ~/.cleudocode/.gateway_token
                ```
                
                **Método 3: Gerar novo token**
                ```bash
                cleudocode config reset-token
                ```
            """)
        
        # Footer
        st.markdown("""
            <div style='text-align: center; margin-top: 3rem; color: rgba(255,255,255,0.6);'>
                <p>Cleudocode v1.0.0</p>
                <p>© 2025 Automações Comerciais Integradas</p>
            </div>
        """, unsafe_allow_html=True)


def logout():
    """Logout current user"""
    if "authenticated" in st.session_state:
        del st.session_state.authenticated
    if "token" in st.session_state:
        del st.session_state.token
    st.rerun()


def show_auth_status():
    """Show authentication status in sidebar"""
    if check_authentication():
        with st.sidebar:
            st.success("🔓 Autenticado")
            if st.button("🚪 Sair", use_container_width=True):
                logout()
