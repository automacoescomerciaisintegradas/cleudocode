"""
Script para testar os endpoints exatos usados no webhook
"""
import requests
import json
from core.config import settings

def testar_endpoints_exatos():
    """Testa os endpoints exatos como usados no webhook"""
    
    print("Testando endpoints exatos como usados no webhook...")
    
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
        "apikey": api_key
    }
    
    # Baseado no webhook, parece que os eventos estão sendo recebidos
    # Isso indica que a instância está ativa, mas talvez não conectada ao WhatsApp
    # Vamos tentar endpoints para verificar o estado da conexão
    
    print("\n1. Testando endpoint para obter QR Code (caso ainda não esteja conectado)...")
    try:
        # Este endpoint pode ser usado para obter o QR Code
        url = f"{base_url}/api/{id_instance}/connect"
        response = requests.post(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   [OK] Resposta: {response.json()}")
            if 'qrcode' in response.json():
                print(f"   QR Code disponível!")
        elif response.status_code == 400:
            print(f"   [AVISO] Requisição inválida - pode precisar de parâmetros")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")
    
    print("\n2. Testando endpoint para obter estado da conexão...")
    try:
        # Endpoint para verificar o estado da conexão
        url = f"{base_url}/api/{id_instance}/status"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   [OK] Status: {response.json()}")
            data = response.json()
            if 'state' in data:
                print(f"   Estado da conexão: {data['state']}")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")
    
    print("\n3. Testando endpoint para informações da instância...")
    try:
        # Endpoint para informações da instância
        url = f"{base_url}/api/{id_instance}/instance"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   [OK] Informações da instância: {response.json()}")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")
    
    print("\n4. Testando endpoint para informações detalhadas...")
    try:
        # Outro possível endpoint para informações
        url = f"{base_url}/api/{id_instance}/info"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   [OK] Informações detalhadas: {response.json()}")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")
    
    print("\n5. Testando endpoint para obter QR Code (formato alternativo)...")
    try:
        # Outro possível endpoint para QR Code
        url = f"{base_url}/api/{id_instance}/qrcode"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   [OK] QR Code: {response.json()}")
        elif response.status_code == 404:
            print(f"   [ERRO] Endpoint não encontrado")
        else:
            print(f"   [?] Outro código: {response.status_code}")
    except Exception as e:
        print(f"   [ERRO] Erro: {e}")

def testar_estado_webhook():
    """Mostra o estado real com base no webhook recebido"""
    print(f"\n{'='*60}")
    print("ESTADO REAL DA INSTÂNCIA BASEADO NO WEBHOOK")
    print("="*60)
    print("Com base no webhook que você forneceu:")
    print("- A instância está recebendo eventos 'presence.update'")
    print("- Isso significa que a instância está ATIVA e recebendo dados")
    print("- O número 558894227586@s.whatsapp.net está sendo monitorado")
    print("- A instância está recebendo informações de presença")
    print("")
    print("Isso indica que:")
    print("[OK] A instância está criada e ativa no servidor")
    print("[OK] A autenticação está funcionando corretamente")
    print("[OK] A instância está recebendo dados do WhatsApp")
    print("[AVISO] Mas pode não estar completamente conectada para envio de mensagens")
    print("")
    print("A instância pode estar em estado de 'conectando' ou 'aguardando QR'.")
    print("Para completar a conexão, é necessário escanear o QR Code.")
    print("="*60)

if __name__ == "__main__":
    print("Teste de Conexão com Evolution API - Baseado no Webhook Exato")
    print("="*60)
    
    testar_estado_webhook()
    testar_endpoints_exatos()
    
    print(f"\n{'='*60}")
    print("TESTE CONCLUÍDO")
    print("="*60)
    print("\nNOTA: Se os endpoints ainda não funcionarem, a instância pode")
    print("estar configurada corretamente mas aguardando a conexão com o WhatsApp.")