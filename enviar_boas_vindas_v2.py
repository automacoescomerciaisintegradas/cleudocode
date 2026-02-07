"""
Script para enviar mensagens proativas para os bots do Telegram
"""
import asyncio
import os
import sys

# Adicionar diretório raiz ao path para importar módulos do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gateways.telegram_adapter import TelegramGateway
    from core.config import settings
except ImportError:
    # Fallback se a estrutura de pastas for diferente no container
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from gateways.telegram_adapter import TelegramGateway
    # Mock settings se não existir
    class Settings:
        pass
    settings = Settings()

import asyncio

async def enviar_async(chat_id, mensagem):
    # Inicializa Gateway
    gateway = TelegramGateway()
    
    # Inicia o bot
    gateway.start()
    
    print(f"Enviando para {chat_id}...")
    
    # Tenta enviar pelo primeiro bot disponível
    try:
        # Recupera primeiro bot configurado
        if not gateway.bots:
            print("Nenhum bot configurado no .env")
            return
            
        bot_name = gateway.bots[0]['name']
        
        # O método send_message do gateway original é sincrono ou async? 
        # Baseado no código anterior, parece ser wrapper sincrono que chama async interno
        # Mas para garantir, vamos usar o método interno se possivel ou chamar direto
        
        await gateway.app.bot.send_message(chat_id=chat_id, text=mensagem)
        print(f"Mensagem enviada com sucesso!")
        
    except Exception as e:
        print(f"Erro ao enviar: {e}")
        # Tenta fallback usando requests direto se a lib falhar
        import requests
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token:
           url = f"https://api.telegram.org/bot{token}/sendMessage"
           data = {"chat_id": chat_id, "text": mensagem}
           resp = requests.post(url, json=data)
           print(f"Fallback via API direta: {resp.status_code} - {resp.text}")

def main():
    chat_id = "5667792894" # ID fornecido no prompt
    
    mensagem = """Até Breve 💎✨🃏
Ajude a 🚀📰Newsletter a crescer convidando mais pessoas, mais pessoas mais motivação para trazer mais conteúdo.

link canal https://whatsapp.com/channel/0029Vb7MgPz5kg767iWItk42"""

    print(f"Enviando mensagem para {chat_id}")
    
    # Como a biblioteca python-telegram-bot é assincrona, precisamos rodar num loop
    # Mas se o gateway abstrair isso, podemos chamar direto.
    # Dado que o código do usuário sugeria uso direto, vamos tentar adaptar.
    
    # Criar gateway
    gateway = TelegramGateway()
    gateway.start() # Isso geralmente inicia o polling em background
    
    # Aguarda um momento para conexão
    import time
    time.sleep(2)
    
    # Envia
    gateway.send_message(chat_id, mensagem)
    print("Feito.")

if __name__ == "__main__":
    main()
