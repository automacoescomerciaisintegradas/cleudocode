import logging
import threading
import time
import workflow_manager

from core.message_pipeline import MessagePipeline, MessageValidationError, InboundMessage


class CleudoDaemon:
    def __init__(self, pipeline_config=None):
        self.gateways = []
        self.running = False
        self.config = {}
        # Borda: entrada unificada + validação + fila com workers limitados.
        # O processamento roda em _process_message, dentro dos workers.
        # Late binding: _process_message é resolvido na chamada, permitindo
        # subclasse/monkeypatch sem reconstruir o pipeline.
        self.pipeline = MessagePipeline(handler=lambda msg: self._process_message(msg), config=pipeline_config)

    def get_gateways_status(self):
        return [
            {"name": gw.name, "running": getattr(gw, "running", False), "type": gw.__class__.__name__}
            for gw in self.gateways
        ]

    def stop(self):
        self.running = False
        self.pipeline.stop()
        logging.info("Parando Daemon (soft stop)...")

    def add_gateway(self, gateway):
        gateway.set_callback(self.handle_message)
        self.gateways.append(gateway)
        logging.info(f"Gateway {gateway.name} adicionado.")

    def start(self):
        if self.running:
            return

        logging.info("--- Iniciando Daemon Cleudocode --")
        self.running = True

        # Inicia os workers da borda (fila de mensagens)
        self.pipeline.start()

        # Iniciar Gateways
        for gw in self.gateways:
            self._start_gateway_thread(gw)

    def _start_gateway_thread(self, gw):
        def runner():
            try:
                logging.info(f"Iniciando thread para {gw.name}...")
                gw.set_callback(self.handle_message)
                gw.start()
            except Exception as e:
                logging.error(f"Falha ao iniciar gateway {gw.name}: {e}")

        t = threading.Thread(target=runner, daemon=True, name=f"gw-{gw.name}")
        t.start()

    def handle_message(self, data_or_msg, sender_id=None, source_name=None):
        """
        Ponto de entrada único (Borda): normaliza, valida e enfileira.
        Suporta tanto assinatura antiga (msg, sender, source) quanto nova (payload dict).
        A execução real acontece nos workers da borda (_process_message).
        """
        if isinstance(data_or_msg, dict) and 'content' in data_or_msg:
            # Assinatura BaseGateway (payload único)
            message = data_or_msg.get('content')
            sender_id = data_or_msg.get('sender_id')
            source_name = data_or_msg.get('gateway')
            metadata = data_or_msg.get('metadata') or {}
        else:
            # Assinatura Legacy ou direta
            message = data_or_msg
            metadata = {}

        try:
            message_id = self.pipeline.submit(
                content=message,
                sender_id=sender_id,
                channel=source_name or "direct",
                metadata=metadata,
            )
        except MessageValidationError as e:
            logging.warning(f"Mensagem rejeitada na borda: {e}")
            return {"accepted": False, "reason": str(e)}

        logging.info(f"msg aceita [{source_name}] {sender_id}: {message_id}")
        return {"accepted": True, "message_id": message_id}

    def _process_message(self, msg: InboundMessage):
        """
        Roteamento da mensagem, executado em um worker da borda.
        Substitui o antigo `threading.Thread` por mensagem: agora a concorrência
        é limitada pelos workers da fila.
        """
        message = msg.content
        sender_id = msg.sender_id
        source_name = msg.channel

        logging.info(f"msg << [{source_name}] {sender_id}: {message}")

        # Interceptador de Workflows (Lobster Engine)
        if message.lower().startswith("/run ") or "executar workflow" in message.lower():
            wf_name = message.replace("/run ", "").replace("executar workflow", "").strip()
            logging.info(f"🚀 Disparando workflow: {wf_name}")
            try:
                success = workflow_manager.executar_workflow(wf_name)
                status = "concluído com sucesso" if success else "falhou"
                logging.info(f"🏁 Workflow {wf_name} {status}.")
            except Exception as e:
                logging.error(f"❌ Erro ao executar workflow {wf_name}: {e}")
            return

        # 2. Ponte Telegram -> WhatsApp (Exemplo: /zap 5511999999999 Mensagem)
        if message.lower().startswith(("/zap ", "/wa ")):
            parts = message.split(" ", 2)
            if len(parts) >= 3:
                target_number = parts[1].replace("+", "").replace("-", "").strip()
                text_to_send = parts[2]

                logging.info(f"🌉 Ponte detectada: Enviando para WhatsApp {target_number}...")

                # Localiza gateway de WhatsApp
                wa_gw = next((g for g in self.gateways if "whatsapp" in g.name.lower()), None)
                if wa_gw:
                    success = wa_gw.send_message(target_number, text_to_send)
                    if success:
                        status_msg = f"✅ Mensagem enviada para WhatsApp ({target_number})"
                    else:
                        status_msg = "❌ Erro ao enviar para WhatsApp. Verifique se a instância está conectada."
                else:
                    status_msg = "⚠️ Gateway WhatsApp não está ativo ou configurado."

                # Opcional: Responder de volta para a origem (ex: Telegram)
                origin_gw = next((g for g in self.gateways if g.name.lower() == source_name.lower()), None)
                if origin_gw and hasattr(origin_gw, 'send_message'):
                    origin_gw.send_message(sender_id, status_msg)
                return

        # 3. Lógica de Resposta via Orquestrador (Mission Control)
        if not message.startswith("/"):
            try:
                from orchestrator import orchestrator

                logging.info(f"🧠 Passando para o Orquestrador: {sender_id}")
                result = orchestrator.receive_message({"text": message, "from": sender_id})

                # Extrai a resposta (seja do Jarvis ou de um agente delegado)
                if result.get("status") == "success":
                    res_data = result.get("result", {})
                    ai_response = res_data.get("output") or res_data.get("agent_output")

                    if not ai_response:
                        ai_response = "A missão foi processada, mas não houve retorno textual direto."

                    # Localiza gateway de origem para responder
                    origin_gw = next((g for g in self.gateways if g.name.lower() == source_name.lower()), None)
                    if origin_gw and hasattr(origin_gw, 'send_message'):
                        origin_gw.send_message(sender_id, ai_response)
                        logging.info(f"📤 Resposta orquestrada enviada via {source_name}")
            except Exception as e:
                logging.error(f"❌ Erro na orquestração: {e}")

        return
