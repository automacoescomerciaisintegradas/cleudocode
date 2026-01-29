"""
Script para testar manualmente a conexão com a Evolution API
"""
import requests
from core.config import settings

def testar_endpoints_evolution_api():
    """Testa manualmente os endpoints da Evolution API"""
    
    print("Testando endpoints da Evolution API...")
    
    id_instance = settings.WHATSAPP_ID_INSTANCE
    api_token = settings.WHATSAPP_API_TOKEN_INSTANCE
    base_url = settings.WHATSAPP_BASE_URL
    
    print(f"ID Instance: {id_instance}")
    print(f"API Token: {api_token}")
    print(f"Base URL: {base_url}")
    
    if not id_instance or not api_token:
        print("Credenciais do WhatsApp não configuradas.")
        return
    
    # Headers para autenticação
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    # Lista de endpoints potenciais para testar
    endpoints_to_try = [
        # Status e informações da instância
        f"{base_url}/api/{id_instance}/status/instance",
        f"{base_url}/api/{id_instance}/instance/status",
        f"{base_url}/api/{id_instance}/status",
        f"{base_url}/api/{id_instance}/info",
        f"{base_url}/status/{id_instance}",
        f"{base_url}/instance/{id_instance}/status",
        
        # Endpoints legados (caso esteja usando versão mais antiga)
        f"{base_url}/api/waInstance{id_instance}/statusInstance/{api_token}",
        f"{base_url}/api/{id_instance}/instance/ping",
        
        # Root endpoints
        f"{base_url}/",
        f"{base_url}/api/",
    ]
    
    print(f"\nTentando {len(endpoints_to_try)} endpoints diferentes...")
    
    for i, url in enumerate(endpoints_to_try, 1):
        print(f"\n{i}. Testando: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status Code: {response.status_code}")
            if response.status_code in [200, 201, 202]:
                print(f"   [OK] SUCESSO - Resposta: {response.text[:200]}...")
                # Se for 200, tentar enviar uma mensagem de teste
                break
            elif response.status_code == 404:
                print(f"   [ERRO] Não encontrado")
            elif response.status_code == 401:
                print(f"   [AVISO] Não autorizado - credenciais podem estar incorretas")
            elif response.status_code == 403:
                print(f"   [AVISO] Acesso proibido - verifique permissões")
            else:
                print(f"   [?] Outro código: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   [ERRO] Erro de conexão - servidor pode estar offline")
        except requests.exceptions.Timeout:
            print(f"   [ERRO] Timeout - servidor demorou para responder")
        except Exception as e:
            print(f"   [ERRO] Erro: {e}")
    
    print(f"\nTeste concluído. Se nenhum endpoint funcionou, verifique:")
    print(f"- Se o servidor Evolution API está online e acessível")
    print(f"- Se as credenciais (ID e Token) estão corretas")
    print(f"- Se o formato da URL está correto para a sua instalação")

def testar_envio_mensagem():
    """Testa o envio de uma mensagem de teste"""
    print(f"\n{'='*50}")
    print("TESTE DE ENVIO DE MENSAGEM")
    print("="*50)
    
    id_instance = settings.WHATSAPP_ID_INSTANCE
    api_token = settings.WHATSAPP_API_TOKEN_INSTANCE
    base_url = settings.WHATSAPP_BASE_URL
    
    if not id_instance or not api_token:
        print("Credenciais do WhatsApp não configuradas.")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    # Testar envio para um número de teste (substitua por um número real para testar de verdade)
    numero_teste = input("Digite um número de WhatsApp para testar (ou pressione Enter para pular): ").strip()
    
    if not numero_teste:
        print("Pulando teste de envio de mensagem.")
        return
    
    endpoints_envio = [
        f"{base_url}/api/{id_instance}/chat/sendText",
        f"{base_url}/api/{id_instance}/message/sendText",
        f"{base_url}/api/{id_instance}/chat/sendMessage",
        f"{base_url}/api/{id_instance}/send/text",
        f"{base_url}/send/{id_instance}/text",
        f"{base_url}/api/{id_instance}/chat/send"
    ]
    
    payload = {
        "number": numero_teste,
        "text": "Teste de mensagem da Evolution API via Cleudocodebot!",
        "delay": 1200,
        "presence": "composing"
    }
    
    print(f"Tentando enviar mensagem para: {numero_teste}")
    
    for i, url in enumerate(endpoints_envio, 1):
        print(f"\n{i}. Testando envio em: {url}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"   Status Code: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"   ✅ MENSAGEM ENVIADA COM SUCESSO!")
                print(f"   Resposta: {response.text}")
                break
            elif response.status_code == 404:
                print(f"   ❌ Endpoint não encontrado")
            elif response.status_code == 401:
                print(f"   ⚠️  Não autorizado")
            else:
                print(f"   ❓ Código: {response.status_code}, Resposta: {response.text}")
        except Exception as e:
            print(f"   ❗ Erro: {e}")

if __name__ == "__main__":
    print("Teste de Conexão com Evolution API")
    print("="*50)
    
    testar_endpoints_evolution_api()
    testar_envio_mensagem()
    
    print(f"\n{'='*50}")
    print("TESTE CONCLUÍDO")
    print("="*50)