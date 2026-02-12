"""
Cleudocode Design Tokens (Python)
Extracted from the landing page at http://localhost:18900/

Usage in Streamlit:
    from design_tokens import COLORS, FONTS, SPACING
    
    st.markdown(f"<h1 style='color: {COLORS['brand']['primary']};'>Title</h1>", 
                unsafe_allow_html=True)
"""

COLORS = {
    "brand": {
        "primary": "#FF5F5F",        # Coral/Salmon Red
        "secondary": "#6366F1",      # Indigo
        "accent": "#10B981",         # Emerald Green
        "warning": "#FB923C",        # Orange
    },
    "background": {
        "primary": "#080808",        # Almost Black
        "secondary": "#0A0A0A",      # Very Dark Gray
        "tertiary": "rgb(15, 22, 41)",  # Dark Blue-Gray
        "elevated": "rgba(255, 255, 255, 0.02)",
        "hover": "rgba(255, 255, 255, 0.05)",
        "active": "rgba(255, 255, 255, 0.08)",
    },
    "text": {
        "primary": "#FFFFFF",        # White
        "secondary": "#94A3B8",      # Gray-Blue
        "tertiary": "#64748B",       # Darker Gray-Blue
        "muted": "#6B7280",          # Muted Gray
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


# Streamlit CSS Helper
def generate_streamlit_css():
    """
    Generate CSS string for use in Streamlit st.markdown()
    
    Usage:
        st.markdown(generate_streamlit_css(), unsafe_allow_html=True)
    """
    return f"""
    <style>
        :root {{
            /* Brand Colors */
            --brand-primary: {COLORS['brand']['primary']};
            --brand-secondary: {COLORS['brand']['secondary']};
            --brand-accent: {COLORS['brand']['accent']};
            
            /* Backgrounds */
            --bg-primary: {COLORS['background']['primary']};
            --bg-secondary: {COLORS['background']['secondary']};
            --bg-elevated: {COLORS['background']['elevated']};
            --bg-hover: {COLORS['background']['hover']};
            
            /* Text */
            --text-primary: {COLORS['text']['primary']};
            --text-secondary: {COLORS['text']['secondary']};
            --text-tertiary: {COLORS['text']['tertiary']};
            
            /* Fonts */
            --font-sans: {FONTS['family']['sans']};
            --font-mono: {FONTS['family']['mono']};
        }}
        
        /* Apply to Streamlit app */
        .stApp {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-sans);
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary);
            font-family: var(--font-sans);
        }}
        
        /* Buttons */
        .stButton button {{
            background-color: var(--brand-primary);
            color: var(--text-primary);
            border: none;
            border-radius: {BORDER_RADIUS['lg']};
            font-weight: {FONTS['weight']['semibold']};
            transition: {TRANSITIONS['fast']};
        }}
        
        .stButton button:hover {{
            background-color: #ff7a7a;
            transform: translateY(-1px);
        }}
    </style>
    """


# Component-specific styles
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
