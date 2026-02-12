#!/usr/bin/env python3
"""
Script para obter o ID do seu chat e enviar mensagem de boas-vindas para o Telegram
"""
import requests
import time
from core.config import settings

def obter_atualizacoes_telegram():
    """Obtém as últimas atualizações do bot do Telegram para identificar IDs de chat"""
    # Forçar recarregamento do token
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado nas configurações")
        return None
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("ok"):
                updates = data.get("result", [])
                
                if not updates:
                    print("📭 Nenhuma atualização recente encontrada.")
                    print("\n💡 Para obter o ID do seu chat:")
                    print("   1. Abra o Telegram e procure pelo seu bot: @xyzaios_bot")
                    print("   2. Inicie uma conversa e envie qualquer mensagem (ex: 'Olá')")
                    print("   3. Espere 10 segundos")
                    print("   4. Execute este script novamente")
                    print("   5. O ID do seu chat será exibido automaticamente")
                    return None
                
                print("💬 Atualizações recebidas do Telegram:")
                seen_chats = set()  # Para evitar duplicatas
                chat_ids = []
                
                for update in updates:
                    if 'message' in update:
                        message = update['message']
                        chat = message.get('chat', {})
                        
                        chat_id = chat.get('id')
                        chat_type = chat.get('type')
                        chat_title = chat.get('title', 'Privado')
                        user_first_name = message.get('from', {}).get('first_name', 'Desconhecido')
                        
                        if chat_id not in seen_chats:
                            seen_chats.add(chat_id)
                            chat_ids.append(chat_id)
                            
                            print(f"\n---")
                            print(f"🆔 ID do Chat: {chat_id}")
                            print(f"📝 Tipo: {chat_type}")
                            print(f"🏷️  Título: {chat_title}")
                            print(f"👤 Usuário: {user_first_name}")
                            
                            if 'text' in message:
                                print(f"💬 Mensagem: {message['text']}")
                            elif 'photo' in message:
                                print("🖼️  Foto recebida")
                            elif 'document' in message:
                                print("📎 Documento recebido")
                            else:
                                print("📱 Outro tipo de mensagem")
                
                print(f"\n✅ IDs de chat identificados: {chat_ids}")
                return chat_ids
            else:
                print(f"❌ Erro na API do Telegram: {data.get('description', 'Erro desconhecido')}")
                return None
        elif response.status_code == 409:
            print("❌ Erro 409: Conflito de webhook detectado.")
            print("   Isso pode acontecer se o bot estiver conectado a outro webhook.")
            print("   Para resolver, você pode:")
            print("   1. Desativar o webhook atual: /deleteWebhook")
            print("   2. Ou usar o método manual descrito no guia")
            return None
        else:
            print(f"❌ Falha na requisição HTTP: {response.status_code}")
            print(f"   Detalhes: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Erro: Tempo limite excedido ao tentar conectar ao Telegram")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def enviar_mensagem_boas_vindas_para_chat(chat_id):
    """Envia mensagem de boas-vindas para um chat específico"""
    # Forçar recarregamento do token
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado")
        return False
    
    try:
        mensagem = """🎉 Bem-vindo(a) ao nosso canal! 💎✨🃏

🚀 Fique por dentro das últimas novidades
📧 Newsletter exclusiva para membros

🤝 Ajude a comunidade a crescer:
Convide amigos para fazer parte desta jornada!

🔔 Canal oficial: https://whatsapp.com/channel/0029Vb7MgPz5kg767iWItk42

✨ Obrigado por fazer essa comunidade evoluir!"""
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensagem,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print(f"✅ Mensagem de boas-vindas enviada com sucesso para {chat_id}")
                return True
            else:
                print(f"❌ Erro ao enviar mensagem: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Falha ao enviar mensagem: {response.status_code}")
            print(f"   Detalhes: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem de boas-vindas: {e}")
        return False

def main():
    print("🔍 Obtendo IDs de chat do Telegram...")
    chat_ids = obter_atualizacoes_telegram()
    
    if chat_ids:
        print(f"\n🎯 IDs de chat encontrados: {chat_ids}")
        
        # Enviar mensagem de boas-vindas automaticamente para os chats encontrados
        for chat_id in chat_ids:
            print(f"\nEnviando mensagem de boas-vindas para {chat_id}...")
            enviar_mensagem_boas_vindas_para_chat(chat_id)
    else:
        print("\n❌ Nenhum ID de chat encontrado nas atualizações.")
        print("\n💡 Para obter o ID do seu chat:")
        print("   1. Abra o Telegram e procure pelo seu bot: @xyzaios_bot")
        print("   2. Inicie uma conversa e envie qualquer mensagem (ex: 'Olá')")
        print("   3. Espere 10 segundos")
        print("   4. Execute este script novamente")
        print("   5. O ID do seu chat será exibido automaticamente")

if __name__ == "__main__":
    main()