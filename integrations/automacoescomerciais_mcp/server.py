#!/usr/bin/env python3
import sys
import json
import threading
import http.server
import socketserver
import time
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List

# --- Configurações do Banco de Dados ---
DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefone TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("[INFO] Banco de dados inicializado com sucesso.", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[ERROR] Falha ao inicializar banco de dados: {e}", file=sys.stderr, flush=True)

# --- HTTP Health Check Server ---
class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            try:
                conn = get_db_connection()
                conn.close()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "healthy", "database": "connected"}).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "unhealthy", "error": str(e)}).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <html>
                <head><title>ACI-MCP Gateway</title></head>
                <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                    <h1>🚀 ACI-MCP Gateway is running</h1>
                    <p>Status: <strong>Connected to Database</strong></p>
                    <p>Endpoint MCP: <code>stdio</code></p>
                    <p>Health Check: <a href="/health">/health</a></p>
                </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run_health_check():
    PORT = 65000
    try:
        with socketserver.TCPServer(("", PORT), HealthCheckHandler) as httpd:
            print(f"[INFO] Health check server listening on port {PORT}", file=sys.stderr, flush=True)
            httpd.serve_forever()
    except Exception as e:
        print(f"[ERROR] Health check server failed: {e}", file=sys.stderr, flush=True)

# --- MCP Server ---
class AutomacoesComerciaisMCP:
    def __init__(self):
        self.name = "automacoes-comerciais-mcp"
        self.version = "1.2.0"

    def log_info(self, message: str):
        print(f"[INFO] {message}", file=sys.stderr, flush=True)

    def handle_request(self, line: str):
        try:
            request = json.loads(line)
            method = request.get("method")
            if method == "initialize":
                response = self.handle_initialize(request)
            elif method == "tools/list":
                response = self.handle_tools_list(request)
            elif method == "tools/call":
                response = self.handle_tools_call(request)
            else:
                response = {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32601, "message": "Method not supported"}}
            print(json.dumps(response), flush=True)
        except Exception as e:
            self.log_info(f"Error handling request: {e}")

    def handle_initialize(self, request: Dict) -> Dict:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": self.name, "version": self.version}
            }
        }

    def handle_tools_list(self, request: Dict) -> Dict:
        tools = [
            {
                "name": "adicionar_lead",
                "description": "Adiciona um novo lead ao banco de dados",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string"},
                        "email": {"type": "string"},
                        "telefone": {"type": "string"}
                    },
                    "required": ["nome", "email"]
                }
            },
            {
                "name": "listar_leads",
                "description": "Lista os leads cadastrados",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "listar_usuarios",
                "description": "Lista os usuários cadastrados no sistema",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "listar_transacoes",
                "description": "Lista as transações financeiras recentes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limite": {"type": "integer", "default": 10}
                    }
                }
            },
            {
                "name": "verificar_permissoes_db",
                "description": "Lista as roles e permissões do banco de dados",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
        return {"jsonrpc": "2.0", "id": request.get("id"), "result": {"tools": tools}}

    def handle_tools_call(self, request: Dict) -> Dict:
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            if tool_name == "adicionar_lead":
                nome = arguments.get("nome")
                email = arguments.get("email")
                telefone = arguments.get("telefone")
                cur.execute("INSERT INTO leads (nome, email, telefone) VALUES (%s, %s, %s) RETURNING id", (nome, email, telefone))
                new_id = cur.fetchone()['id']
                conn.commit()
                result = f"Lead adicionado com sucesso! ID: {new_id}"
            
            elif tool_name == "listar_leads":
                cur.execute("SELECT * FROM leads ORDER BY criado_em DESC LIMIT 50")
                leads = cur.fetchall()
                result = json.dumps(leads, default=str, indent=2)

            elif tool_name == "listar_usuarios":
                cur.execute("SELECT id, name, email, role, created_at FROM users LIMIT 50")
                users = cur.fetchall()
                result = json.dumps(users, default=str, indent=2)

            elif tool_name == "listar_transacoes":
                limite = arguments.get("limite", 10)
                cur.execute("SELECT * FROM transactions ORDER BY created_at DESC LIMIT %s", (limite,))
                txs = cur.fetchall()
                result = json.dumps(txs, default=str, indent=2)

            elif tool_name == "verificar_permissoes_db":
                cur.execute("SELECT rolname, rolsuper, rolinherit, rolcreaterole, rolcreatedb, rolcanlogin FROM pg_roles")
                roles = cur.fetchall()
                result = json.dumps(roles, default=str, indent=2)
            
            else:
                return {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32601, "message": "Ferramenta não encontrada"}}
            
            cur.close()
            conn.close()
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"content": [{"type": "text", "text": result}]}
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": str(e)}
            }

    def run(self):
        self.log_info("Starting MCP server...")
        init_db()
        health_thread = threading.Thread(target=run_health_check, daemon=True)
        health_thread.start()
        
        if sys.stdin.isatty():
             for line in sys.stdin:
                 self.handle_request(line)
        else:
            self.log_info("Running in non-interactive mode (Gateway/Health check only via HTTP)")
            while True:
                time.sleep(60)

if __name__ == "__main__":
    server = AutomacoesComerciaisMCP()
    server.run()
