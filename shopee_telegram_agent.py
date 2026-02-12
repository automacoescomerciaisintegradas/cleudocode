#!/usr/bin/env python3
"""
Agente de Vendas Shopee - Sistema 24/7 para responder clientes no Telegram
Este script ativa o agente que responderá automaticamente às mensagens dos clientes
com base nas políticas e informações de vendas da Shopee.
"""
import time
import requests
import json
from datetime import datetime
import sys
import os

# Adicionar o caminho para importar os módulos necessários
sys.path.append('/root/cleudocode')

from core.config import settings

class ShopeeSalesAgent:
    def __init__(self):
        self.bot_token = settings.get("TELEGRAM_BOT_TOKEN")
        self.name = "DANNET MASTER"
        self.description = "DANNET MASTER - Agente de vendas avançado da F.C.A. DE QUEIROZ (Automações Comerciais Integradas) para afiliados da Shopee que responde automaticamente às mensagens dos clientes no Telegram"
        
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
        elif any(palavra in mensagem_cliente_lower for palavra in ['flywheel', 'roda', 'crescimento', 'ciclo', 'virtuoso']):
            return self.resposta_flywheel()
        elif any(palavra in mensagem_cliente_lower for palavra in ['estudo', 'caso', 'sucesso', 'amazon', 'apple', 'netflix']):
            return self.resposta_estudos_caso()
        elif any(palavra in mensagem_cliente_lower for palavra in ['link', 'afiliado', 'gerar link', 'shopee link']):
            return self.resposta_gerar_link_afiliado()
        elif any(palavra in mensagem_cliente_lower for palavra in ['mensagem', 'promocional', 'gerar mensagem', 'ia']):
            return self.resposta_gerar_mensagem_ia()
        elif any(palavra in mensagem_cliente_lower for palavra in ['dannet', 'master', 'aci']):
            return self.resposta_apresentacao_dannet()
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
        
        return f"""🤖 {periodo}! 👋 

Olá! Sou o **DANNET MASTER**, seu assistente avançado de vendas da **F.C.A. DE QUEIROZ ("Automações Comerciais Integradas" ou "ACI")**! 

✨ Comigo você pode:
• Consultar produtos disponíveis
• Tirar dúvidas sobre frete e entrega
• Obter informações sobre pagamento
• Receber recomendações personalizadas
• Gerar links de afiliado
• Criar mensagens promocionais com IA
• Enviar ofertas diretamente para o Telegram

Tem interesse em algum produto específico ou gostaria de gerar uma oferta? 😊"""
    
    def resposta_consulta_produto(self, mensagem_original):
        """Resposta para consultas de produto"""
        return f"""🔍 Interessante sua consulta sobre produtos! 

Nosso sistema de recomendação inteligente identificou que você pode se interessar por produtos com alta taxa de conversão e excelentes avaliações. Isso faz parte do nosso ciclo de crescimento (Flywheel Effect) - recomendamos produtos que você ama, você se torna um cliente satisfeito, e sua recomendação atrai mais pessoas para nossa comunidade!

📊 Sobre o produto que você consultou:

📦 Informações detalhadas e transparentes
🚚 Simulação de frete e prazo em tempo real
💳 Opções de pagamento flexíveis
⭐ Avaliações reais de outros compradores felizes
🔄 Produtos complementares que você pode amar

Ao comprar conosco, você faz parte de um ciclo virtuoso: sua satisfação gera recomendações, que trazem mais clientes, que permitem melhores negociações com fornecedores, que resultam em preços ainda melhores para você!

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

Se tiver algum problema com sua compra, estarei aqui para resolver da melhor forma!"""
    
    def resposta_agradecimento(self):
        """Resposta para agradecimentos"""
        return f"""😊 Agradeço seu contato!

Se precisar de mais alguma informação, estarei sempre à disposição. 

Não se esqueça de conferir nossas promoções diárias e seguir nossos canais para as melhores ofertas! 🛍️"""
    
    def resposta_padrao(self, mensagem_original):
        """Resposta padrão para mensagens genéricas"""
        return f"""🤖 Recebi sua mensagem: "{mensagem_original}"

Sou o **DANNET MASTER**, um assistente avançado de vendas da **ACI Automacoes Comerciais Integradas** guiado pelo conceito de "Flywheel Effect" - ciclos virtuosos de crescimento. Isso significa que cada cliente satisfeito gera mais clientes, criando um ciclo sustentável de crescimento!

👨‍💼 Posso te ajudar com:

📦 Informações sobre produtos
🚚 Detalhes de frete e entrega  
💳 Opções de pagamento
🔄 Política de trocas
💡 Recomendações personalizadas
🔗 Geração de links de afiliado
✨ Criação de mensagens promocionais com IA
📈 Estudos de caso de sucesso
🎯 Ciclo de crescimento (atração → conversão → retenção → advocacia)

Se quiser saber mais sobre algum produto específico, basta mencionar o nome ou características do que procura. 

Também posso te recomendar produtos com base no que você está buscando!"""

    def resposta_gerar_link_afiliado(self):
        """Resposta sobre geração de links de afiliado"""
        return f"""🔗 **GERADOR DE LINKS DE AFILIADO SHOPEE** - DANNET MASTER

O DANNET MASTER pode gerar links de afiliado personalizados para produtos da Shopee! 

✨ **Como funciona:**
1. Envie-me o link original do produto Shopee
2. Eu criarei um link personalizado com seu ID de afiliado
3. Cada compra realizada através do seu link gera comissão para você!

💰 **Benefícios:**
- Ganhe comissão em cada venda
- Links personalizados e profissionais
- Acompanhamento de desempenho
- Integração direta com a API da Shopee

Para gerar um link de afiliado, basta me enviar o link do produto Shopee que deseja promover!"""

    def resposta_gerar_mensagem_ia(self):
        """Resposta sobre geração de mensagens com IA"""
        return f"""✨ **GERADOR DE MENSAGENS PROMOCIONAIS COM IA** - DANNET MASTER

O DANNET MASTER utiliza inteligência artificial avançada para criar mensagens promocionais otimizadas para conversão!

🎯 **Características das mensagens geradas:**
- Personalizadas para cada produto
- Otimizadas para conversão
- Baseadas em técnicas de marketing digital
- Com chamadas para ação eficazes
- Formato ideal para redes sociais

🤖 **Como funciona:**
1. Envie-me o link do produto Shopee
2. Eu analisarei as características do produto
3. Gerei uma mensagem persuasiva com IA
4. A mensagem estará pronta para ser usada em seus canais

Para gerar uma mensagem promocional com IA, basta me enviar o link do produto Shopee!"""

    def resposta_apresentacao_dannet(self):
        """Resposta sobre o DANNET MASTER"""
        return f"""🤖 **DANNET MASTER** - Agente de Vendas Avançado da **F.C.A. DE QUEIROZ ("Automações Comerciais Integradas" ou "ACI")**

Sou um assistente especializado em vendas de produtos Shopee com funcionalidades avançadas:

🔗 **Geração de Links de Afiliado**
- Criação automática de links personalizados
- Integração com API da Shopee
- Acompanhamento de desempenho

✨ **Criação de Mensagens com IA**
- Mensagens promocionais otimizadas
- Baseadas em características do produto
- Técnicas de marketing digital

🔄 **Ciclo de Crescimento (Flywheel Effect)**
- Atração → Conversão → Retenção → Advocacia
- Modelos de negócios baseados em ciclos virtuosos
- Estudos de caso de empresas de sucesso

📊 **Análise e Recomendação**
- Sugestões baseadas em dados
- Produtos com alta taxa de conversão
- Estratégias de posicionamento

📞 **Contato**
- Empresa: F.C.A. DE QUEIROZ ("Automações Comerciais Integradas" ou "ACI")
- Telefone: +55 88 921567214

Sou seu parceiro completo para vendas de produtos Shopee!"""
    
    def resposta_flywheel(self):
        """Resposta sobre o conceito de Flywheel Effect"""
        return f"""👨‍💼 Ah, você se interessou pelo nosso modelo de "Flywheel Effect" (Roda de Crescimento)! 

Este é um conceito poderoso usado por empresas de sucesso como Amazon, Apple e Netflix:

🔄 **Nossa Roda de Crescimento:**
1. **Atração**: Destacamos produtos com alta taxa de conversão
2. **Conversão**: Fornecemos informações completas e transparentes
3. **Retenção**: Oferecemos suporte pós-venda e produtos complementares
4. **Advocacia**: Incentivamos avaliações e recomendações

💡 **Exemplo Prático:**
Ao comprar conosco, você faz parte deste ciclo virtuoso: sua satisfação gera recomendações, que trazem mais clientes, que permitem melhores negociações com fornecedores, que resultam em preços ainda melhores para você!

Quer que eu te mostre produtos que se encaixam nesse modelo de excelência?"""
    
    def resposta_estudos_caso(self):
        """Resposta sobre estudos de caso de sucesso"""
        return f"""📚 **Estudos de Caso de Sucesso no Modelo Flywheel**:

🔍 **Amazon**:
Foco no cliente → Recomendações → Mais escala → Custos reduzidos → Melhor preço/oferta

📱 **Apple**:
Excelência no produto → Lealdade do cliente → Mais vendas → Financia inovação contínua

📺 **Netflix**:
Conteúdo de qualidade → Assinantes fiéis → Mais receita → Mais produção → Mais assinantes

🎯 **Como isso se aplica a você**:
Ao comprar conosco, você experimenta esse modelo: produtos de qualidade → satisfação → recomendações → mais variedade → preços melhores!

Quer que eu te mostre como aplicamos esses princípios na prática com os produtos que vendemos?"""
    
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

