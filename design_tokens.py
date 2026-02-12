"""
Cleudocode Design Tokens (Python)
Extraído da landing page em http://localhost:18900/

Uso no Streamlit:
    from design_tokens import COLORS, FONTS, SPACING
    
    st.markdown(f"<h1 style='color: {COLORS['brand']['primary']};'>Título</h1>", 
                unsafe_allow_html=True)
"""

COLORS = {
    "brand": {
        "primary": "#FF5F5F",        # Vermelho Coral
        "secondary": "#6366F1",      # Índigo
        "accent": "#10B981",         # Verde Esmeralda
        "warning": "#FB923C",        # Laranja
    },
    "background": {
        "primary": "#050505",        # Preto Profundo
        "secondary": "#080808",      # Quase Preto
        "tertiary": "#0A0A0A",       
        "elevated": "#111111",       # Grafite Escuro
        "hover": "#161616",
        "active": "#1C1C1C",
    },
    "text": {
        "primary": "#FFFFFF",        # Branco
        "secondary": "#94A3B8",      # Cinza-Azulado
        "tertiary": "#64748B",       # Cinza-Azulado Escuro
        "muted": "#6B7280",          # Cinza Apagado
        "disabled": "rgb(71, 85, 105)",
    },
    "border": {
        "subtle": "rgba(255, 255, 255, 0.05)",
        "default": "rgba(255, 255, 255, 0.1)",
        "strong": "rgba(255, 255, 255, 0.2)",
    },
    "semantic": {
        "success": "#10B981",
        "success_bg": "rgba(16, 185, 129, 0.2)",
        "warning": "#F59E0B",
        "warning_bg": "rgba(245, 158, 11, 0.2)",
        "error": "#EF4444",
        "error_bg": "rgba(239, 68, 68, 0.2)",
        "info": "#6366F1",
        "info_bg": "rgba(99, 102, 241, 0.2)",
    },
    "status": {
        "green": "#34D399",
        "red": "#FF5F5F",
        "blue": "#818CF8",
        "orange": "#FBBF24",
        "purple": "#C084FC",
    }
}

FONTS = {
    "family": {
        "sans": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif",
        "mono": "'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace",
    },
    "size": {
        "xs": "12px",
        "sm": "14px",
        "base": "16px",
        "lg": "18px",
        "xl": "20px",
        "2xl": "24px",
        "3xl": "30px",
        "4xl": "36px",
        "5xl": "48px",
        "6xl": "60px",
        "7xl": "72px",
    },
    "weight": {
        "normal": 400,
        "medium": 500,
        "semibold": 600,
        "bold": 700,
        "extrabold": 800,
        "black": 900,
    },
    "line_height": {
        "tight": 1.25,
        "snug": 1.375,
        "normal": 1.5,
        "relaxed": 1.625,
        "loose": 2,
    },
    "letter_spacing": {
        "tighter": "-0.05em",
        "tight": "-0.025em",
        "normal": "0",
        "wide": "0.025em",
        "wider": "0.05em",
        "widest": "0.1em",
    }
}

SPACING = {
    "0": "0",
    "1": "0.25rem",    # 4px
    "2": "0.5rem",     # 8px
    "3": "0.75rem",    # 12px
    "4": "1rem",       # 16px
    "5": "1.25rem",    # 20px
    "6": "1.5rem",     # 24px
    "8": "2rem",       # 32px
    "10": "2.5rem",    # 40px
    "12": "3rem",      # 48px
    "16": "4rem",      # 64px
    "20": "5rem",      # 80px
    "24": "6rem",      # 96px
}

BORDER_RADIUS = {
    "none": "0",
    "sm": "0.125rem",   # 2px
    "base": "0.25rem",  # 4px
    "md": "0.375rem",   # 6px
    "lg": "0.5rem",     # 8px
    "xl": "0.75rem",    # 12px
    "2xl": "1rem",      # 16px
    "3xl": "1.5rem",    # 24px
    "full": "9999px",
}

SHADOWS = {
    "sm": "0 1px 2px rgba(0, 0, 0, 0.5)",
    "md": "0 4px 6px rgba(0, 0, 0, 0.5)",
    "lg": "0 10px 15px rgba(0, 0, 0, 0.5)",
    "xl": "0 20px 25px rgba(0, 0, 0, 0.5)",
}

TRANSITIONS = {
    "fast": "150ms cubic-bezier(0.4, 0, 0.2, 1)",
    "base": "250ms cubic-bezier(0.4, 0, 0.2, 1)",
    "slow": "350ms cubic-bezier(0.4, 0, 0.2, 1)",
    "slower": "500ms cubic-bezier(0.4, 0, 0.2, 1)",
}

Z_INDEX = {
    "base": 1,
    "dropdown": 1000,
    "sticky": 1100,
    "fixed": 1200,
    "modal_backdrop": 1300,
    "modal": 1400,
    "popover": 1500,
    "tooltip": 1600,
    "notification": 1700,
}


