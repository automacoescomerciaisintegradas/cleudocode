#!/usr/bin/env python3
"""
Cliente MCP para Stitch - Teste rápido de list_projects
"""

import requests
import json
import sys

# Configuração do Stitch MCP
STITCH_MCP_URL = "https://stitch.googleapis.com/mcp"
API_KEY = "AIzaSyAb8RN6JMiN6D8gSOMKj0mt4RyXtaVhECA-0MJhP_jYYiTeXAJg"

def call_stitch_tool(tool_name: str, arguments: dict = None):
    """
    Chama uma ferramenta do Stitch MCP
    
    Args:
        tool_name: Nome da ferramenta (ex: 'list_projects')
        arguments: Argumentos da ferramenta
    
    Returns:
        Resposta da API
    """
    headers = {
        "X-Goog-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Formato JSON-RPC 2.0 correto
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
        return None

def list_projects():
    """Lista todos os projetos do Stitch"""
    print("\n" + "="*60)
    print("📋 LISTANDO PROJETOS DO STITCH")
    print("="*60 + "\n")
    
    result = call_stitch_tool("list_projects")
    
    if result:
        print("\n" + "="*60)
        print("📊 RESULTADO")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Extrair e exibir projetos de forma formatada
        if "projects" in result:
            projects = result["projects"]
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
            print("\n⚠️ Nenhum projeto encontrado ou formato de resposta inesperado")
    else:
        print("\n❌ Falha ao listar projetos")

if __name__ == "__main__":
    list_projects()
