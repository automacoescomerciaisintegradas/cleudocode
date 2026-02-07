#!/usr/bin/env python3
"""
Teste detalhado do Stitch MCP com debug completo
"""

import requests
import json
import subprocess
import sys

STITCH_MCP_URL = "https://stitch.googleapis.com/mcp"

def get_access_token():
    """Obtém o access token do gcloud ADC"""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        token = result.stdout.strip()
        return token
    except Exception as e:
        print(f"❌ Erro ao obter token: {e}")
        return None

def test_stitch_connection():
    """Testa a conexão com Stitch MCP"""
    print("="*70)
    print("🔬 TESTE DETALHADO DO STITCH MCP")
    print("="*70)
    
    # 1. Verificar token
    print("\n📝 Passo 1: Obtendo token OAuth2...")
    token = get_access_token()
    if not token:
        print("❌ Falha ao obter token")
        return
    
    print(f"✅ Token obtido: {token[:30]}...{token[-20:]}")
    print(f"   Tamanho: {len(token)} caracteres")
    
    # 2. Verificar configuração do projeto
    print("\n📝 Passo 2: Verificando configuração do projeto...")
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            check=True
        )
        project_id = result.stdout.strip()
        print(f"✅ Projeto configurado: {project_id}")
    except Exception as e:
        print(f"⚠️ Erro ao obter projeto: {e}")
        project_id = "unknown"
    
    # 3. Verificar credenciais ADC
    print("\n📝 Passo 3: Verificando credenciais ADC...")
    try:
        with open("/root/.config/gcloud/application_default_credentials.json", "r") as f:
            creds = json.load(f)
            print(f"✅ Tipo: {creds.get('type')}")
            print(f"✅ Quota Project: {creds.get('quota_project_id')}")
            print(f"✅ Account: {creds.get('account', 'N/A')}")
    except Exception as e:
        print(f"⚠️ Erro ao ler credenciais: {e}")
    
    # 4. Testar chamada ao Stitch MCP
    print("\n📝 Passo 4: Testando chamada ao Stitch MCP...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_id  # Adicionar header de quota project
    }
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "list_projects",
            "arguments": {}
        },
        "id": 1
    }
    
    print(f"\n📤 Request:")
    print(f"   URL: {STITCH_MCP_URL}")
    print(f"   Headers: {json.dumps({k: v[:50] + '...' if len(v) > 50 else v for k, v in headers.items()}, indent=4)}")
    print(f"   Payload: {json.dumps(payload, indent=4)}")
    
    try:
        response = requests.post(
            STITCH_MCP_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📥 Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCESSO!")
            print(f"\n📊 Resultado:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Processar resultado
            if "result" in result and not result["result"].get("isError"):
                print(f"\n🎉 Chamada bem-sucedida!")
                if "content" in result["result"]:
                    for content in result["result"]["content"]:
                        if content.get("type") == "text":
                            try:
                                data = json.loads(content["text"])
                                if "projects" in data:
                                    print(f"\n✨ Projetos encontrados: {len(data['projects'])}")
                                    for i, proj in enumerate(data['projects'], 1):
                                        print(f"\n  🎨 Projeto {i}:")
                                        print(f"     ID: {proj.get('id')}")
                                        print(f"     Nome: {proj.get('name')}")
                            except json.JSONDecodeError:
                                print(f"\n📄 Conteúdo: {content['text']}")
        else:
            print(f"\n❌ ERRO {response.status_code}")
            print(f"\n📄 Resposta:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
                
                # Analisar erro
                if "result" in error_data and error_data["result"].get("isError"):
                    if "content" in error_data["result"]:
                        for content in error_data["result"]["content"]:
                            if content.get("type") == "text":
                                print(f"\n💡 Mensagem de erro:")
                                print(f"   {content['text']}")
            except:
                print(response.text)
                
    except Exception as e:
        print(f"\n❌ Exceção: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stitch_connection()
