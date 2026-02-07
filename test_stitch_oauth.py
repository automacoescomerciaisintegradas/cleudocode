#!/usr/bin/env python3
"""
Cliente MCP para Stitch - Usando OAuth2 ADC
"""

import requests
import json
import subprocess
import sys

# Configuração do Stitch MCP
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
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao obter token: {e}")
        print(f"📝 Certifique-se de executar: gcloud auth application-default login")
        return None
    except FileNotFoundError:
        print(f"❌ gcloud não encontrado. Instale o Google Cloud SDK.")
        return None

def call_stitch_tool(tool_name: str, arguments: dict = None):
    """
    Chama uma ferramenta do Stitch MCP usando OAuth2
    
    Args:
        tool_name: Nome da ferramenta (ex: 'list_projects')
        arguments: Argumentos da ferramenta
    
    Returns:
        Resposta da API
    """
    # Obter token OAuth2
    access_token = get_access_token()
    if not access_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Formato JSON-RPC 2.0
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        },
        "id": 1
    }
    
    try:
        print(f"🔍 Chamando ferramenta: {tool_name}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        print(f"🔐 Token: {access_token[:20]}...{access_token[-10:]}")
        
        response = requests.post(
            STITCH_MCP_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso!")
            return result
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def list_projects():
    """Lista todos os projetos do Stitch"""
    print("\n" + "="*60)
    print("📋 LISTANDO PROJETOS DO STITCH (OAuth2)")
    print("="*60 + "\n")
    
    result = call_stitch_tool("list_projects")
    
    if result:
        print("\n" + "="*60)
        print("📊 RESULTADO")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Processar resultado JSON-RPC
        if "result" in result:
            rpc_result = result["result"]
            
            # Verificar se há erro
            if rpc_result.get("isError"):
                print("\n❌ Erro retornado pela API:")
                if "content" in rpc_result:
                    for content in rpc_result["content"]:
                        if content.get("type") == "text":
                            print(f"  {content.get('text')}")
            else:
                # Sucesso - processar conteúdo
                if "content" in rpc_result:
                    for content in rpc_result["content"]:
                        if content.get("type") == "text":
                            try:
                                # Tentar parsear JSON
                                projects_data = json.loads(content.get("text", "{}"))
                                
                                if "projects" in projects_data:
                                    projects = projects_data["projects"]
                                    print(f"\n✨ Total de projetos: {len(projects)}")
                                    
                                    for i, project in enumerate(projects, 1):
                                        print(f"\n🎨 Projeto {i}:")
                                        print(f"  ID: {project.get('id', 'N/A')}")
                                        print(f"  Nome: {project.get('name', 'N/A')}")
                                        print(f"  Criado: {project.get('created_at', 'N/A')}")
                                        print(f"  Atualizado: {project.get('updated_at', 'N/A')}")
                                        
                                        if 'screens' in project:
                                            print(f"  Telas: {len(project['screens'])}")
                                else:
                                    print(f"\n📄 Conteúdo: {content.get('text')}")
                            except json.JSONDecodeError:
                                print(f"\n📄 Conteúdo (texto): {content.get('text')}")
        else:
            print("\n⚠️ Formato de resposta inesperado")
    else:
        print("\n❌ Falha ao listar projetos")
        print("\n💡 Dica: Execute primeiro:")
        print("   gcloud auth application-default login")

if __name__ == "__main__":
    list_projects()
