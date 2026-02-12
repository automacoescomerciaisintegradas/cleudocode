#!/usr/bin/env python3
"""
Menu Interativo para o Agente de Vendas Shopee com base no conceito de Flywheel Master
"""
import requests
from core.config import settings

class ShopeeMenu:
    def __init__(self):
        self.bot_token = settings.get("TELEGRAM_BOT_TOKEN")
        
    def get_main_menu(self):
        """Retorna o menu principal com as opções do DANNET MASTER"""
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🔍 Consultar Produtos", "callback_data": "consultar_produtos"},
                    {"text": "🔗 Gerar Link Afiliado", "callback_data": "gerar_link_afiliado"}
                ],
                [
                    {"text": "✨ Gerar Mensagem IA", "callback_data": "gerar_mensagem_ia"},
                    {"text": "🚚 Simular Frete", "callback_data": "simular_frete"}
                ],
                [
                    {"text": "💳 Formas de Pagamento", "callback_data": "formas_pagamento"},
                    {"text": "🔄 Política de Trocas", "callback_data": "politica_trocas"}
                ],
                [
                    {"text": "🔄 Ciclo de Crescimento", "callback_data": "flywheel_concept"},
                    {"text": "📚 Estudos de Caso", "callback_data": "estudos_caso"}
                ],
                [
                    {"text": "🏆 Cases de Sucesso", "callback_data": "cases_sucesso"},
                    {"text": "💡 Recomendar Produtos", "callback_data": "recomendar_produtos"}
                ],
                [
                    {"text": "⭐ Avaliações", "callback_data": "avaliacoes"},
                    {"text": "🎁 Promoções", "callback_data": "promocoes"}
                ]
            ]
        }
        return keyboard
    
    def get_flywheel_submenu(self):
        """Retorna submenu sobre o conceito de Flywheel"""
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Amazon", "callback_data": "caso_amazon"},
                    {"text": "Apple", "callback_data": "caso_apple"}
                ],
                [
                    {"text": "Netflix", "callback_data": "caso_netflix"},
                    {"text": "Outros", "callback_data": "outros_casos"}
                ],
                [
                    {"text": "Voltar ao Menu", "callback_data": "voltar_menu"}
                ]
            ]
        }
        return keyboard
    
    def get_product_submenu(self):
        """Retorna submenu para consulta de produtos"""
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Promoções", "callback_data": "prod_promocoes"},
                    {"text": "Mais Vendidos", "callback_data": "prod_mais_vendidos"}
                ],
                [
                    {"text": "Novidades", "callback_data": "prod_novidades"},
                    {"text": "Por Categoria", "callback_data": "prod_categoria"}
                ],
                [
                    {"text": "Voltar ao Menu", "callback_data": "voltar_menu"}
                ]
            ]
        }
        return keyboard

def enviar_menu_principal(chat_id):
    """Envia o menu principal para o usuário"""
    bot_token = settings.get("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado")
        return False
    
    try:
        menu = ShopeeMenu()
        keyboard = menu.get_main_menu()
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": """🤖 **DANNET MASTER** - Agente de Vendas Avançado da **F.C.A. DE QUEIROZ ("Automações Comerciais Integradas" ou "ACI")**! 🚀

Sou seu assistente especializado em vendas e ciclos de crescimento. Posso te ajudar com:

🔍 *Consulta de Produtos* - Encontre exatamente o que procura
🔗 *Geração de Links de Afiliado* - Crie links personalizados para ganhar comissão
✨ *Mensagens com IA* - Gere mensagens promocionais otimizadas
🚚 *Simulação de Frete* - Calcule prazo e valor de entrega
💳 *Formas de Pagamento* - Condições especiais para você
🔄 *Ciclo de Crescimento* - Entenda como nosso modelo gera valor
📚 *Estudos de Caso* - Cases de sucesso de grandes empresas
🏆 *Cases de Sucesso* - Como outros clientes tiveram bons resultados

Empresa: F.C.A. DE QUEIROZ ("Automações Comerciais Integradas" ou "ACI")
Telefone: +55 88 921567214

Selecione uma opção abaixo:""",
            "parse_mode": "Markdown",
            "reply_markup": keyboard
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print(f"✅ Menu principal DANNET MASTER enviado com sucesso para {chat_id}")
                return True
            else:
                print(f"❌ Erro ao enviar menu: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Falha ao enviar menu: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar menu: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Módulo de Menu Interativo do Agente de Vendas Shopee - FLYWHEEL MASTER")
    print("Este módulo pode ser integrado ao seu sistema de atendimento")