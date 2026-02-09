#!/usr/bin/env python3
"""
🔗 Configurador de Webhook Evolution API → Cleudocode
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Configurações
BASE_URL = os.getenv("WHATSAPP_BASE_URL", "").rstrip('/')
TOKEN = os.getenv("WHATSAPP_API_TOKEN_INSTANCE")
INSTANCE = os.getenv("WHATSAPP_INSTANCE_NAME", "cleudocode")

def show_status():
    """Mostra status atual"""
    print("""
╭──────────────────────────────────────╮
│  🔗 Cleudocode - Webhook Evolution   │
╰──────────────────────────────────────╯
""")
    
    print("📋 Configuração Atual:")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Instância: {INSTANCE}")
    print(f"   Token: {'✅ Configurado' if TOKEN else '❌ Ausente'}")
    print()

def get_current_webhook():
    """Verifica webhook atual"""
    url = f"{BASE_URL}/webhook/find/{INSTANCE}"
    headers = {"apikey": TOKEN}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return data
        return None
    except Exception as e:
        print(f"❌ Erro ao verificar webhook: {e}")
        return None

def set_webhook(webhook_url):
    """Configura o webhook"""
    url = f"{BASE_URL}/webhook/set/{INSTANCE}"
    headers = {"apikey": TOKEN, "Content-Type": "application/json"}
    
    payload = {
        "url": webhook_url,
        "webhookByEvents": False,
        "webhookBase64": False,
        "events": [
            "APPLICATION_STARTUP",
            "QRCODE_UPDATED",
            "MESSAGES_SET",
            "MESSAGES_UPSERT",
            "MESSAGES_UPDATE",
            "MESSAGES_DELETE",
            "SEND_MESSAGE",
            "CONTACTS_SET",
            "CONTACTS_UPSERT",
            "CONTACTS_UPDATE",
            "PRESENCE_UPDATE",
            "CHATS_SET",
            "CHATS_UPSERT",
            "CHATS_UPDATE",
            "CHATS_DELETE",
            "GROUPS_UPSERT",
            "GROUP_UPDATE",
            "CONNECTION_UPDATE",
            "CALL",
            "NEW_JWT_TOKEN"
        ]
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            print(f"✅ Webhook configurado com sucesso!")
            print(f"   URL: {webhook_url}")
            return True
        else:
            print(f"❌ Erro ao configurar webhook: {resp.status_code}")
            print(f"   Resposta: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def remove_webhook():
    """Remove o webhook"""
    # Evolution API não tem delete, apenas configure com URL vazia ou inválida
    print("⚠️  Para remover o webhook, configure com uma URL vazia ou inválida")
    return False

def test_webhook(webhook_url):
    """Testa se o endpoint do webhook está acessível"""
    try:
        # Tenta acessar o endpoint
        resp = requests.post(webhook_url, json={"test": True}, timeout=5)
        print(f"   Teste: Status {resp.status_code}")
        return resp.status_code in [200, 404, 500]  # Qualquer resposta = está acessível
    except Exception as e:
        print(f"   ⚠️  Endpoint não acessível: {e}")
        return False

def main():
    if not BASE_URL or not TOKEN:
        print("❌ Configure WHATSAPP_BASE_URL e WHATSAPP_API_TOKEN_INSTANCE no .env")
        return
    
    show_status()
    
    # Verifica webhook atual
    print("🔍 Verificando webhook atual...")
    current = get_current_webhook()
    
    if current:
        print(f"   Webhook atual: {current.get('url', 'N/A')}")
        print(f"   Eventos: {len(current.get('events', []))} configurados")
    else:
        print("   Nenhum webhook configurado")
    
    print()
    
    # Menu de opções
    if len(sys.argv) > 1:
        if sys.argv[1] == "set" and len(sys.argv) > 2:
            webhook_url = sys.argv[2]
            print(f"🔧 Configurando webhook: {webhook_url}")
            
            # Testa primeiro
            print("🧪 Testando acessibilidade...")
            test_webhook(webhook_url)
            
            # Configura
            set_webhook(webhook_url)
        elif sys.argv[1] == "test":
            if current and current.get('url'):
                test_webhook(current.get('url'))
            else:
                print("Nenhum webhook configurado para testar")
    else:
        print("📖 Uso:")
        print("   python configurar_webhook.py           # Mostra status")
        print("   python configurar_webhook.py set URL   # Configura webhook")
        print("   python configurar_webhook.py test      # Testa webhook atual")
        print()
        print("💡 Exemplo de URL:")
        print("   https://seu-servidor.com/webhooks/whatsapp")
        print("   http://IP_PUBLICO:18900/webhooks/whatsapp")
        print()
        print("   Se estiver usando ngrok/cloudflare tunnel:")
        print("   https://seu-tunnel.ngrok.io/webhooks/whatsapp")

if __name__ == "__main__":
    main()
