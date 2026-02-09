#!/usr/bin/env python3
"""
Stitch MCP Server - Servidor standalone compatível com MCP protocol
Usa stdio para comunicação (stdin/stdout)
"""

import sys
import json
import subprocess
import requests
import os
from typing import Dict, Any


class StitchMCPServer:
    """Servidor MCP para Stitch com autenticação OAuth2 ADC"""
    
    def __init__(self):
        self.stitch_url = "https://stitch.googleapis.com/mcp"
        # Forçando o Project ID para evitar falhas de contexto do ambiente
        self.project_id = "gen-lang-client-0700279835"
        
    def get_access_token(self) -> str:
        """Obtém token OAuth2 via gcloud"""
        try:
            # Usando caminho absoluto para evitar problemas de PATH
            result = subprocess.run(
                ["/usr/bin/gcloud", "auth", "application-default", "print-access-token"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception as e:
            self.log_error(f"Erro ao obter token via /usr/bin/gcloud: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                self.log_error(f"Stderr do gcloud: {e.stderr}")
            return None
    
    def log_error(self, message: str):
        """Log de erro (stderr)"""
        print(f"[ERROR] {message}", file=sys.stderr, flush=True)
    
    def log_info(self, message: str):
        """Log de info (stderr)"""
        print(f"[INFO] {message}", file=sys.stderr, flush=True)
    
    def handle_initialize(self, request: Dict) -> Dict:
        """Handle initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "stitch-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    
    def handle_tools_list(self, request: Dict) -> Dict:
        """Handle tools/list request"""
        tools = [
            {
                "name": "list_projects",
                "description": "Lista todos os projetos do Stitch",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_project",
                "description": "Obtém detalhes de um projeto específico",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "ID do projeto"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "generate_screen_from_text",
                "description": "Gera uma tela de UI a partir de um prompt de texto",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Descrição da UI a ser gerada"
                        },
                        "device_type": {
                            "type": "string",
                            "enum": ["MOBILE", "DESKTOP", "TABLET"],
                            "description": "Tipo de dispositivo"
                        }
                    },
                    "required": ["prompt"]
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": tools
            }
        }
    
    def handle_tools_call(self, request: Dict) -> Dict:
        """Handle tools/call request"""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        self.log_info(f"Chamando ferramenta: {tool_name}")
        
        # Obter token
        token = self.get_access_token()
        if not token:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": "Falha ao obter token de autenticação"
                }
            }
        
        # Preparar requisição para Stitch
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id
        }
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
        
        try:
            response = requests.post(
                self.stitch_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                stitch_result = response.json()
                
                # Retornar resultado do Stitch
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": stitch_result.get("result", {})
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": response.status_code,
                        "message": f"Erro HTTP {response.status_code}: {response.text}"
                    }
                }
        
        except Exception as e:
            self.log_error(f"Erro na requisição: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def handle_request(self, request: Dict) -> Dict:
        """Processa uma requisição MCP"""
        method = request.get("method", "")
        
        if method == "initialize":
            return self.handle_initialize(request)
        elif method == "tools/list":
            return self.handle_tools_list(request)
        elif method == "tools/call":
            return self.handle_tools_call(request)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Método não suportado: {method}"
                }
            }
    
    def run(self):
        """Loop principal do servidor (stdin/stdout)"""
        self.log_info("Stitch MCP Server iniciado")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    self.log_info(f"Requisição recebida: {request.get('method')}")
                    
                    response = self.handle_request(request)
                    
                    # Enviar resposta via stdout
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError as e:
                    self.log_error(f"JSON inválido: {e}")
                except Exception as e:
                    self.log_error(f"Erro ao processar requisição: {e}")
                    import traceback
                    traceback.print_exc(file=sys.stderr)
        
        except KeyboardInterrupt:
            self.log_info("Servidor interrompido")


if __name__ == "__main__":
    server = StitchMCPServer()
    server.run()
