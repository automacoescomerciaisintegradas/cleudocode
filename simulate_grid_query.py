import requests
import json
import time

def simulate_sentient_query():
    url = "http://localhost:8085/api/sentient/query" # Porta mapeada no Docker
    
    print("🚀 Iniciando Simulação de Query via Sentient Grid (Protocolo OML)")
    print("-" * 50)
    
    # Caso 1: Query sem autorização (Deve Falhar se a lealdade não estiver verificada)
    payload_unauthorized = {
        "instruction": "Qual é a sua missão?",
        "auth_proof": "INVALID_TOKEN"
    }
    
    print("\n[Teste 1] Enviando query SEM autorização válida...")
    try:
        response = requests.post(url, json=payload_unauthorized)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
    except Exception as e:
        print(f"Erro: {e}")

    # Caso 2: Query com Autorização de Desenvolvedor (Deve Funcionar)
    payload_authorized = {
        "instruction": "Descreva a arquitetura do CleudoCode em uma frase.",
        "auth_proof": "DEVELOPER_MODE"
    }
    
    print("\n[Teste 2] Enviando query COM autorização (DEVELOPER_MODE)...")
    try:
        start_time = time.time()
        response = requests.post(url, json=payload_authorized)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! Latência: {end_time - start_time:.2f}s")
            print(f"🤖 Resposta do Modelo: {data.get('response')}")
            print(f"📍 Node ID: {data.get('node')}")
            print(f"📜 Protocolo OML: {data.get('oml_version')}")
        else:
            print(f"❌ Falha: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    simulate_sentient_query()
