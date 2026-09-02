"""Camada de Borda: entrada unificada, validação e enfileiramento de mensagens.

Fluxo de entrada:
    canal (gateway/webhook/API) -> MessagePipeline.submit() -> MessageValidator
    -> fila -> workers -> handler

A borda é a única porta de entrada do sistema. Os canais não conhecem o
orquestrador nem os workflows: entregam aqui e recebem um message_id.
O handler (camada de processamento) roda em um worker com concorrência
limitada; falhas transitórias são reenviadas com backoff exponencial.
"""

import logging
import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# Limites padrão da borda. Sobrescrevíveis no construtor via config.
DEFAULT_MAX_MESSAGE_LENGTH = 4096
DEFAULT_MAX_QUEUE_SIZE = 1000
DEFAULT_MAX_WORKERS = 4
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE_SECONDS = 0.5


class MessageValidationError(Exception):
    """Mensagem rejeitada pela validação da borda."""


class TransientProcessingError(Exception):
    """Falha temporária no handler: a mensagem deve ser reenviada com backoff."""


@dataclass
class InboundMessage:
    """Mensagem normalizada que cruza a borda até a fila."""

    message_id: str
    content: str
    channel: str
    sender_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    received_at: float = field(default_factory=time.time)


class MessageValidator:
    """Valida mensagens na entrada, antes do enfileiramento."""

    def __init__(
        self,
        max_message_length: int = DEFAULT_MAX_MESSAGE_LENGTH,
        allowed_channels: Optional[list] = None,
    ):
        self.max_message_length = max_message_length
        self.allowed_channels = set(allowed_channels) if allowed_channels else None

    def validate(self, message: InboundMessage) -> None:
        if not message.content or not message.content.strip():
            raise MessageValidationError("mensagem vazia")
        if len(message.content) > self.max_message_length:
            raise MessageValidationError(
                f"mensagem excede o limite de {self.max_message_length} caracteres"
            )
        if self.allowed_channels is not None and message.channel not in self.allowed_channels:
            raise MessageValidationError(f"canal '{message.channel}' não permitido")


class MessagePipeline:
    """Borda do sistema: entrada unificada -> validação -> fila -> workers.

    - submit(): valida e enfileira; devolve o message_id ou levanta
      MessageValidationError com o motivo da rejeição.
    - Os workers consomem a fila com concorrência limitada e chamam handler(msg).
    - TransientProcessingError do handler é reenviado com backoff até
      max_retries; as demais exceções são logadas e descartadas.
    - Se ainda não iniciado, o pipeline inicia sozinho no primeiro submit()
      (comportamento equivalente ao daemon antigo, que processava sem start()).
    """

    def __init__(
        self,
        handler: Callable[[InboundMessage], None],
        config: Optional[Dict[str, Any]] = None,
    ):
        self.handler = handler
        cfg = config or {}
        self.validator = MessageValidator(
            max_message_length=cfg.get("max_message_length", DEFAULT_MAX_MESSAGE_LENGTH),
            allowed_channels=cfg.get("allowed_channels"),
        )
        self.queue: "queue.Queue[InboundMessage]" = queue.Queue(
            maxsize=cfg.get("max_queue_size", DEFAULT_MAX_QUEUE_SIZE)
        )
        self.max_workers = cfg.get("max_workers", DEFAULT_MAX_WORKERS)
        self.max_retries = cfg.get("max_retries", DEFAULT_MAX_RETRIES)
        self.backoff_base = cfg.get("backoff_base_seconds", DEFAULT_BACKOFF_BASE_SECONDS)
        self._workers: list = []
        self._lock = threading.Lock()
        self._running = False
        self._stats_lock = threading.Lock()
        self.stats: Dict[str, int] = {
            "submitted": 0,
            "rejected": 0,
            "processed": 0,
            "failed": 0,
            "retried": 0,
        }

    # -- Ciclo de vida -------------------------------------------------------

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._running = True
            for i in range(self.max_workers):
                t = threading.Thread(
                    target=self._worker_loop,
                    name=f"edge-worker-{i}",
                    daemon=True,
                )
                t.start()
                self._workers.append(t)
        logger.info("MessagePipeline iniciado com %d workers.", self.max_workers)

    def stop(self, timeout: float = 5.0) -> None:
        with self._lock:
            if not self._running:
                return
            self._running = False
        for t in self._workers:
            t.join(timeout=timeout)
        self._workers.clear()
        logger.info("MessagePipeline parado.")

    # -- Entrada -------------------------------------------------------------

    def submit(
        self,
        content: str,
        sender_id: str = "",
        channel: str = "direct",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Valida e enfileira uma mensagem; devolve o message_id."""
        if not self._running:
            self.start()
        message = InboundMessage(
            message_id=uuid.uuid4().hex[:16],
            content=content,
            channel=channel,
            sender_id=sender_id or "desconhecido",
            metadata=metadata or {},
        )
        try:
            self.validator.validate(message)
        except MessageValidationError:
            self._bump("rejected")
            raise
        try:
            self.queue.put_nowait(message)
        except queue.Full:
            self._bump("rejected")
            raise MessageValidationError("fila cheia: tente novamente mais tarde")
        self._bump("submitted")
        logger.debug(
            "msg enfileirada [%s] %s: %s", message.channel, message.sender_id, message.message_id
        )
        return message.message_id

    # -- Processamento -------------------------------------------------------

    def _worker_loop(self) -> None:
        while self._running:
            try:
                message = self.queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                self._handle_with_retry(message)
            finally:
                self.queue.task_done()

    def _handle_with_retry(self, message: InboundMessage) -> None:
        attempts = 0
        while True:
            try:
                self.handler(message)
                self._bump("processed")
                return
            except TransientProcessingError as exc:
                attempts += 1
                if attempts > self.max_retries:
                    logger.error(
                        "msg %s falhou após %d tentativas: %s", message.message_id, attempts, exc
                    )
                    self._bump("failed")
                    return
                self._bump("retried")
                delay = self.backoff_base * (2 ** (attempts - 1))
                logger.warning(
                    "msg %s falhou (tentativa %d), reenviando em %.1fs: %s",
                    message.message_id,
                    attempts,
                    delay,
                    exc,
                )
                time.sleep(delay)
            except Exception as exc:  # falha permanente: loga e descarta
                logger.error("msg %s falhou e foi descartada: %s", message.message_id, exc)
                self._bump("failed")
                return

    # -- Observabilidade -----------------------------------------------------

    def _bump(self, key: str) -> None:
        with self._stats_lock:
            self.stats[key] += 1

    def pending(self) -> int:
        return self.queue.qsize()