# Helper para gerar CSS do Streamlit
def generate_streamlit_css():
    """
    Gera string CSS para uso no Streamlit st.markdown()
    
    Uso:
        st.markdown(generate_streamlit_css(), unsafe_allow_html=True)
    """
    return f"""
    <style>
        /* === IMPORTAR FONTE INTER === */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        
        /* === VARIÁVEIS CSS === */
        :root {{
            /* Cores da Marca */
            --brand-primary: {COLORS['brand']['primary']};
            --brand-secondary: {COLORS['brand']['secondary']};
            --brand-accent: {COLORS['brand']['accent']};
            --brand-warning: {COLORS['brand']['warning']};
            
            /* Fundos */
            --bg-primary: {COLORS['background']['primary']};
            --bg-secondary: {COLORS['background']['secondary']};
            --bg-elevated: {COLORS['background']['elevated']};
            --bg-hover: {COLORS['background']['hover']};
            --bg-active: {COLORS['background']['active']};
            
            /* Textos */
            --text-primary: {COLORS['text']['primary']};
            --text-secondary: {COLORS['text']['secondary']};
            --text-tertiary: {COLORS['text']['tertiary']};
            --text-muted: {COLORS['text']['muted']};
            
            /* Bordas */
            --border-subtle: {COLORS['border']['subtle']};
            --border-default: {COLORS['border']['default']};
            --border-strong: {COLORS['border']['strong']};
            
            /* Semânticas */
            --color-success: {COLORS['semantic']['success']};
            --color-warning: {COLORS['semantic']['warning']};
            --color-error: {COLORS['semantic']['error']};
            --color-info: {COLORS['semantic']['info']};
            
            /* Fontes */
            --font-sans: {FONTS['family']['sans']};
            --font-mono: {FONTS['family']['mono']};
            
            /* Espaçamento */
            --space-2: {SPACING['2']};
            --space-3: {SPACING['3']};
            --space-4: {SPACING['4']};
            --space-6: {SPACING['6']};
            --space-8: {SPACING['8']};
            
            /* Raio de borda */
            --radius-lg: {BORDER_RADIUS['lg']};
            --radius-xl: {BORDER_RADIUS['xl']};
            --radius-2xl: {BORDER_RADIUS['2xl']};
            --radius-full: {BORDER_RADIUS['full']};
            
            /* Transições */
            --transition-fast: {TRANSITIONS['fast']};
            --transition-base: {TRANSITIONS['base']};
        }}
        
        /* === APLICAR AO APP STREAMLIT === */
        .stApp, [data-testid="stAppViewContainer"] {{
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            font-family: var(--font-sans) !important;
        }}
        
        /* Header */
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
        }}
        
        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: var(--bg-secondary) !important;
            border-right: 1px solid var(--border-subtle) !important;
        }}
        
        /* Textos Gerais */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary) !important;
            font-family: var(--font-sans) !important;
        }}
        
        p, span, div, label {{
            color: var(--text-primary) !important;
        }}
        
        /* Cabeçalhos da Sidebar */
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {{
            color: var(--brand-primary) !important;
            font-size: 0.9rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            margin-top: 1.5rem !important;
            margin-bottom: 0.5rem !important;
            font-weight: 700 !important;
        }}
        
        /* === MENSAGENS DO CHAT === */
        .stChatMessage {{
            background-color: transparent !important;
            border-left: 3px solid transparent !important;
            padding: var(--space-4) !important;
            margin-bottom: var(--space-2) !important;
            border-radius: var(--radius-lg) !important;
            transition: all var(--transition-fast) !important;
        }}
        
        /* Avatar com cor sólida técnica */
        .stChatMessage .stChatMessageAvatar {{
            background: var(--bg-elevated) !important;
            border: 1px solid var(--border-default) !important;
            color: var(--brand-primary) !important;
        }}
        
        /* Mensagens alternadas */
        [data-testid="stChatMessage"]:nth-child(odd) {{
            background-color: #0F0F0F !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-left: 3px solid var(--brand-primary) !important;
        }}
        
        [data-testid="stChatMessage"]:nth-child(even) {{
            background-color: #161616 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-left: 3px solid var(--brand-secondary) !important;
        }}
        
        .stChatMessage:hover {{
            background-color: var(--bg-hover) !important;
        }}
        
        /* === INPUTS & TEXTAREAS === */
        .stTextInput input, 
        .stTextArea textarea, 
        .stSelectbox div[data-baseweb="select"] {{
            background-color: rgba(255, 255, 255, 0.03) !important;
            color: var(--text-primary) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: var(--radius-lg) !important;
            font-family: var(--font-sans) !important;
            transition: all var(--transition-fast) !important;
        }}
        
        .stTextInput input:focus,
        .stTextArea textarea:focus {{
            border-color: var(--brand-primary) !important;
            box-shadow: 0 0 0 2px rgba(255, 95, 95, 0.2) !important;
        }}
        
        /* Placeholder */
        ::placeholder {{
            color: var(--text-muted) !important;
        }}
        
        /* === BOTÕES === */
        .stButton button[kind="primary"], 
        .stButton button[type="primary"],
        .stButton > button:first-child:not([kind]) {{
            background-color: var(--brand-primary) !important;
            color: var(--text-primary) !important;
            border: none !important;
            border-radius: var(--radius-lg) !important;
            font-weight: {FONTS['weight']['semibold']} !important;
            font-family: var(--font-sans) !important;
            padding: var(--space-3) var(--space-6) !important;
            transition: all var(--transition-fast) !important;
        }}
        
        .stButton button[kind="primary"]:hover,
        .stButton > button:first-child:not([kind]):hover {{
            background-color: #ff7a7a !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 15px rgba(255, 95, 95, 0.4) !important;
        }}
        
        .stButton button[kind="secondary"] {{
            background-color: var(--bg-hover) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-default) !important;
            border-radius: var(--radius-lg) !important;
            font-weight: {FONTS['weight']['medium']} !important;
            transition: all var(--transition-fast) !important;
        }}
        
        .stButton button[kind="secondary"]:hover {{
            background-color: var(--bg-active) !important;
            border-color: var(--border-strong) !important;
        }}
        
        /* === TABS (Estilo Terminal Window) === */
        .stTabs [data-baseweb="tab-list"] {{
            gap: var(--space-4);
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-bottom: none;
            border-radius: var(--radius-xl) var(--radius-xl) 0 0;
            padding: var(--space-2) var(--space-6);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent !important;
            color: var(--text-tertiary) !important;
            font-family: var(--font-mono) !important;
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            transition: all var(--transition-fast) !important;
            border-bottom: 2px solid transparent !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            color: var(--brand-primary) !important;
            border-bottom: 2px solid var(--brand-primary) !important;
        }}
        
        /* === EXPANDER === */
        .streamlit-expanderHeader {{
            background-color: var(--bg-elevated) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-lg) !important;
            font-family: var(--font-sans) !important;
        }}
        
        .streamlit-expanderHeader:hover {{
            background-color: var(--bg-hover) !important;
            border-color: var(--border-default) !important;
        }}
        
        /* === FILE UPLOADER === */
        [data-testid="stFileUploader"] {{
            background-color: var(--bg-elevated) !important;
            border: 2px dashed var(--border-default) !important;
            border-radius: var(--radius-xl) !important;
            padding: var(--space-6) !important;
        }}
        
        [data-testid="stFileUploader"]:hover {{
            border-color: var(--brand-primary) !important;
            background-color: var(--bg-hover) !important;
        }}
        
        /* === SLIDER === */
        .stSlider [data-baseweb="slider"] [role="slider"] {{
            background-color: var(--brand-primary) !important;
        }}
        
        .stSlider [data-baseweb="slider"] > div > div {{
            background-color: var(--brand-primary) !important;
        }}
        
        /* === CHECKBOX & RADIO === */
        .stCheckbox label, .stRadio label {{
            font-family: var(--font-sans) !important;
        }}
        
        /* === SPINNER === */
        .stSpinner > div {{
            border-top-color: var(--brand-primary) !important;
        }}
        
        /* === SUCCESS/WARNING/ERROR/INFO === */
        .stSuccess {{
            background-color: var(--color-success-bg) !important;
            color: var(--color-success) !important;
            border-left: 4px solid var(--color-success) !important;
        }}
        
        .stWarning {{
            background-color: var(--color-warning-bg) !important;
            color: var(--color-warning) !important;
            border-left: 4px solid var(--color-warning) !important;
        }}
        
        .stError {{
            background-color: var(--color-error-bg) !important;
            color: var(--color-error) !important;
            border-left: 4px solid var(--color-error) !important;
        }}
        
        .stInfo {{
            background-color: var(--color-info-bg) !important;
            color: var(--color-info) !important;
            border-left: 4px solid var(--color-info) !important;
        }}
    </style>
    """


