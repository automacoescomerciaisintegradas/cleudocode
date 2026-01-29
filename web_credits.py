import streamlit as st
import pandas as pd
import json
import os

# Configuração da página para manter a estética Dark/Premium do Intelyze
st.set_page_config(page_title="Intelyze Clone - Sistema de Créditos", layout="wide")

# Estilo Customizado (CSS) para simular o Dark Mode Premium
st.markdown("""
    <style>
    .main {
        background-color: #0d1117;
        color: white;
    }
    .stButton>button {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(106, 17, 203, 0.5);
    }
    .price-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .price-value {
        font-size: 24px;
        font-weight: bold;
        color: #58a6ff;
    }
    .cost-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_stdio=True)

# Dados de Precificação (Extraídos via Agente de Navegação)
PRICING_DATA = {
    "Publicação no Instagram": 0.27,
    "Resposta Pública": 0.09,
    "Resposta Privada": 0.09,
    "Envio para Telegram": 0.09,
    "Consulta Shopee (50 produtos)": 0.09,
    "Envio para WooCommerce": 0.27
}

RECHARGE_PLANS = {
    "Starter": 197.00,
    "Professional": 499.00,
    "Scale": 999.00,
    "Enterprise": 1999.00
}

def credits_screen():
    st.title("💎 Gerenciamento de Créditos")
    st.write("Controle seu saldo e recarregue para continuar suas automações.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Planos de Recarga")
        p_cols = st.columns(len(RECHARGE_PLANS))
        for i, (name, price) in enumerate(RECHARGE_PLANS.items()):
            with p_cols[i]:
                st.markdown(f"""
                <div class="price-card">
                    <h4>{name}</h4>
                    <div class="price-value">R$ {price:,.2f}</div>
                    <p style="color: #8b949e; font-size: 12px; margin-top: 10px;">Saldo Integral em Créditos</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Comprar {name}", key=f"btn_{name}"):
                    st.success(f"Simulando transação para {name}...")

        st.subheader("📊 Tabela de Custos por Execução")
        df_costs = pd.DataFrame(list(PRICING_DATA.items()), columns=["Ação", "Custo (R$)"])
        st.table(df_costs)

    with col2:
        st.subheader("💳 Seu Saldo")
        # Simulando um saldo inicial
        if 'balance' not in st.session_state:
            st.session_state.balance = 50.00
        
        st.metric(label="Saldo Disponível", value=f"R$ {st.session_state.balance:,.2f}")
        
        st.write("---")
        st.subheader("🚀 Simulador de Uso")
        selected_action = st.selectbox("Escolha uma ação para simular", list(PRICING_DATA.keys()))
        qty = st.number_input("Quantidade", min_value=1, value=10)
        
        total_cost = PRICING_DATA[selected_action] * qty
        st.warning(f"Custo Estimado: R$ {total_cost:,.2f}")
        
        if st.button("Simular Execução"):
            if st.session_state.balance >= total_cost:
                st.session_state.balance -= total_cost
                st.balloons()
                st.success(f"Executado com sucesso! Novo saldo: R$ {st.session_state.balance:,.2f}")
            else:
                st.error("Saldo insuficiente para esta operação.")

# Para rodar basta adicionar credits_screen() ao seu app principal ou rodar este arquivo
if __name__ == "__main__":
    credits_screen()
