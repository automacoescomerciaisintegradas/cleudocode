#!/usr/bin/env python3
"""
Script para testar a conexão com o bot do Telegram
"""
import os
import requests
from core.config import settings

def test_telegram_connection():
    """Testa a conexão com o bot do Telegram"""
    print("🔍 Testando conexão com o bot do Telegram...")
    
    # Obtém o token do bot
    bot_token = settings.get("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado nas configurações")
        print("💡 Verifique se o token está definido no arquivo .env.prod")
        return False
    
    print(f"✅ Token do bot encontrado: {'*' * (len(bot_token) - 10)}{bot_token[-10:]}")
    
    # Testa a conexão com a API do Telegram
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                user_info = data.get("result", {})
                print(f"✅ Bot do Telegram conectado com sucesso!")
                print(f"   Nome do bot: {user_info.get('first_name', 'Desconhecido')}")
                print(f"   Username: @{user_info.get('username', 'desconhecido')}")
                print(f"   ID do bot: {user_info.get('id', 'desconhecido')}")
                return True
            else:
                print(f"❌ API do Telegram retornou erro: {data.get('description', 'Descrição não disponível')}")
                return False
        else:
            print(f"❌ Falha na requisição HTTP: {response.status_code} - {response.text}")
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

def check_gateway_status():
    """Verifica o status do gateway do Telegram"""
    print("\n🔍 Verificando status do gateway do Telegram...")
    
    try:
        from gateways.telegram_adapter import TelegramGateway
        gateway = TelegramGateway()
        
        if gateway.tokens:
            print(f"✅ Gateway do Telegram encontrado {len(gateway.tokens)} token(s)")
            for i, token_info in enumerate(gateway.tokens):
                print(f"   Bot {i+1}: {token_info['name']} - {'Ativo' if token_info['application'] is not None else 'Não iniciado'}")
            return True
        else:
            print("❌ Nenhum token do Telegram encontrado pelo gateway")
            return False
    except ImportError as e:
        print(f"❌ Erro ao importar o gateway do Telegram: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar o gateway do Telegram: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste de Configuração do Telegram para OpenClaw")
    print("="*50)
    
    # Testa a conexão
    connection_ok = test_telegram_connection()
    
    # Verifica o status do gateway
    gateway_ok = check_gateway_status()
    
    print("\n" + "="*50)
    if connection_ok and gateway_ok:
        print("🎉 Todos os testes do Telegram passaram com sucesso!")
        print("✅ O pareamento (pairing) do OpenClaw com o Telegram está configurado corretamente")
    else:
        print("❌ Problemas encontrados na configuração do Telegram")
        print("🔧 Verifique os erros acima e corrija conforme necessário")