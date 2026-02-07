import threading
import sys
from gateways.base import BaseGateway

class CLIGateway(BaseGateway):
    """
    Gateway de Linha de Comando para testes locais.
    Lê do stdin e imprime no stdout.
    """
    def __init__(self):
        super().__init__("CLI")
        self.listen_thread = None

    def start(self):
        self.running = True
        self.listen_thread = threading.Thread(target=self._input_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        print(">> CLI Gateway Iniciado. Digite sua mensagem e pressione Enter:")

    def stop(self):
        self.running = False
        # Thread vai morrer sozinha pois é daemon, ou podemos tentar join se tiver mecanismo de exit

    def send_message(self, recipient_id: str, message: str, **kwargs):
        # Simplesmente printa a resposta
        print(f"\n[Bot]: {message}\n>> ", end="", flush=True)

    def _input_loop(self):
        while self.running:
            try:
                # O input() bloqueia, então isso é apenas para dev local
                user_input = input()
                if user_input.strip():
                    self.incoming_message("console_user", user_input)
            except EOFError:
                self.running = False
            except Exception as e:
                print(f"[CLI Error] {e}")
