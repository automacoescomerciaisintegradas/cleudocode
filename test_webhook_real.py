"""
Script para testar diretamente os endpoints com base no webhook
"""
import requests
import json
from core.config import settings

def testar_endpoints_corretos():
    """Testa os endpoints com a autenticação exata como no webhook"""
    
    print("Testando endpoints com autenticação exata como no webhook...")
    
    id_instance = settings.WHATSAPP_ID_INSTANCE
    api_key = settings.AUTHENTICATION_API_KEY
    base_url = settings.WHATSAPP_BASE_URL
    
    print(f"ID Instance: {id_instance}")
    print(f"API Key: {api_key}")
    print(f"Base URL: {base_url}")
    
    if not id_instance or not api_key:
        print("Credenciais não configuradas.")
        return
    
    # Headers exatamente como no webhook
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "apikey": api_key  # Exatamente como no webhook
    }
    
    # Testar o endpoint exato que está funcionando no webhook
    print("\n1. Testando endpoint de status da conexão...")
    try:
        # Baseado no webhook, o endpoint pode ser diferente
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
    
    print("\n2. Testando endpoint de informações da instância...")
    try:
        url = f"{base_url}/api/{id_instance}/instance/fetch"
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
    
    print("\n3. Testando endpoint de estado da conexão...")
    try:
        # Este é o endpoint que parece estar funcionando baseado no webhook
        url = f"{base_url}/api/instance/connectionState/{id_instance}"
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
    
    print("\n4. Testando endpoint de informações da instância (formato alternativo)...")
    try:
        url = f"{base_url}/api/instance/info/{id_instance}"
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
    
    print("\n5. Testando envio de mensagem...")
    try:
        url = f"{base_url}/api/message/sendText/{id_instance}"
        payload = {
            "number": "5511999999999",  # Número de teste
            "text": "Teste de mensagem"
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   [OK] Mensagem enviada: {response.json()}")
        elif response.status_code == 400:
            print(f"   [AVISO] Requisição inválida (provavelmente número inválido): {response.text}")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}, Resposta: {response.text}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")

def testar_webhook_recebido():
    """Mostra como o webhook está funcionando com base nas informações fornecidas"""
    print(f"\n{'='*60}")
    print("ANÁLISE DO WEBHOOK RECEBIDO")
    print("="*60)
    print("Com base nas informações do webhook que você forneceu:")
    print("- A instância está ativa e recebendo eventos")
    print("- O ID da instância é: c95832c3-8406-4cfa-8205-e4978887a9cb")
    print("- O nome da instância é: cleudocodebot")
    print("- A versão da API é: 2.3.7")
    print("- A chave de autenticação usada é: 0D60FBDD8358-4BE0-8F17-117F8DC3256E")
    print("- Headers usados: apikey, X-Instance-ID, X-Instance-Name")
    print("")
    print("Importante notar que o webhook mostra que a instância está:")
    print("- Recebendo eventos de presença (presence.update)")
    print("- O número 558894227586@s.whatsapp.net está ativo")
    print("- A instância está recebendo mensagens e eventos")
    print("")
    print("Isso indica que a instância está configurada e ativa,")
    print("mas talvez ainda não esteja completamente conectada ao WhatsApp")
    print("ou o gateway não está conseguindo acessar os endpoints corretos.")
    print("="*60)

if __name__ == "__main__":
    print("Teste de Conexão com Evolution API - Baseado no Webhook Real")
    print("="*60)
    
    testar_webhook_recebido()
    testar_endpoints_corretos()
    
    print(f"\n{'='*60}")
    print("TESTE CONCLUÍDO")
    print("="*60)
    print("\nNOTA: Se os endpoints acima não funcionarem, a instância pode")
    print("estar configurada mas com restrições de acesso específicas.")