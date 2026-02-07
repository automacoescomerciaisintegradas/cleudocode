
import os
import requests
import json
from dotenv import load_dotenv

# Carregar variaveis do .env
load_dotenv()

def send_telegram_direct():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = "5667792894"
    
    if not token:
        print("ERRO: TELEGRAM_BOT_TOKEN não encontrado no .env")
        return

    mensagem = """Até Breve 💎✨🃏
Ajude a 🚀📰Newsletter a crescer convidando mais pessoas, mais pessoas mais motivação para trazer mais conteúdo.

link canal https://whatsapp.com/channel/0029Vb7MgPz5kg767iWItk42"""

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensagem,
        "disable_web_page_preview": False
    }

    try:
        print(f"Enviando mensagem para {chat_id}...")
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Sucesso! Mensagem enviada.")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Erro API Telegram: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exceção ao enviar: {str(e)}")

if __name__ == "__main__":
    send_telegram_direct()
