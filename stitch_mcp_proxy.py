#!/usr/bin/env python3
"""
MCP Server Wrapper para Stitch
Proxy que adiciona autenticação OAuth2 ADC
"""

import sys
import json
import subprocess
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class StitchMCPProxy(BaseHTTPRequestHandler):
    """Proxy que adiciona autenticação OAuth2 ao Stitch MCP"""
    
    STITCH_URL = "https://stitch.googleapis.com/mcp"
    PROJECT_ID = "gen-lang-client-0700279835"
    
    def get_access_token(self):
        """Obtém token OAuth2 via gcloud"""
        try:
            result = subprocess.run(
                ["gcloud", "auth", "application-default", "print-access-token"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Erro ao obter token: {e}", file=sys.stderr)
            return None
    
    def do_POST(self):
        """Processa requisições POST"""
        # Ler corpo da requisição
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        # Obter token
        token = self.get_access_token()
        if not token:
            self.send_error(500, "Falha ao obter token de autenticação")
            return
        
        # Preparar headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.PROJECT_ID
        }
        
        try:
            # Fazer requisição ao Stitch
            response = requests.post(
                self.STITCH_URL,
                headers=headers,
                data=body,
                timeout=30
            )
            
            # Retornar resposta
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            print(f"Erro na requisição: {e}", file=sys.stderr)
            self.send_error(500, str(e))
    
    def do_GET(self):
        """Processa requisições GET (SSE)"""
        if self.path == "/sse":
            # SSE endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            
            # Manter conexão aberta
            try:
                while True:
                    # Heartbeat
                    self.wfile.write(b': heartbeat\n\n')
                    self.wfile.flush()
                    import time
                    time.sleep(30)
            except:
                pass
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        """Log personalizado"""
        print(f"[Stitch MCP Proxy] {format % args}", file=sys.stderr)


def run_proxy(port=18901):
    """Inicia o proxy"""
    server = HTTPServer(('localhost', port), StitchMCPProxy)
    print(f"🚀 Stitch MCP Proxy rodando em http://localhost:{port}", file=sys.stderr)
    print(f"📝 Configure o Antigravity para usar: http://localhost:{port}", file=sys.stderr)
    server.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18901
    run_proxy(port)
