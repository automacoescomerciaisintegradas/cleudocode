from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import sys

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            code = params['code'][0]
            self.wfile.write(f"<html><body><h1>Login Sucesso!</h1><p>Codigo: {code}</p><p>Pode fechar esta janela.</p></body></html>".encode())
            print(f"AUTH_CODE_RECEIVED:{code}")
            # Terminando o servidor após receber o código
            sys.exit(0)
        else:
            self.wfile.write(b"<html><body><h1>Erro</h1><p>Codigo nao encontrado.</p></body></html>")

def run(port=51121):
    server_address = ('', port)
    httpd = HTTPServer(server_address, OAuthHandler)
    print(f"Servidor ouvindo na porta {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
