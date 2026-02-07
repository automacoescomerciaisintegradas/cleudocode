import logging
import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from gateways.base import BaseGateway
from core.config import settings

logger = logging.getLogger(__name__)

class SlackGateway(BaseGateway):
    def __init__(self):
        super().__init__("Slack")
        self.app_token = settings.get("SLACK_APP_TOKEN")
        self.bot_token = settings.get("SLACK_BOT_TOKEN")
        self.app = None
        self.handler = None
        self.listen_thread = None

    def start(self):
        if not self.app_token or not self.bot_token:
            logger.warning("[Slack] Tokens não configurados (SLACK_APP_TOKEN, SLACK_BOT_TOKEN). Ignorando gateway.")
            return

        self.running = True
        
        # Inicializa o app do Slack
        self.app = App(token=self.bot_token)
        
        # Adiciona handler para mensagens
        @self.app.event("message")
        def handle_message(event, say):
            if "subtype" not in event:  # Evita eventos como 'bot_message'
                user_id = event.get("user", "")
                text = event.get("text", "")
                
                logger.debug(f"[Slack] Mensagem de {user_id}: {text}")
                
                # Envia para o router
                self.incoming_message(
                    sender_id=user_id,
                    content=text,
                    metadata={
                        "channel": event.get("channel"),
                        "timestamp": event.get("ts")
                    }
                )
        
        # Inicia o handler em uma thread separada
        self.handler = SocketModeHandler(self.app, self.app_token)
        self.listen_thread = threading.Thread(target=self._run_handler, daemon=True)
        self.listen_thread.start()
        
        logger.info("[Slack] Gateway iniciado.")

    def _run_handler(self):
        try:
            self.handler.start()
        except Exception as e:
            logger.error(f"[Slack] Erro ao iniciar handler: {e}")

    def stop(self):
        logger.info("[Slack] Parando gateway...")
        self.running = False
        if self.handler:
            # O SocketModeHandler não tem método direto para parar, 
            # mas a thread daemon será encerrada automaticamente
            pass

    def send_message(self, recipient_id: str, message: str, **kwargs):
        if not self.app or not self.running:
            logger.error("[Slack] Gateway não está rodando.")
            return
            
        try:
            # Envia mensagem para o canal ou usuário especificado
            self.app.client.chat_postMessage(
                channel=recipient_id,
                text=message
            )
        except Exception as e:
            logger.error(f"[Slack] Erro ao enviar mensagem: {e}")