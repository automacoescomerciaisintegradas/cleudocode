import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseGateway(ABC):
    def __init__(self, name):
        self.name = name
        self.running = False
        self.callback = None

    def set_callback(self, callback):
        """Define a função que processará as mensagens recebidas."""
        self.callback = callback

    @abstractmethod
    def start(self):
        """Inicia o gateway."""
        pass

    @abstractmethod
    def stop(self):
        """Para o gateway."""
        pass

    @abstractmethod
    def send_message(self, recipient_id, message, **kwargs):
        """Envia mensagem para o destino."""
        pass

    def incoming_message(self, sender_id, content, metadata=None):
        """Ponto de entrada para mensagens vindas do canal."""
        if self.callback:
            payload = {
                "gateway": self.name,
                "sender_id": sender_id,
                "content": content,
                "metadata": metadata or {}
            }
            self.callback(payload)
        else:
            logger.warning(f"[{self.name}] Callback não definido. Mensagem ignorada.")