# Estilos específicos de componentes
COMPONENT_STYLES = {
    "hero_heading": {
        "font-family": FONTS['family']['sans'],
        "font-size": FONTS['size']['7xl'],
        "font-weight": FONTS['weight']['black'],
        "font-style": "italic",
        "color": COLORS['text']['primary'],
        "letter-spacing": "-3.6px",
        "line-height": "1.1",
    },
    "hero_tagline": {
        "font-family": FONTS['family']['sans'],
        "font-size": FONTS['size']['xl'],
        "font-weight": FONTS['weight']['medium'],
        "color": COLORS['brand']['primary'],
        "text-transform": "uppercase",
        "letter-spacing": FONTS['letter_spacing']['wide'],
    },
    "body_text": {
        "font-family": FONTS['family']['sans'],
        "font-size": FONTS['size']['xl'],
        "font-weight": FONTS['weight']['medium'],
        "color": COLORS['text']['secondary'],
        "line-height": FONTS['line_height']['relaxed'],
    },
    "card": {
        "background": COLORS['background']['elevated'],
        "border": f"1px solid {COLORS['border']['subtle']}",
        "border-radius": BORDER_RADIUS['2xl'],
        "padding": SPACING['6'],
    },
    "icon_circle": {
        "background": COLORS['brand']['primary'],
        "border-radius": BORDER_RADIUS['full'],
        "color": COLORS['text']['primary'],
    }
}
