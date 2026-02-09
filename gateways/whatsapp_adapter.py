
import os
import requests
import json
import logging
from .base import BaseGateway

# Configuração de Logger
logger = logging.getLogger(__name__)

class EvolutionGateway(BaseGateway):
    def __init__(self):
        super().__init__("whatsapp_evolution")
        self.base_url = os.getenv("WHATSAPP_BASE_URL", "").rstrip('/')
        self.token = os.getenv("WHATSAPP_API_TOKEN_INSTANCE")
        self.instance_name = os.getenv("WHATSAPP_INSTANCE_NAME", "Cleudocode")
        self.callback = None
        
    def start(self):
        """Inicia o gateway (setup de webhooks seria aqui se necessário)"""
        if not self.token or not self.base_url:
            logger.error("WhatsApp Gateway não iniciado: URL ou Token ausentes.")
            return

        logger.info(f"Iniciando Evolution API Gateway para instância: {self.instance_name}")
        # Opcional: Verificar status da instância ao iniciar
        self.check_status()

    def check_status(self):
        """Verifica conexão com a Evolution API"""
        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
            headers = {
                "apikey": self.token,
                "Content-Type": "application/json"
            }
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                state = data.get('instance', {}).get('state', 'unknown')
                logger.info(f"Status do WhatsApp: {state}")
                if state == 'close':
                    logger.warning("WhatsApp desconectado! Escaneie o QR Code no painel da Evolution.")
            else:
                logger.error(f"Erro ao checar status: {resp.status_code}")
        except Exception as e:
            logger.error(f"Falha ao conectar na Evolution API: {e}")

    def stop(self):
        """Para o gateway (interface abstrata)"""
        logger.info(f"Parando gateway Evolution: {self.instance_name}")
        # Se tivéssemos websockets, fecharíamos aqui
        pass

    def send_message(self, chat_id, text, **kwargs):
        """Envia mensagem de texto"""
        if not self.base_url or not self.token:
            logger.error("Tentativa de envio sem configuração válida.")
            return False

        # Endpoint de envio de texto da Evolution API (v1.6+)
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        
        payload = {
            "number": chat_id, # Evolution usa 'number' (ex: 5511999999999)
            "text": text,
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": True
            }
        }
        
        headers = {
            "apikey": self.token,
            "Content-Type": "application/json"
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code in [200, 201]:
                logger.info(f"Mensagem enviada para {chat_id}")
                return True
            else:
                logger.error(f"Erro no envio WhatsApp ({resp.status_code}): {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Exceção no envio WhatsApp: {e}")
            return False

    def set_callback(self, callback_func):
        self.callback = callback_func

    def simulate_incoming(self, sender_id, text):
        """Simula o recebimento de uma mensagem para testes internos"""
        logger.info(f"Simulando mensagem recebida de {sender_id}: {text}")
        self.incoming_message(sender_id, text, metadata={"simulated": True})
