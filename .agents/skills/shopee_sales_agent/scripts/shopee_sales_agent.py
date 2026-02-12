#!/usr/bin/env python3
"""
Agente de Vendas Shopee - Responde automaticamente às mensagens dos clientes no Telegram
"""
import os
import requests
import json
from datetime import datetime
from core.config import settings

class ShopeeSalesAgent:
    def __init__(self):
        self.bot_token = settings.get("TELEGRAM_BOT_TOKEN")
        self.name = "Shopee Sales Agent"
        self.description = "Agente de vendas para afiliados da Shopee que responde automaticamente às mensagens dos clientes no Telegram"
        
    def responder_mensagem(self, mensagem_cliente, chat_id):
        """
        Processa a mensagem do cliente e retorna uma resposta apropriada
        """
        mensagem_cliente_lower = mensagem_cliente.lower()
        
        # Determinar o tipo de mensagem
        if any(palavra in mensagem_cliente_lower for palavra in ['ola', 'oi', 'olá', 'oi tudo bem', 'bom dia', 'boa tarde', 'boa noite']):
            return self.resposta_saudacao()
        elif any(palavra in mensagem_cliente_lower for palavra in ['produto', 'quero comprar', 'tem', 'disponível', 'estoque', 'valor', 'preço', 'promoção']):
            return self.resposta_consulta_produto(mensagem_cliente)
        elif any(palavra in mensagem_cliente_lower for palavra in ['frete', 'entrega', 'prazo', 'chega', 'envio', 'cep']):
            return self.resposta_frete_entrega()
        elif any(palavra in mensagem_cliente_lower for palavra in ['pagamento', 'cartão', 'pix', 'boleto', 'parcelamento', 'dinheiro']):
            return self.resposta_pagamento()
        elif any(palavra in mensagem_cliente_lower for palavra in ['troca', 'devolução', 'problema', 'defeito', 'arrependimento']):
            return self.resposta_troca_devolucao()
        elif any(palavra in mensagem_cliente_lower for palavra in ['obrigado', 'vlw', 'agradeço', 'ótimo']):
            return self.resposta_agradecimento()
        else:
            # Para mensagens genéricas ou dúvidas
            return self.resposta_padrao(mensagem_cliente)
    
    def resposta_saudacao(self):
        """Resposta para saudações"""
        hora_atual = datetime.now().hour
        
        if hora_atual < 12:
            periodo = "Bom dia"
        elif hora_atual < 18:
            periodo = "Boa tarde"
        else:
            periodo = "Boa noite"
        
        return f"""{periodo}! 👋 

Olá! Sou seu assistente virtual da loja Shopee e estou aqui para ajudar. 

✨ Comigo você pode:
• Consultar produtos disponíveis
• Tirar dúvidas sobre frete e entrega
• Obter informações sobre pagamento
• Receber recomendações personalizadas

Tem interesse em algum produto específico ou gostaria de ver nossas promoções de hoje? 🛒"""
    
    def resposta_consulta_produto(self, mensagem_original):
        """Resposta para consultas de produto"""
        return f"""Interessante sua consulta sobre produtos! 🕵️‍♂️

A maioria dos produtos que divulgamos tem excelente avaliação dos nossos clientes. Para te ajudar melhor, posso providenciar:

📦 Informações detalhadas sobre o produto
🚚 Simulação de frete e prazo
💳 Opções de pagamento e parcelamento
⭐ Avaliações reais de outros compradores

Se quiser, posso te enviar o link direto para a compra com o melhor preço do dia! 

Qual produto específico você gostaria de saber mais?"""
    
    def resposta_frete_entrega(self):
        """Resposta para dúvidas de frete e entrega"""
        return f"""🚚 Sobre frete e entrega:

✅ Entregas em todo Brasil
⏱️ Prazos de 3 a 10 dias úteis (calculado automaticamente por CEP)
🔍 Acompanhamento com código de rastreio
📦 Em muitos casos, opções de entrega mais rápidas disponíveis

Após a confirmação do pagamento, você recebe o código de rastreio para acompanhar sua compra em tempo real. 

Quer simular o frete para algum produto específico?"""
    
    def resposta_pagamento(self):
        """Resposta para dúvidas de pagamento"""
        return f"""💳 Sobre formas de pagamento:

✅ Aceitamos PIX (à vista com desconto)
✅ Cartões de crédito (até 12x sem juros em muitos produtos)
✅ Cartões de débito
✅ Boleto bancário (à vista)

Segurança garantida pela plataforma Shopee com proteção ao comprador. 

As condições exatas de parcelamento variam por produto. Posso te informar as opções específicas para o produto que você tem interesse."""
    
    def resposta_troca_devolucao(self):
        """Resposta para dúvidas de troca/devolução"""
        return f"""↩️ Política de troca e devolução:

🔄 7 dias para desistência (direito de arrependimento)
🛡️ Garantia do fabricante conforme descrição do produto
📋 Processo simplificado de troca
😊 Atendimento ao cliente ágil para resolver qualquer problema

A plataforma Shopee oferece proteção total ao comprador. 

Se tiver algum problema com sua compra, estaremos aqui para resolver da melhor forma!"""
    
    def resposta_agradecimento(self):
        """Resposta para agradecimentos"""
        return f"""😊 Agradeço seu contato!

Se precisar de mais alguma informação, estarei sempre à disposição. 

Não se esqueça de conferir nossas promoções diárias e seguir nossos canais para as melhores ofertas! 🛍️"""
    
    def resposta_padrao(self, mensagem_original):
        """Resposta padrão para mensagens genéricas"""
        return f"""🤖 Recebi sua mensagem: "{mensagem_original}"

Sou um assistente virtual especializado em vendas da Shopee e posso te ajudar com:

📦 Informações sobre produtos
🚚 Detalhes de frete e entrega  
💳 Opções de pagamento
🔄 Política de trocas
💡 Recomendações personalizadas

Se quiser saber mais sobre algum produto específico, basta mencionar o nome ou características do que procura. 

Também posso te recomendar produtos com base no que você está buscando!"""
    
    def enviar_resposta(self, chat_id, mensagem):
        """Envia a resposta para o cliente via Telegram"""
        if not self.bot_token:
            print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": mensagem,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    print(f"✅ Resposta enviada com sucesso para {chat_id}")
                    return True
                else:
                    print(f"❌ Erro ao enviar resposta: {data.get('description', 'Erro desconhecido')}")
                    return False
            else:
                print(f"❌ Falha ao enviar resposta: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao enviar resposta: {e}")
            return False

def processar_mensagem_entrada(message_data):
    """
    Função que processa a mensagem recebida e envia resposta automaticamente
    """
    # Extrair informações da mensagem
    message = message_data.get('message', {})
    chat = message.get('chat', {})
    chat_id = chat.get('id')
    text = message.get('text', '')
    
    if not text:
        # Pode ser uma mensagem de outro tipo (imagem, etc)
        return {"success": True, "message": "Mensagem não textual recebida"}
    
    # Criar instância do agente
    agent = ShopeeSalesAgent()
    
    # Gerar resposta
    resposta = agent.responder_mensagem(text, chat_id)
    
    # Enviar resposta
    sucesso = agent.enviar_resposta(chat_id, resposta)
    
    if sucesso:
        return {"success": True, "message": f"Resposta enviada para {chat_id}"}
    else:
        return {"success": False, "message": f"Falha ao enviar resposta para {chat_id}"}

if __name__ == "__main__":
    print("🤖 Agente de Vendas Shopee - Pronto para atender clientes!")
    print("Este módulo pode ser integrado ao seu sistema de mensagens do Telegram")