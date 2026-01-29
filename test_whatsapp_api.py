"""
Script para testar a conexão com a API do WhatsApp
"""
import requests
from core.config import settings

def testar_conexao_whatsapp():
    """Testa a conexão com a API do WhatsApp"""
    
    print("Testando conexão com a API do WhatsApp...")
    
    id_instance = settings.WHATSAPP_ID_INSTANCE
    api_token = settings.WHATSAPP_API_TOKEN_INSTANCE
    base_url = settings.WHATSAPP_BASE_URL
    
    print(f"ID Instance: {id_instance}")
    print(f"API Token: {api_token}")
    print(f"Base URL: {base_url}")
    
    if not id_instance or not api_token:
        print("Credenciais do WhatsApp não configuradas.")
        return False
    
    # Testar conexão com a API
    try:
        # Endpoint para obter informações da conta
        url = f"{base_url}/waInstance{id_instance}/getStatusInstance/{api_token}"
        
        print(f"Tentando conectar em: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"Código de resposta: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            print("✓ Conexão com a API do WhatsApp bem-sucedida!")
            return True
        else:
            print("✗ Erro na conexão com a API do WhatsApp")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        return False

def testar_formato_green_api():
    """Testa o formato padrão do Green-API"""
    print("\nTestando formato padrão do Green-API...")
    
    id_instance = settings.WHATSAPP_ID_INSTANCE
    api_token = settings.WHATSAPP_API_TOKEN_INSTANCE
    
    if not id_instance or not api_token:
        print("Credenciais do WhatsApp não configuradas.")
        return False
    
    # Testar com o URL padrão do Green-API
    base_url_padrao = "https://api.green-api.com"
    
    try:
        url = f"{base_url_padrao}/waInstance{id_instance}/getStatusInstance/{api_token}"
        print(f"Tentando conectar em: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"Código de resposta: {response.status_code}")
        if response.status_code != 404:  # 404 indica que o endpoint não existe
            print(f"Resposta: {response.text}")
        
        if response.status_code in [200, 201, 400]:  # 400 pode indicar credenciais inválidas mas API acessível
            print("✓ API do Green-API acessível!")
            return True
        else:
            print("✗ API do Green-API não acessível com credenciais atuais")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro de conexão com Green-API: {e}")
        return False

if __name__ == "__main__":
    print("Testando conexão com API do WhatsApp")
    print("="*50)
    
    sucesso = testar_conexao_whatsapp()
    
    if not sucesso:
        print("\nTentando com formato padrão do Green-API...")
        testar_formato_green_api()
    
    print("\nTeste concluído.")