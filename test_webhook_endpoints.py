"""
Script para testar os endpoints exatos da Evolution API com base no webhook
"""
import requests
import json
from core.config import settings

def testar_webhook_endpoints():
    """Testa os endpoints que sabemos que estão funcionando com base no webhook"""
    
    print("Testando endpoints da Evolution API com base no webhook...")
    
    id_instance = settings.WHATSAPP_ID_INSTANCE
    api_key = settings.AUTHENTICATION_API_KEY
    base_url = settings.WHATSAPP_BASE_URL
    
    print(f"ID Instance: {id_instance}")
    print(f"API Key: {api_key}")
    print(f"Base URL: {base_url}")
    
    if not id_instance or not api_key:
        print("Credenciais não configuradas.")
        return
    
    # Headers baseado no webhook
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "api_key": api_key,
        "X-Instance-ID": id_instance
    }
    
    # Testar endpoints que podem estar relacionados com base no webhook
    print("\n1. Testando status da instância...")
    try:
        url = f"{base_url}/api/{id_instance}/whatsapp/info"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   [OK] Resposta: {response.json()}")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")

    print("\n2. Testando status da conexão...")
    try:
        url = f"{base_url}/api/{id_instance}/status"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   [OK] Resposta: {response.json()}")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")

    print("\n3. Testando endpoints de sessão...")
    session_endpoints = [
        f"{base_url}/api/{id_instance}/instance/fetch",
        f"{base_url}/api/{id_instance}/connection/status",
        f"{base_url}/api/{id_instance}/whatsapp/status",
        f"{base_url}/api/{id_instance}/state",
        f"{base_url}/api/{id_instance}/session",
        f"{base_url}/api/{id_instance}/auth/session"
    ]

    for endpoint in session_endpoints:
        print(f"\n4. Testando: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   [OK] FUNCIONANDO - Resposta: {response.json()}")
                return  # Se encontrar um que funciona, termina
            elif response.status_code == 401:
                print(f"   [AVISO] Não autorizado - credenciais incorretas")
            elif response.status_code == 404:
                print(f"   [ERRO] Endpoint não encontrado")
            else:
                print(f"   [?] Outro código: {response.status_code}")
        except Exception as e:
            print(f"   [ERRO] Erro: {e}")

    print("\n5. Testando com método POST (alguns endpoints podem exigir isso)...")
    post_endpoints = [
        f"{base_url}/api/{id_instance}/instance/start",
        f"{base_url}/api/{id_instance}/connect",
        f"{base_url}/api/{id_instance}/init",
        f"{base_url}/api/{id_instance}/whatsapp/connect"
    ]

    for endpoint in post_endpoints:
        print(f"\n6. Testando POST: {endpoint}")
        try:
            response = requests.post(endpoint, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"   [OK] FUNCIONANDO - Resposta: {response.json()}")
                return
            elif response.status_code == 401:
                print(f"   [AVISO] Não autorizado")
            elif response.status_code == 404:
                print(f"   [ERRO] Endpoint não encontrado")
            else:
                print(f"   [?] Outro código: {response.status_code}")
        except Exception as e:
            print(f"   [ERRO] Erro: {e}")

def testar_envio_mensagem_manual():
    """Testa envio de mensagem manualmente"""
    print(f"\n{'='*60}")
    print("TESTE MANUAL DE ENVIO DE MENSAGEM")
    print("="*60)
    
    id_instance = settings.WHATSAPP_ID_INSTANCE
    api_key = settings.AUTHENTICATION_API_KEY
    base_url = settings.WHATSAPP_BASE_URL
    
    if not id_instance or not api_key:
        print("Credenciais não configuradas.")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "api_key": api_key,
        "X-Instance-ID": id_instance
    }
    
    # Solicitar número para teste
    numero_teste = input("Digite um número do WhatsApp para testar (formato internacional, ex: 5511999999999): ").strip()
    
    if not numero_teste:
        print("Nenhum número fornecido, pulando teste.")
        return
    
    # Tentar diferentes endpoints de envio
    endpoints_envio = [
        f"{base_url}/api/{id_instance}/chat/sendText",
        f"{base_url}/api/{id_instance}/message/sendText",
        f"{base_url}/api/{id_instance}/chat/sendMessage"
    ]
    
    payload = {
        "number": numero_teste,
        "text": "Teste de mensagem via Evolution API - Cleudocodebot!"
    }
    
    print(f"Tentando enviar mensagem para: {numero_teste}")
    
    for endpoint in endpoints_envio:
        print(f"\nTestando envio em: {endpoint}")
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"   [OK] MENSAGEM ENVIADA! Resposta: {response.json()}")
                return
            elif response.status_code == 401:
                print(f"   [AVISO] Não autorizado")
            elif response.status_code == 400:
                print(f"   [AVISO] Requisição inválida - verifique o formato do payload")
                print(f"   Resposta: {response.text}")
            elif response.status_code == 404:
                print(f"   [ERRO] Endpoint não encontrado")
            else:
                print(f"   [?] Outro código: {response.status_code}, Resposta: {response.text}")
        except Exception as e:
            print(f"   [ERRO] Erro: {e}")

if __name__ == "__main__":
    print("Teste de Conexão com Evolution API - Baseado no Webhook")
    print("="*60)
    
    testar_webhook_endpoints()
    testar_envio_mensagem_manual()
    
    print(f"\n{'='*60}")
    print("TESTE CONCLUÍDO")
    print("="*60)
    print("\nNOTA: Se os endpoints acima não funcionarem, o problema pode estar")
    print("na configuração específica do servidor Evolution API ou na forma")
    print("como a instância foi criada.")