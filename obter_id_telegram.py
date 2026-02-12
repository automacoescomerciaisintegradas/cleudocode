#!/usr/bin/env python3
"""
Script para obter o ID do chat do Telegram
Instruções para uso:
1. Adicione seu bot do Telegram a um grupo ou inicie uma conversa privada
2. Envie uma mensagem para o bot (em um grupo ou conversa privada)
3. Execute este script para obter o ID do chat
"""
import requests
from core.config import settings

def obter_atualizacoes_telegram():
    """Obtém as últimas atualizações do bot do Telegram para identificar IDs de chat"""
    bot_token = settings.get("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado nas configurações")
        return
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("ok"):
                updates = data.get("result", [])
                
                if not updates:
                    print("📭 Nenhuma atualização recente encontrada.")
                    print("\n💡 Para obter o ID do chat:")
                    print("   1. Inicie uma conversa com seu bot no Telegram (@xyzaios_bot)")
                    print("   2. Envie qualquer mensagem para o bot (ex: 'Olá')")
                    print("   3. Espere alguns segundos e execute este script novamente")
                    return
                
                print("💬 Atualizações recebidas do Telegram:")
                seen_chats = set()  # Para evitar duplicatas
                
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
                
                print(f"\n✅ Processo concluído! Use os IDs acima para enviar mensagens diretas.")
            else:
                print(f"❌ Erro na API do Telegram: {data.get('description', 'Erro desconhecido')}")
        elif response.status_code == 409:
            print("❌ Erro 409: Conflito de webhook detectado.")
            print("   Isso pode acontecer se o bot estiver conectado a outro webhook.")
            print("   Para resolver, você pode:")
            print("   1. Desativar o webhook atual: /deleteWebhook")
            print("   2. Ou usar o método manual descrito no guia")
        else:
            print(f"❌ Falha na requisição HTTP: {response.status_code}")
            print(f"   Detalhes: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Erro: Tempo limite excedido ao tentar conectar ao Telegram")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def enviar_mensagem_teste(chat_id):
    """Envia uma mensagem de teste para um chat específico"""
    bot_token = settings.get("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado")
        return
    
    try:
        mensagem = "🤖 Mensagem de teste - este é o ID do seu chat!"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensagem
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print(f"✅ Mensagem de teste enviada com sucesso para {chat_id}")
            else:
                print(f"❌ Erro ao enviar mensagem: {data.get('description', 'Erro desconhecido')}")
        else:
            print(f"❌ Falha ao enviar mensagem: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem de teste: {e}")

if __name__ == "__main__":
    print("🔍 Ferramenta de Descoberta de IDs do Telegram")
    print("="*50)
    
    print("\n1. Obtendo IDs de chats do seu bot...")
    obter_atualizacoes_telegram()
    
    print(f"\n💡 Dica: Para enviar mensagens para um chat específico,")
    print(f"   adicione o ID do chat na lista de destinos no código.")
    
    print(f"\n📋 Exemplo de como usar o ID em seu código:")
    print(f"   chat_ids = [\"SEU_ID_REAL_AQUI\"]")