import logging
import threading
import asyncio
import requests
from gateways.base import BaseGateway
from core.config import settings

logger = logging.getLogger(__name__)

class TeamsGateway(BaseGateway):
    """
    Gateway do Microsoft Teams para o Cleudocodebot.
    Usa o Microsoft Graph API para integração com o Teams.
    """
    def __init__(self):
        super().__init__("Teams")
        self.tenant_id = settings.get("TEAMS_TENANT_ID")
        self.client_id = settings.get("TEAMS_CLIENT_ID")
        self.client_secret = settings.get("TEAMS_CLIENT_SECRET")
        self.bot_app_id = settings.get("TEAMS_BOT_APP_ID")
        self.bot_app_password = settings.get("TEAMS_BOT_APP_PASSWORD")
        self.service_url = settings.get("TEAMS_SERVICE_URL", "https://smba.trafficmanager.net/")
        self.access_token = None
        self.listen_thread = None

    def start(self):
        self.running = True
        logger.info("[Teams] Gateway iniciado.")
        
        if not all([self.tenant_id, self.client_id, self.client_secret, 
                   self.bot_app_id, self.bot_app_password]):
            logger.warning("[Teams] Credenciais incompletas. Usando modo simulação.")
            return

        try:
            # Obter token de acesso
            self._get_access_token()
            
            # Iniciar thread para escutar mensagens
            self.listen_thread = threading.Thread(target=self._listen_for_messages, daemon=True)
            self.listen_thread.start()
            
            logger.info("[Teams] Gateway iniciado com sucesso.")
        except Exception as e:
            logger.error(f"[Teams] Erro ao iniciar gateway: {e}")

    def _get_access_token(self):
        """Obtém token de acesso para o Microsoft Graph API"""
        try:
            url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default'
            }
            
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                logger.info("[Teams] Token de acesso obtido com sucesso.")
            else:
                logger.error(f"[Teams] Falha ao obter token de acesso: {response.text}")
        except Exception as e:
            logger.error(f"[Teams] Erro ao obter token de acesso: {e}")

    def _listen_for_messages(self):
        """Thread para escutar mensagens recebidas (implementação simplificada)"""
        import time
        while self.running:
            try:
                # Em uma implementação completa, esta função escutaria por webhooks ou polling
                # Por enquanto, mantemos a thread ativa
                time.sleep(10)
            except Exception as e:
                logger.error(f"[Teams] Erro na thread de escuta: {e}")
                break

    def stop(self):
        logger.info("[Teams] Parando gateway...")
        self.running = False
        logger.info("[Teams] Gateway parado.")

    def send_message(self, recipient_id: str, message: str, **kwargs):
        if not self.access_token or not self.running:
            logger.error("[Teams] Gateway não está rodando ou não está configurado.")
            # Em modo simulação, mostra a mensagem
            logger.info(f"[Teams SIM] Enviando para {recipient_id}: {message[:50]}...")
            print(f"\n[TEAMS OUTGOING TO {recipient_id}]: {message}\n")
            return

        try:
            # Preparar payload para enviar mensagem
            url = f"{self.service_url}v3/conversations/{recipient_id}/activities"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'type': 'message',
                'text': message
            }
            
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code in [200, 201, 202]:
                logger.info(f"[Teams] Mensagem enviada com sucesso para {recipient_id}")
            else:
                logger.error(f"[Teams] Falha ao enviar mensagem: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"[Teams] Erro ao enviar mensagem: {e}")
            # Fallback para modo simulação
            logger.info(f"[Teams SIM] Enviando para {recipient_id}: {message[:50]}...")
            print(f"\n[TEAMS OUTGOING TO {recipient_id}]: {message}\n")

    def handle_incoming_message(self, message_data):
        """Lida com mensagem recebida via webhook (chamado externamente)"""
        try:
            sender_id = message_data.get('from', {}).get('id', '')
            content = message_data.get('text', '')
            conversation_id = message_data.get('conversation', {}).get('id', '')
            
            if content:
                logger.debug(f"[Teams] Mensagem recebida de {sender_id} ({conversation_id}): {content}")
                
                # Envia para o router
                self.incoming_message(
                    sender_id=sender_id,
                    content=content,
                    metadata={
                        "conversation_id": conversation_id,
                        "service_url": message_data.get('serviceUrl'),
                        "channel_id": message_data.get('channelId')
                    }
                )
        except Exception as e:
            logger.error(f"[Teams] Erro ao processar mensagem recebida: {e}")