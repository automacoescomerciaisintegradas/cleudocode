#!/usr/bin/env python3
"""
Serviço para manter o Agente de Vendas Shopee ativo 24/7 no Telegram
"""
import time
import requests
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.shopee_sales_agent import ShopeeSalesAgent

class ShopeeTelegramService:
    def __init__(self):
        from core.config import settings
        self.bot_token = settings.get("TELEGRAM_BOT_TOKEN")
        self.last_update_id = 0
        self.agent = ShopeeSalesAgent()
        self.running = True
        
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