"""
Servidor Web para Teste do Sistema de Comunicação Multicanal
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from gateways.telegram_adapter import TelegramGateway
from gateways.whatsapp_adapter import WhatsAppGateway

app = Flask(__name__)

# Instanciar gateways
whatsapp_gateway = WhatsAppGateway()
telegram_gateway = TelegramGateway()

@app.route('/')
def index():
    """Página principal com opções de teste"""
    return '''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cleudocodebot - Sistema de Comunicação Multicanal</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            .card {
                background-color: #ecf0f1;
                padding: 20px;
                margin: 15px 0;
                border-radius: 5px;
                border-left: 5px solid #3498db;
            }
            .btn {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            .btn:hover {
                background-color: #2980b9;
            }
            input[type="text"], textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin: 5px 0;
            }
            .status {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
            }
            .success { background-color: #d4edda; color: #155724; }
            .error { background-color: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Cleudocodebot - Sistema de Comunicação Multicanal</h1>
            
            <div class="card">
                <h2>📡 Status do Sistema</h2>
                <p><strong>ID da Instância WhatsApp:</strong> ''' + str(settings.WHATSAPP_ID_INSTANCE) + '''</p>
                <p><strong>API Key Configurada:</strong> ''' + ('Sim' if settings.AUTHENTICATION_API_KEY else 'Não') + '''</p>
                <p><strong>Telegram Bots:</strong> 2 ativos</p>
            </div>
            
            <div class="card">
                <h2>💬 Enviar Mensagem via WhatsApp</h2>
                <form id="whatsappForm">
                    <label>Número (formato internacional):</label>
                    <input type="text" id="whatsappNumber" placeholder="Ex: 5588999999999" required>
                    <label>Mensagem:</label>
                    <textarea id="whatsappMessage" rows="4" placeholder="Digite sua mensagem aqui..." required></textarea>
                    <button type="submit" class="btn">Enviar via WhatsApp</button>
                </form>
                <div id="whatsappResult"></div>
            </div>
            
            <div class="card">
                <h2>🤖 Enviar Mensagem via Telegram</h2>
                <form id="telegramForm">
                    <label>ID do Chat:</label>
                    <input type="text" id="telegramChatId" placeholder="Ex: 123456789" required>
                    <label>Mensagem:</label>
                    <textarea id="telegramMessage" rows="4" placeholder="Digite sua mensagem aqui..." required></textarea>
                    <button type="submit" class="btn">Enviar via Telegram</button>
                </form>
                <div id="telegramResult"></div>
            </div>
            
            <div class="card">
                <h2>🔄 Encaminhar Mensagem entre Canais</h2>
                <form id="forwardForm">
                    <label>Origem:</label>
                    <select id="originChannel">
                        <option value="whatsapp">WhatsApp</option>
                        <option value="telegram">Telegram</option>
                    </select>
                    <label>Destino:</label>
                    <select id="destinationChannel">
                        <option value="telegram">Telegram</option>
                        <option value="whatsapp">WhatsApp</option>
                    </select>
                    <label>ID de Origem:</label>
                    <input type="text" id="originId" placeholder="ID do contato/canal de origem" required>
                    <label>ID de Destino:</label>
                    <input type="text" id="destinationId" placeholder="ID do contato/canal de destino" required>
                    <label>Mensagem:</label>
                    <textarea id="forwardMessage" rows="4" placeholder="Mensagem a ser encaminhada" required></textarea>
                    <button type="submit" class="btn">Encaminhar Mensagem</button>
                </form>
                <div id="forwardResult"></div>
            </div>
            
            <div class="card">
                <h2>📋 Mensagem de Boas-Vindas</h2>
                <p>Esta é a mensagem que será enviada automaticamente para novos contatos:</p>
                <pre>!!! 👋 Olá, Seja bem-vindo(a) ao nosso canal!

🚀 Aqui você terá acesso a soluções inteligentes, automações e novidades para revolucionar seu atendimento.

Nome do cliente: {nome_do_cliente}
Telefone do cliente: {numero_do_cliente}</pre>
            </div>
        </div>
        
        <script>
            // Função para enviar mensagem via WhatsApp
            document.getElementById('whatsappForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const number = document.getElementById('whatsappNumber').value;
                const message = document.getElementById('whatsappMessage').value;
                
                fetch('/send_whatsapp', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        number: number,
                        message: message
                    })
                })
                .then(response => response.json())
                .then(data => {
                    const resultDiv = document.getElementById('whatsappResult');
                    if (data.success) {
                        resultDiv.innerHTML = '<div class="status success">✅ Mensagem enviada com sucesso!</div>';
                    } else {
                        resultDiv.innerHTML = '<div class="status error">❌ Erro: ' + data.error + '</div>';
                    }
                });
            });
            
            // Função para enviar mensagem via Telegram
            document.getElementById('telegramForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const chatId = document.getElementById('telegramChatId').value;
                const message = document.getElementById('telegramMessage').value;
                
                fetch('/send_telegram', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        chat_id: chatId,
                        message: message
                    })
                })
                .then(response => response.json())
                .then(data => {
                    const resultDiv = document.getElementById('telegramResult');
                    if (data.success) {
                        resultDiv.innerHTML = '<div class="status success">✅ Mensagem enviada com sucesso!</div>';
                    } else {
                        resultDiv.innerHTML = '<div class="status error">❌ Erro: ' + data.error + '</div>';
                    }
                });
            });
            
            // Função para encaminhar mensagem
            document.getElementById('forwardForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const originChannel = document.getElementById('originChannel').value;
                const destinationChannel = document.getElementById('destinationChannel').value;
                const originId = document.getElementById('originId').value;
                const destinationId = document.getElementById('destinationId').value;
                const message = document.getElementById('forwardMessage').value;
                
                fetch('/forward_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        origin_channel: originChannel,
                        destination_channel: destinationChannel,
                        origin_id: originId,
                        destination_id: destinationId,
                        message: message
                    })
                })
                .then(response => response.json())
                .then(data => {
                    const resultDiv = document.getElementById('forwardResult');
                    if (data.success) {
                        resultDiv.innerHTML = '<div class="status success">🔄 Mensagem encaminhada com sucesso!</div>';
                    } else {
                        resultDiv.innerHTML = '<div class="status error">❌ Erro: ' + data.error + '</div>';
                    }
                });
            });
        </script>
    </body>
    </html>
    '''

@app.route('/send_whatsapp', methods=['POST'])
def send_whatsapp():
    """Enviar mensagem via WhatsApp"""
    try:
        data = request.json
        number = data.get('number')
        message = data.get('message')
        
        # Enviar mensagem via gateway do WhatsApp
        result = whatsapp_gateway.send_message(number, message)
        
        if result:
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Falha ao enviar mensagem via WhatsApp. Verifique se a instância está conectada e as credenciais estão corretas nos logs.'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/send_telegram', methods=['POST'])
def send_telegram():
    """Enviar mensagem via Telegram"""
    try:
        data = request.json
        chat_id = data.get('chat_id')
        message = data.get('message')
        
        # Enviar mensagem via gateway do Telegram
        result = telegram_gateway.send_message(chat_id, message)
        
        if result:
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Falha ao enviar mensagem via Telegram. Verifique o Token do Bot e Chat ID.'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/forward_message', methods=['POST'])
def forward_message():
    """Encaminhar mensagem entre canais"""
    try:
        data = request.json
        origin_channel = data.get('origin_channel')
        destination_channel = data.get('destination_channel')
        origin_id = data.get('origin_id')
        destination_id = data.get('destination_id')
        message = data.get('message')
        
        # Primeiro, obter a mensagem do canal de origem (simulado)
        # Em um sistema real, isso viria do webhook do canal de origem
        
        # Depois, enviar para o canal de destino
        if destination_channel == 'whatsapp':
            result = whatsapp_gateway.send_message(destination_id, message)
        elif destination_channel == 'telegram':
            result = telegram_gateway.send_message(destination_id, message)
        else:
            return jsonify({
                'success': False,
                'error': 'Canal de destino inválido'
            })
        
        if result:
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Falha ao encaminhar mensagem para {destination_channel}.'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/status')
def status():
    """Retorna status do sistema"""
    return jsonify({
        'whatsapp_gateway': {
            'configured': bool(whatsapp_gateway.id_instance),
            'id_instance': whatsapp_gateway.id_instance,
            'running': whatsapp_gateway.running
        },
        'telegram_gateway': {
            'configured': True,
            'running': True
        },
        'system': 'operational'
    })

if __name__ == '__main__':
    print("Iniciando servidor web para testes...")
    print("Acesse http://localhost:5000 para testar o sistema")
    print("Credenciais do WhatsApp configuradas:")
    print(f"  - ID Instance: {settings.WHATSAPP_ID_INSTANCE}")
    print(f"  - API Key: {'Configurada' if settings.AUTHENTICATION_API_KEY else 'Não configurada'}")
    
    app.run(debug=False, host='0.0.0.0', port=5000)