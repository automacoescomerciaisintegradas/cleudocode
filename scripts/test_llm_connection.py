import sys
import os
import requests

# Adicionar raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

def test_connection():
    print(f"--- Diagnóstico de Conexão LLM ---")
    print(f"URL Base: {settings.LLM_BASE_URL}")
    print(f"Modelo: {settings.LLM_MODEL}")
    print(f"Provider: {settings.LLM_PROVIDER}")
    print("-" * 30)

    try:
        # Endpoint de Tags/Version do Ollama
        url = f"{settings.LLM_BASE_URL}/api/tags"
        print(f"Testando GET {url}...")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ SUCESSO: Conexão estabelecida!")
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            print(f"Modelos Disponíveis: {model_names}")
            
            if settings.LLM_MODEL in model_names:
                print(f"✅ Modelo alvo '{settings.LLM_MODEL}' encontrado no servidor.")
            else:
                print(f"⚠️ AVISO: Modelo '{settings.LLM_MODEL}' NÃO encontrado na lista.")
        else:
            print(f"❌ FALHA: Status Code {response.status_code}")
            print(f"Resposta: {response.text}")

    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")

if __name__ == "__main__":
    test_connection()
