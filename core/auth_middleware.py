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
    try:
        from design_tokens import COLORS, FONTS, BORDER_RADIUS, SHADOWS
        brand_primary = COLORS['brand']['primary']
        bg_primary = COLORS['background']['primary']
        text_primary = COLORS['text']['primary']
        font_sans = FONTS['family']['sans']
    except ImportError:
        brand_primary = "#FF5F5F"
        bg_primary = "#050505"
        text_primary = "#FFFFFF"
        font_sans = "Inter, sans-serif"

    st.set_page_config(
        page_title="Cleudocode - Mission Control",
        page_icon="🤖",
        layout="centered"
    )
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {bg_primary} !important;
            font-family: {font_sans} !important;
        }}
        .login-card {{
            background: #080808 !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            padding: 3rem !important;
            border-radius: 24px !important;
            box-shadow: 0 30px 60px rgba(0,0,0,0.8) !important;
        }}
        .brand-logo {{
            color: white !important;
            font-family: {font_sans} !important;
            font-weight: 800 !important;
            font-style: italic !important;
            font-size: 4.5rem !important;
            letter-spacing: -2px !important;
            line-height: 1 !important;
            text-transform: uppercase !important;
            margin-bottom: 1rem !important;
            text-align: center;
        }}
        .tagline {{
            color: {brand_primary} !important;
            font-family: {font_sans} !important;
            font-size: 0.75rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 4px !important;
            text-align: center;
            margin-bottom: 3rem !important;
        }}
        .stButton button[kind="primary"] {{
            background-color: {brand_primary} !important;
            height: 3rem !important;
        }}
        .stTextInput input {{
            background-color: #111 !important;
            border: 1px solid #222 !important;
            height: 3.5rem !important;
            text-align: center !important;
            font-size: 1.2rem !important;
            border-radius: 12px !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Logo Area
    st.markdown("<div class='brand-logo'>CLEUDOCODE</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #FF5F5F; text-align: center; font-family: Inter; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 6px; margin-bottom: 4rem;'>THE AI THAT ACTUALLY DOES THINGS.</div>", unsafe_allow_html=True)
    
    # Login card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("<div class='login-card'>", unsafe_allow_html=True)
            
            st.markdown(f"<h3 style='text-align: center; color: white; margin-bottom: 0.5rem; font-family: Inter; letter-spacing: 1px;'>🔐 Autenticação</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #888; margin-bottom: 2rem; font-size: 0.9rem;'>Insira seu token de acesso para continuar.</p>", unsafe_allow_html=True)
            
            token_input = st.text_input(
                "Gateway Token",
                type="password",
                placeholder="Insira seu token...",
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("INICIAR SESSÃO", use_container_width=True, type="primary"):
                config_manager = get_config_manager()
                stored_token = config_manager.get_or_create_token()
                
                if token_input == stored_token:
                    st.session_state.authenticated = True
                    st.session_state.token = token_input
                    st.success("SESSÃO VALIDADA")
                    st.rerun()
                else:
                    st.error("ACESSO NEGADO: TOKEN INVÁLIDO")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Help Section
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("❓ Precisa de ajuda?"):
            st.markdown(f"""
                <div style='color: #888; font-size: 0.9rem;'>
                Para acessar o sistema sem digitar o token manualmente, execute no seu terminal:
                <br><br>
                <code style='color: #FF5F5F; background: rgba(255,95,95,0.1); padding: 4px 8px; border-radius: 4px;'>cleudocode dashboard</code>
                <br><br>
                O dashboard será aberto no seu navegador já autenticado.
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='text-align: center; margin-top: 4rem; color: #333; font-family: {font_sans}; font-size: 0.7rem; letter-spacing: 1px;'>
                © 2026 Automações Comerciais Integradas<br>
                V 2.0.0 - Mission Control Agent
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
        try:
            from design_tokens import COLORS, BORDER_RADIUS, SPACING
            brand_primary = COLORS['brand']['primary']
            bg_elevated = COLORS['background']['elevated']
            radius_lg = BORDER_RADIUS['lg']
            space_2 = SPACING['2']
        except ImportError:
            brand_primary = "#FF5F5F"
            bg_elevated = "rgba(255, 255, 255, 0.05)"
            radius_lg = "0.5rem"
            space_2 = "0.5rem"

        with st.sidebar:
            st.markdown(f"""
                <div style='
                    background: {bg_elevated};
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-left: 3px solid #10B981;
                    padding: {space_2} 1rem;
                    border-radius: {radius_lg};
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                '>
                    <span style='color: #10B981;'>●</span>
                    <span style='color: white; font-size: 0.9rem; font-weight: 500;'>Sistema Autenticado</span>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Encerrar Sessão", use_container_width=True):
                logout()
