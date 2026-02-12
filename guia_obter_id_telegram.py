#!/usr/bin/env python3
"""
Guia para obter o ID do chat do Telegram
"""
import requests
from core.config import settings

def obter_id_manual():
    """Fornece instruções manuais para obter o ID do chat"""
    print("🔐 MÉTODO MANUAL PARA OBTER O ID DO CHAT DO TELEGRAM")
    print("="*60)
    print()
    print("Existem duas formas principais de obter o ID do seu chat:")
    print()
    print("1. VIA BOT CONVERSATION (Método mais simples):")
    print("   • Adicione seu bot a um grupo ou inicie conversa privada")
    print("   • Envie qualquer mensagem para o bot (ex: 'Olá')")
    print("   • Acesse: https://api.telegram.org/bot<TOKEN>/getUpdates")
    print("   • Substitua <TOKEN> pelo seu token do bot")
    print("   • Procure pelo campo 'chat' -> 'id' na resposta")
    print()
    print("2. VIA @USERINFobot (Método alternativo):")
    print("   • Vá para https://t.me/userinfobot")
    print("   • Inicie uma conversa com o bot")
    print("   • Ele mostrará seu ID de usuário")
    print()
    print("3. VIA @RAWDATA_BOT (Método mais detalhado):")
    print("   • Vá para https://t.me/rawdata_bot")
    print("   • Envie qualquer mensagem para o bot")
    print("   • Ele enviará um arquivo JSON com todos os dados")
    print("   • Procure pelo campo 'chat' -> 'id'")
    print()
    print("4. PARA GRUPOS:")
    print("   • Adicione o bot ao grupo")
    print("   • Faça o bot enviar uma mensagem para o grupo")
    print("   • Use o método 1 para obter o ID do grupo")
    print("   • IDs de grupos geralmente são negativos (ex: -1001234567890)")
    print()
    print("ATENÇÃO:")
    print("• IDs de grupos privados começam com -100 (ex: -1001234567890)")
    print("• IDs de usuários são números positivos")
    print("• IDs de canais também podem ser negativos")
    print()
    print("EXEMPLO DE COMO USAR O ID:")
    print("Depois de obter o ID real, substitua nos scripts:")
    print('chat_ids = ["SEU_ID_REAL_AQUI"]')
    print()
    print("Seu token do bot é: ", end="")
    
    bot_token = settings.get("TELEGRAM_BOT_TOKEN")
    if bot_token:
        print(f"{'*' * (len(bot_token)-10)}{bot_token[-10:]}")
        print()
        print(f"Link para verificar atualizações: https://api.telegram.org/bot{bot_token}/getUpdates")
    else:
        print("NÃO ENCONTRADO")
        print("Verifique se o TELEGRAM_BOT_TOKEN está configurado corretamente no .env")

def testar_conexao_bot():
    """Testa a conexão básica com o bot"""
    bot_token = settings.get("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado nas configurações")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                user_info = data.get("result", {})
                print(f"✅ Bot conectado com sucesso!")
                print(f"   Nome: {user_info.get('first_name', 'Desconhecido')}")
                print(f"   @username: @{user_info.get('username', 'desconhecido')}")
                print(f"   ID: {user_info.get('id', 'desconhecido')}")
                return True
            else:
                print(f"❌ API do Telegram retornou erro: {data.get('description', 'Descrição não disponível')}")
                return False
        else:
            print(f"❌ Falha na requisição HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Erro: Tempo limite excedido ao tentar conectar ao Telegram")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Guia Completo para Obter ID do Chat do Telegram")
    print("="*60)
    
    print("\n1. Verificando conexão com o bot...")
    conexao_ok = testar_conexao_bot()
    
    if conexao_ok:
        print("\n2. Instruções para obter o ID do seu chat:")
        obter_id_manual()
    else:
        print("\n❌ Não foi possível conectar ao bot. Verifique suas configurações.")