class ShopeeTelegramService:
    def __init__(self):
        self.bot_token = settings.get("TELEGRAM_BOT_TOKEN")
        self.last_update_id = 0
        self.agent = ShopeeSalesAgent()
        self.running = True
        
    def enviar_menu_principal(self, chat_id):
        """Envia o menu principal para o usuário"""
        import requests
        import os
        from dotenv import load_dotenv
        
        # Forçar recarregamento do .env
        load_dotenv(override=True)
        
        # Obter o token do bot diretamente do ambiente
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not bot_token:
            print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado")
            return False
        
        # Criar o teclado inline para o menu
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
        
        # Mensagem do menu
        menu_message = """🤖 **DANNET MASTER** - Agente de Vendas Avançado da **F.C.A. DE QUEIROZ ("Automações Comerciais Integradas" ou "ACI")**! 🚀

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

Selecione uma opção abaixo:"""
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": menu_message,
                "parse_mode": "Markdown",
                "reply_markup": keyboard
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    print(f"✅ Menu DANNET MASTER enviado com sucesso para {chat_id}")
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
        
    def get_updates(self):
        """Obtém as últimas atualizações do bot"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "timeout": 30
            }
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return data.get("result", [])
            return []
        except Exception as e:
            print(f"Erro ao obter atualizações: {e}")
            return []
    
    def process_update(self, update):
        """Processa uma atualização (mensagem)"""
        if 'message' in update:
            message = update['message']
            
            # Verificar se é uma mensagem de texto
            if 'text' in message:
                chat = message.get('chat', {})
                chat_id = chat.get('id')
                text = message.get('text')
                user = message.get('from', {})
                username = user.get('username', user.get('first_name', 'Cliente'))
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Nova mensagem de {username} ({chat_id}): {text}")
                
                # Verificar se é um comando especial
                if text.lower() in ['/menu', '/start', 'menu', 'opções', 'opcoes']:
                    # Enviar menu interativo
                    self.enviar_menu_principal(chat_id)
                else:
                    # Processar com o agente
                    resposta = self.agent.responder_mensagem(text, chat_id)
                    
                    # Enviar resposta
                    sucesso = self.agent.enviar_resposta(chat_id, resposta)
                    
                    if sucesso:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Resposta enviada para {username}")
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Falha ao enviar resposta para {username}")
                
                # Atualizar o último ID processado
                self.last_update_id = update['update_id']
        elif 'callback_query' in update:
            # Processar callbacks de botões inline
            callback = update['callback_query']
            chat_id = callback['message']['chat']['id']
            data = callback['data']
            user = callback.get('from', {})
            username = user.get('username', user.get('first_name', 'Cliente'))
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Callback recebido de {username} ({chat_id}): {data}")
            
            # Processar diferentes tipos de callback
            if data == 'voltar_menu':
                self.enviar_menu_principal(chat_id)
            elif data == 'consultar_produtos':
                resposta = self.agent.resposta_consulta_produto("produtos")
                self.agent.enviar_resposta(chat_id, resposta)
            elif data == 'flywheel_concept':
                resposta = self.agent.resposta_flywheel()
                self.agent.enviar_resposta(chat_id, resposta)
            elif data == 'estudos_caso':
                resposta = self.agent.resposta_estudos_caso()
                self.agent.enviar_resposta(chat_id, resposta)
            else:
                # Para outros callbacks, enviar uma resposta genérica
                resposta = self.agent.resposta_padrao(data)
                self.agent.enviar_resposta(chat_id, resposta)
            
            # Responder ao callback
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/answerCallbackQuery"
                payload = {
                    "callback_query_id": callback['id'],
                    "text": "Processando sua solicitação...",
                    "show_alert": False
                }
                requests.post(url, json=payload)
            except:
                pass  # Ignorar erros ao responder callback
            
            # Atualizar o último ID processado
            self.last_update_id = update['update_id']
    
    def start_polling(self):
        """Inicia o polling para receber mensagens continuamente"""
        print(f"🚀 Iniciando serviço do Agente de Vendas Shopee...")
        print(f"🤖 Bot ativo e pronto para responder mensagens 24/7")
        print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("-" * 50)
        
        while self.running:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.process_update(update)
                
                # Pequeno delay para não sobrecarregar a API
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Serviço interrompido pelo usuário")
                self.running = False
            except Exception as e:
                print(f"Erro no polling: {e}")
                time.sleep(5)  # Esperar 5 segundos antes de tentar novamente
    
    def stop(self):
        """Para o serviço"""
        print("🛑 Parando serviço do Agente de Vendas Shopee...")
        self.running = False

def run_service():
    """Função para executar o serviço"""
    service = ShopeeTelegramService()
    
    try:
        service.start_polling()
    except KeyboardInterrupt:
        print("\n🛑 Serviço encerrado pelo usuário")
    finally:
        service.stop()

if __name__ == "__main__":
    run_service()