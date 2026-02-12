#!/usr/bin/env python3
"""
Script para obter o ID do chat do Telegram e testar a funcionalidade
"""
import requests
import time
from core.config import settings

def obter_atualizacoes_telegram():
    """Obtém as últimas atualizações do bot do Telegram para identificar IDs de chat"""
    bot_token = settings.get("TELEGRAM_BOT_TOKEN")
    
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

def instrucoes_obter_id():
    """Exibe instruções para obter o ID do chat"""
    print("\n🔍 INSTRUÇÕES PARA OBTER O ID DO SEU CHAT:")
    print("1. Abra o Telegram e procure pelo seu bot: @xyzaios_bot")
    print("2. Inicie uma conversa e envie qualquer mensagem (ex: 'teste')")
    print("3. Volte aqui e execute este script novamente")
    print("4. O ID do seu chat será exibido automaticamente")

def testar_envio_mensagem(chat_id):
    """Testa o envio de uma mensagem para o chat"""
    bot_token = settings.get("TELEGRAM_BOT_TOKEN")
    
    if not bot_token or not chat_id:
        print("❌ Erro: Token do bot ou ID do chat não fornecido")
        return False
    
    try:
        mensagem = "🤖 Teste de conexão - esta é uma mensagem de teste!"
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
                return True
            else:
                print(f"❌ Erro ao enviar mensagem: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Falha ao enviar mensagem: {response.status_code}")
            print(f"   Detalhes: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem de teste: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Ferramenta de Descoberta de IDs do Telegram")
    print("="*50)
    
    print("\n1. Verificando atualizações do bot...")
    chat_ids = obter_atualizacoes_telegram()
    
    if chat_ids:
        print(f"\n🎯 IDs de chat encontrados: {chat_ids}")
        
        # Oferecer para testar envio de mensagem
        if chat_ids:
            print(f"\n🧪 Deseja testar o envio de uma mensagem de teste?")
            resposta = input("Digite 's' para sim ou qualquer outra tecla para não: ").lower().strip()
            
            if resposta == 's':
                for chat_id in chat_ids:
                    print(f"\nEnviando mensagem de teste para {chat_id}...")
                    testar_envio_mensagem(chat_id)
    else:
        print("\n❌ Nenhum ID de chat encontrado nas atualizações.")
        instrucoes_obter_id()
    
    print(f"\n💡 Dica: Para enviar mensagens de boas-vindas futuramente,")
    print(f"   use os IDs encontrados nos scripts de envio.")