"""Testes da camada de Borda: core/message_pipeline.py.

Roda com pytest (`pytest tests/test_message_pipeline.py -v`) ou standalone
(`python tests/test_message_pipeline.py`), seguindo o padrão dos scripts
test_*.py do projeto.
"""

import sys
import time

from core.message_pipeline import (
    MessagePipeline,
    MessageValidationError,
    TransientProcessingError,
)


def _wait_until(predicate, timeout=3.0, interval=0.02):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


def _expect_raises(exc_type, fn, *args, match=None, **kwargs):
    """Executa fn e falha se exc_type não for levantada; valida a mensagem."""
    try:
        fn(*args, **kwargs)
    except exc_type as e:
        if match and match not in str(e):
            raise AssertionError(
                f"Exceção {exc_type.__name__} levantada, mas mensagem '{e}' não contém '{match}'"
            )
        return
    raise AssertionError(f"{exc_type.__name__} não foi levantada")


def test_submit_valida_enfileira_e_processa():
    received = []

    def handler(msg):
        received.append(msg)

    pipe = MessagePipeline(handler=handler, config={"max_workers": 2})

    # Não chamamos start(): o primeiro submit deve iniciar o pipeline sozinho.
    msg_id = pipe.submit(content="olá", sender_id="user1", channel="whatsapp")

    assert msg_id
    assert pipe.stats["submitted"] == 1
    assert _wait_until(lambda: len(received) == 1), "mensagem não processada a tempo"

    assert received[0].content == "olá"
    assert received[0].sender_id == "user1"
    assert received[0].channel == "whatsapp"
    assert received[0].message_id == msg_id
    assert pipe.stats["processed"] == 1

    pipe.stop()


def test_submit_rejeita_mensagem_vazia():
    pipe = MessagePipeline(handler=lambda m: None)

    _expect_raises(MessageValidationError, pipe.submit, content="   ")

    assert pipe.stats["rejected"] == 1
    assert pipe.stats["submitted"] == 0
    assert pipe.pending() == 0

    pipe.stop()


def test_submit_rejeita_mensagem_acima_do_limite():
    pipe = MessagePipeline(handler=lambda m: None, config={"max_message_length": 10})

    _expect_raises(MessageValidationError, pipe.submit, content="x" * 11, match="limite")

    assert pipe.stats["rejected"] == 1

    pipe.stop()


def test_submit_rejeita_canal_nao_permitido():
    pipe = MessagePipeline(
        handler=lambda m: None, config={"allowed_channels": ["whatsapp", "telegram"]}
    )

    _expect_raises(MessageValidationError, pipe.submit, content="oi", channel="discord", match="canal")

    pipe.stop()


def test_handler_levanta_transient_error_e_reenvia_com_backoff():
    calls = {"n": 0}

    def handler(msg):
        calls["n"] += 1
        raise TransientProcessingError("API temporariamente indisponível")

    pipe = MessagePipeline(
        handler=handler, config={"max_retries": 2, "backoff_base_seconds": 0.01}
    )

    pipe.submit(content="oi", sender_id="u", channel="cli")

    # 1 tentativa inicial + 2 retries = 3 chamadas, depois falha definitiva.
    assert _wait_until(lambda: pipe.stats["failed"] == 1), "falha definitiva não registrada"
    assert calls["n"] == 3
    assert pipe.stats["retried"] == 2
    assert pipe.stats["processed"] == 0

    pipe.stop()


def test_handler_levanta_excecao_comum_e_descarta():
    def handler(msg):
        raise RuntimeError("erro permanente")

    pipe = MessagePipeline(handler=handler, config={"max_retries": 3})

    pipe.submit(content="oi", sender_id="u", channel="cli")

    assert _wait_until(lambda: pipe.stats["failed"] == 1), "falha não registrada"
    assert pipe.stats["retried"] == 0  # exceção comum não reenfileira

    pipe.stop()


def test_worker_continua_apos_falha_de_uma_mensagem():
    processed = []

    def handler(msg):
        if msg.content == "quebra":
            raise RuntimeError("boom")
        processed.append(msg.content)

    pipe = MessagePipeline(handler=handler, config={"max_retries": 1})

    pipe.submit(content="quebra", sender_id="u", channel="cli")
    pipe.submit(content="ok", sender_id="u", channel="cli")

    assert _wait_until(lambda: len(processed) == 1), "segunda mensagem não processada"
    assert processed == ["ok"]
    assert pipe.stats["failed"] == 1

    pipe.stop()


_TESTS = [
    test_submit_valida_enfileira_e_processa,
    test_submit_rejeita_mensagem_vazia,
    test_submit_rejeita_mensagem_acima_do_limite,
    test_submit_rejeita_canal_nao_permitido,
    test_handler_levanta_transient_error_e_reenvia_com_backoff,
    test_handler_levanta_excecao_comum_e_descarta,
    test_worker_continua_apos_falha_de_uma_mensagem,
]


def main():
    failures = 0
    for test in _TESTS:
        try:
            test()
            print(f"✅ {test.__name__}")
        except Exception as e:
            failures += 1
            print(f"❌ {test.__name__}: {e}")
    print(f"\n{len(_TESTS) - failures}/{len(_TESTS)} testes passaram")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
