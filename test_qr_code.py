"""
Script para testar o endpoint de QR Code da Evolution API
"""
import requests
import json
from core.config import settings

def testar_qr_code():
    """Testa o endpoint para obter o QR Code da instância"""
    
    print("Testando endpoint para QR Code da Evolution API...")
    
    id_instance = settings.WHATSAPP_ID_INSTANCE
    api_key = settings.AUTHENTICATION_API_KEY
    base_url = settings.WHATSAPP_BASE_URL
    
    print(f"ID Instance: {id_instance}")
    print(f"API Key: {api_key}")
    print(f"Base URL: {base_url}")
    
    if not id_instance or not api_key:
        print("Credenciais não configuradas.")
        return
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "api_key": api_key
    }
    
    # Testar endpoint para obter QR Code
    print("\n1. Testando endpoint para QR Code...")
    try:
        url = f"{base_url}/api/{id_instance}/instance/connect"
        response = requests.post(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   [OK] Resposta: {response.json()}")
        elif response.status_code == 400:
            print(f"   [AVISO] Requisição inválida - pode precisar de parâmetros adicionais")
            print(f"   Resposta: {response.text}")
        elif response.status_code == 401:
            print(f"   [AVISO] Não autorizado - verifique as credenciais")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}, Resposta: {response.text}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")
    
    # Testar outro possível endpoint para QR Code
    print("\n2. Testando outro endpoint possível para QR Code...")
    try:
        url = f"{base_url}/api/{id_instance}/connect"
        response = requests.post(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   [OK] Resposta: {response.json()}")
        elif response.status_code == 400:
            print(f"   [AVISO] Requisição inválida - pode precisar de parâmetros adicionais")
            print(f"   Resposta: {response.text}")
        elif response.status_code == 401:
            print(f"   [AVISO] Não autorizado - verifique as credenciais")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}, Resposta: {response.text}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")
    
    # Testar endpoint para status da instância
    print("\n3. Testando endpoint para status da instância...")
    try:
        url = f"{base_url}/api/{id_instance}/instance/status"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   [OK] Status da instância: {response.json()}")
        elif response.status_code == 401:
            print(f"   [AVISO] Não autorizado - verifique as credenciais")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}, Resposta: {response.text}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")
    
    # Testar endpoint para informações da instância
    print("\n4. Testando endpoint para informações da instância...")
    try:
        url = f"{base_url}/api/{id_instance}/instance/fetch"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   [OK] Informações da instância: {response.json()}")
        elif response.status_code == 401:
            print(f"   [AVISO] Não autorizado - verifique as credenciais")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}, Resposta: {response.text}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")

def testar_webhook_recebido():
    """Mostra como o webhook está funcionando com base nas informações fornecidas"""
    print(f"\n{'='*60}")
    print("INFORMAÇÕES DO WEBHOOK RECEBIDO")
    print("="*60)
    print("Com base nas informações do webhook que você forneceu:")
    print("- A instância está ativa e recebendo eventos")
    print("- O ID da instância é: c95832c3-8406-4cfa-8205-e4978887a9cb")
    print("- O nome da instância é: cleudocodebot")
    print("- A versão da API é: 2.3.7")
    print("- A chave de autenticação está funcionando")
    print("- Eventos estão sendo recebidos corretamente")
    print("\nIsso indica que a instância está configurada,")
    print("mas talvez ainda não esteja completamente conectada ao WhatsApp.")
    print("="*60)

if __name__ == "__main__":
    print("Teste de Conexão com Evolution API - QR Code e Status")
    print("="*60)
    
    testar_webhook_recebido()
    testar_qr_code()
    
    print(f"\n{'='*60}")
    print("TESTE CONCLUÍDO")
    print("="*60)
    print("\nNOTA: Se os endpoints acima não funcionarem, a instância pode")
    print("estar configurada mas ainda não conectada ao WhatsApp. Nesse caso,")
    print("você precisará escanear o QR Code para completar a conexão.")