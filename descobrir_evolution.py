"""
Script para descobrir os endpoints corretos da Evolution API
"""
import requests
import os
import sys

# Adicionar root ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings

def descobrir_instancias():
    """Tenta descobrir as instâncias disponíveis na Evolution API"""
    
    print("Descobrindo instâncias na Evolution API...")
    
    api_token = settings.WHATSAPP_API_TOKEN_INSTANCE
    base_url = settings.WHATSAPP_BASE_URL
    
    print(f"Base URL: {base_url}")
    print(f"API Token: {api_token}")
    
    if not api_token or not base_url:
        print("Token da API ou URL Base não configurados no .env")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}",
        "apikey": api_token # Alguns endpoints usam apikey no header
    }
    
    # Tentar endpoints comuns para listar instâncias
    endpoints_descoberta = [
        f"{base_url}/api/instances",
        f"{base_url}/api/instance/list",
        f"{base_url}/api/listInstances",
        f"{base_url}/instances",
        f"{base_url}/instance/fetchInstances",
        f"{base_url}/api/instance/fetchInstances",
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
    
    print("\nNenhuma lista de instâncias encontrada.")
    return None

if __name__ == "__main__":
    descobrir_instancias()
