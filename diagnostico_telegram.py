#!/usr/bin/env python3
"""
Script para testar envio de mensagem e obter informações sobre o chat
"""
import requests
from core.config import settings

def testar_envio_mensagem():
    """Testa o envio de mensagem para obter informações úteis"""
    bot_token = settings.get("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado")
        return
    
    print("🤖 Testando envio de mensagem para diferentes tipos de ID...")
    
    # Testar com um ID de usuário falso para ver o tipo de erro
    fake_user_id = "123456789"
    mensagem = "Teste de mensagem"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": fake_user_id,
        "text": mensagem
    }
    
    print(f"\n1. Testando envio para ID de usuário falso ({fake_user_id})...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Resposta: {data}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Exceção: {e}")
    
    # Agora vamos tentar obter as atualizações novamente
    print(f"\n2. Tentando obter atualizações novamente...")
    try:
        get_updates_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        updates_response = requests.get(get_updates_url, timeout=10)
        
        if updates_response.status_code == 200:
            updates_data = updates_response.json()
            if updates_data.get("ok"):
                updates = updates_data.get("result", [])
                print(f"   Total de atualizações: {len(updates)}")
                
                if updates:
                    for i, update in enumerate(updates[-3:], 1):  # Mostrar os últimos 3
                        print(f"   \nÚltima atualização {i}:")
                        if 'message' in update:
                            msg = update['message']
                            chat = msg.get('chat', {})
                            print(f"     Chat ID: {chat.get('id')}")
                            print(f"     Tipo: {chat.get('type')}")
                            print(f"     Título: {chat.get('title', 'N/A')}")
                            print(f"     Texto: {msg.get('text', 'N/A')}")
                else:
                    print("   Nenhuma atualização recente.")
            else:
                print(f"   Erro na API: {updates_data.get('description')}")
        else:
            print(f"   Erro HTTP: {updates_response.status_code}")
            print(f"   Resposta: {updates_response.text}")
    except Exception as e:
        print(f"   Erro ao obter atualizações: {e}")

def obter_informacoes_bot():
    """Obtém informações sobre o bot"""
    bot_token = settings.get("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado")
        return
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"\n📋 Informações do Bot:")
                print(f"   Nome: {bot_info.get('first_name')}")
                print(f"   Username: @{bot_info.get('username')}")
                print(f"   ID: {bot_info.get('id')}")
                print(f"   É bot: {bot_info.get('is_bot')}")
            else:
                print(f"   Erro ao obter info do bot: {data.get('description')}")
        else:
            print(f"   Erro HTTP ao obter info do bot: {response.status_code}")
    except Exception as e:
        print(f"   Erro ao obter informações do bot: {e}")

def instrucoes_detalhadas():
    """Fornece instruções detalhadas para obter o ID do chat"""
    print(f"\n🔍 INSTRUÇÕES DETALHADAS PARA OBTER O ID DO CHAT:")
    print(f"")
    print(f"1. ABRA O TELEGRAM E PROCURE PELO SEU BOT:")
    print(f"   • Pesquise por: @xyzaios_bot")
    print(f"   • Ou acesse diretamente: https://t.me/xyzaios_bot")
    print(f"")
    print(f"2. INICIE UMA CONVERSA E ENVIE UMA MENSAGEM:")
    print(f"   • Clique em 'Iniciar' ou envie qualquer mensagem")
    print(f"   • Por exemplo: 'Olá', 'Teste', ou 'Conectando'")
    print(f"")
    print(f"3. AGUARDE ALGUNS SEGUNDOS (10-30 segundos)")
    print(f"")
    print(f"4. EXECUTE ESTE SCRIPT NOVAMENTE:")
    print(f"   • O ID do seu chat será exibido automaticamente")
    print(f"")
    print(f"5. SE ISSO NÃO FUNCIONAR:")
    print(f"   • Tente enviar múltiplas mensagens")
    print(f"   • Verifique se você está mandando para o bot correto (@xyzaios_bot)")
    print(f"")

if __name__ == "__main__":
    print("🔧 Ferramenta de Diagnóstico do Telegram")
    print("="*50)
    
    obter_informacoes_bot()
    testar_envio_mensagem()
    instrucoes_detalhadas()