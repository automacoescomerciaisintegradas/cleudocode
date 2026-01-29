import requests
import threading
import time
from core.daemon import CleudoDaemon
from core.api import WebAPIGateway
from gateways.cli_adapter import CLIGateway

print("Iniciando teste da API...")

# Iniciar daemon e API em uma thread separada para teste
daemon = CleudoDaemon()
daemon.setup()
daemon.add_gateway(CLIGateway())

api_gw = WebAPIGateway(daemon, port=5001)
api_gw.start()

print("Aguardando a API iniciar...")
time.sleep(3)  # Aguardar mais tempo para a API iniciar

try:
    print("Testando endpoint de status...")
    response = requests.get('http://localhost:5001/api/v1/status')
    print('Status da API:', response.json())
    
    print("Testando endpoint de gateways...")
    response = requests.get('http://localhost:5001/api/v1/gateways')
    print('Gateways:', response.json())
    
    print("Testando endpoint de configurações...")
    response = requests.get('http://localhost:5001/api/v1/config')
    print('Configurações:', response.json())
    
    print('[SUCCESS] Testes da API REST funcionando corretamente!')

except Exception as e:
    print('[ERROR] Erro nos testes da API:', e)
finally:
    print("Parando o daemon...")
    daemon.stop()
    print("Daemon parado.")