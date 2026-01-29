"""
Script para descobrir os endpoints corretos da Evolution API
"""
import requests
from core.config import settings

def descobrir_instancias():
    """Tenta descobrir as instâncias disponíveis na Evolution API"""
    
    print("Descobrindo instâncias na Evolution API...")
    
    api_token = settings.WHATSAPP_API_TOKEN_INSTANCE
    base_url = settings.WHATSAPP_BASE_URL
    
    print(f"Base URL: {base_url}")
    print(f"API Token: {api_token}")
    
    if not api_token:
        print("Token da API não configurado.")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    # Tentar endpoints comuns para listar instâncias
    endpoints_descoberta = [
        f"{base_url}/api/instances",
        f"{base_url}/api/instance/list",
        f"{base_url}/api/listInstances",
        f"{base_url}/instances",
        f"{base_url}/api/config",
        f"{base_url}/api/instance/fetch",
        f"{base_url}/api/show"
    ]
    
    for url in endpoints_descoberta:
        print(f"\nTentando: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"SUCCESS! Response: {response.text}")
                return response.json()
            elif response.status_code == 404:
                print("Endpoint não encontrado")
            elif response.status_code == 401:
                print("Não autorizado - verifique o token")
            else:
                print(f"Outro código: {response.status_code}")
        except Exception as e:
            print(f"Erro: {e}")
    
    print("\nNenhuma lista de instâncias encontrada. Vamos tentar criar uma instância...")
    return None

def testar_instancia_padrao():
    """Testa com um ID de instância padrão ou comum"""
    
    print("\n" + "="*50)
    print("TESTANDO COM IDS DE INSTÂNCIA COMUNS")
    print("="*50)
    
    api_token = settings.WHATSAPP_API_TOKEN_INSTANCE
    base_url = settings.WHATSAPP_BASE_URL
    
    if not api_token:
        print("Token da API não configurado.")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    # IDs de instância comuns usados na Evolution API
    ids_comuns = [
        "default",  # Muito comum como padrão
        "main",
        "primary",
        "1",  # ID numérico comum
        "0",  # ID zero comum
        "myInstance",
        "instance1"
    ]
    
    for id_inst in ids_comuns:
        print(f"\nTestando com ID de instância: '{id_inst}'")
        
        endpoints_teste = [
            f"{base_url}/api/{id_inst}/status",
            f"{base_url}/api/{id_inst}/status/instance",
            f"{base_url}/api/{id_inst}/instance/status",
            f"{base_url}/api/{id_inst}/info",
            f"{base_url}/api/{id_inst}/instance/fetch"
        ]
        
        for endpoint in endpoints_teste:
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                print(f"  {endpoint} -> {response.status_code}")
                if response.status_code == 200:
                    print(f"  ✅ SUCCESS! Response: {response.text[:200]}...")
                    return id_inst
            except Exception as e:
                print(f"  Erro: {e}")
    
    print("\nNenhum ID de instância comum funcionou.")
    return None

def testar_sem_id_instancia():
    """Testa endpoints que não requerem ID de instância explícito"""
    
    print("\n" + "="*50)
    print("TESTANDO ENDPOINTS SEM ID DE INSTÂNCIA")
    print("="*50)
    
    api_token = settings.WHATSAPP_API_TOKEN_INSTANCE
    base_url = settings.WHATSAPP_BASE_URL
    
    if not api_token:
        print("Token da API não configurado.")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    # Endpoints que podem não precisar do ID de instância
    endpoints_sem_id = [
        f"{base_url}/api/connect",
        f"{base_url}/api/start",
        f"{base_url}/api/init",
        f"{base_url}/api/session",
        f"{base_url}/api/auth",
        f"{base_url}/api/whatsapp/connect",
        f"{base_url}/api/whatsapp/init",
        f"{base_url}/api/whatsapp/start"
    ]
    
    for endpoint in endpoints_sem_id:
        print(f"\nTestando: {endpoint}")
        try:
            response = requests.post(endpoint, headers=headers, timeout=10)  # Usando POST para endpoints de ação
            print(f"Status: {response.status_code}")
            if response.status_code in [200, 201, 202]:
                print(f"SUCCESS! Response: {response.text}")
                return True
            elif response.status_code == 404:
                print("Endpoint não encontrado")
            elif response.status_code == 401:
                print("Não autorizado")
            else:
                print(f"Outro código: {response.status_code}")
        except Exception as e:
            print(f"Erro: {e}")
    
    return False

if __name__ == "__main__":
    print("Descoberta de Endpoints da Evolution API")
    print("="*50)
    
    # Primeiro, tenta descobrir instâncias existentes
    instancias = descobrir_instancias()
    
    if not instancias:
        # Se não encontrar instâncias, tenta com IDs comuns
        id_encontrado = testar_instancia_padrao()
        if id_encontrado:
            print(f"\n✅ ID de instância encontrado: {id_encontrado}")
        else:
            # Tenta endpoints sem ID de instância
            testar_sem_id_instancia()
    
    print(f"\n{'='*50}")
    print("DESCOBERTA CONCLUÍDA")
    print("="*50)