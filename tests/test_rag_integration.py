"""Testes da integração RAG na camada de cognição (orchestrator.py).

Roda com pytest (`pytest tests/test_rag_integration.py -v`) ou standalone
(`python tests/test_rag_integration.py`).
"""

import os
import sys
import time
from pathlib import Path

# Garante o projeto na raiz do path (scripts em tests/ rodam de qualquer cwd)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Desativa o RAG real ANTES do import: o módulo cria o singleton Orchestrator
# no import e ele não deve abrir o ChromaDB real durante os testes.
os.environ["RAG_ENABLED"] = "false"

import orchestrator as orchestrator_module
from orchestrator import Orchestrator


class StubBrain:
    """Substituto da memória semântica: registra buscas e gravações."""

    def __init__(self, snippets=None):
        self.snippets = snippets if snippets is not None else [
            "[Fonte: manual.txt]\nConteúdo relevante A",
            "[Fonte: manual.txt]\nConteúdo relevante B",
        ]
        self.searches = []
        self.stored = []

    def search(self, query, n_results=3):
        self.searches.append(query)
        return self.snippets

    def add_document(self, content, filename, doc_type):
        self.stored.append({"content": content, "filename": filename, "doc_type": doc_type})


def _make_orch():
    """Orquestrador isolado: sem memória real e com state_file temporário."""
    orch = Orchestrator()
    orch.brain = None
    orch.state_file = Path(f"/tmp/test_agent_status_{time.time_ns()}.json")
    return orch


# -- Recuperação (search) ----------------------------------------------------

def test_search_memory_sem_brain_retorna_none():
    orch = _make_orch()
    assert orch.brain is None
    assert orch._search_memory("oi") is None


def test_search_memory_formata_snippets():
    orch = _make_orch()
    orch.brain = StubBrain()

    ctx = orch._search_memory("como configuro o whatsapp?")

    assert ctx is not None
    assert "Conteúdo relevante encontrado na memória" in ctx
    assert "Conteúdo relevante A" in ctx
    assert "Conteúdo relevante B" in ctx
    assert orch.brain.searches == ["como configuro o whatsapp?"]


def test_search_memory_sem_resultados_retorna_none():
    orch = _make_orch()
    orch.brain = StubBrain(snippets=[])

    assert orch._search_memory("nada aqui") is None


# -- Armazenamento (store) ---------------------------------------------------

def test_store_memory_sem_brain_nao_falha():
    orch = _make_orch()
    orch._store_memory("conteúdo qualquer")  # não deve levantar


def test_store_memory_grava_interacao():
    orch = _make_orch()
    orch.brain = StubBrain()

    orch._store_memory("Usuário: oi\n\nResposta: olá", "conversation")

    assert len(orch.brain.stored) == 1
    assert orch.brain.stored[0]["doc_type"] == "conversation"
    assert "Usuário: oi" in orch.brain.stored[0]["content"]


# -- Fluxo completo: receive_message ------------------------------------------

def test_receive_message_injeta_contexto_e_armazena():
    orch = _make_orch()
    orch.brain = StubBrain()
    calls = {}

    def fake_query(messages, model=None, provider=None, temperature=0.7, **kwargs):
        calls["messages"] = messages
        return "resposta do agente"

    original = orchestrator_module.llm_hub.query
    orchestrator_module.llm_hub.query = fake_query
    try:
        result = orch.receive_message({"text": "como configuro o whatsapp?"})
    finally:
        orchestrator_module.llm_hub.query = original

    assert result["status"] == "success"

    user_msg = calls["messages"][1]["content"]
    assert "Conteúdo relevante encontrado na memória" in user_msg
    assert "Conteúdo relevante A" in user_msg
    assert "Usuário: como configuro o whatsapp?" in user_msg

    # a interação foi gravada na memória
    assert len(orch.brain.stored) == 1
    assert "resposta do agente" in orch.brain.stored[0]["content"]
    assert orch.brain.stored[0]["doc_type"] == "conversation"


def test_receive_message_sem_memoria_nao_injeta():
    orch = _make_orch()  # brain = None
    calls = {}

    def fake_query(messages, model=None, provider=None, temperature=0.7, **kwargs):
        calls["messages"] = messages
        return "ok"

    original = orchestrator_module.llm_hub.query
    orchestrator_module.llm_hub.query = fake_query
    try:
        result = orch.receive_message({"text": "bom dia"})
    finally:
        orchestrator_module.llm_hub.query = original

    assert result["status"] == "success"
    user_msg = calls["messages"][1]["content"]
    assert "memória" not in user_msg
    assert user_msg == "bom dia"


def test_delegate_task_injeta_contexto():
    orch = _make_orch()
    orch.brain = StubBrain()
    calls = {}

    def fake_query(messages, model=None, provider=None, temperature=0.7, **kwargs):
        calls["messages"] = messages
        return "tarefa feita"

    original = orchestrator_module.llm_hub.query
    orchestrator_module.llm_hub.query = fake_query
    try:
        result = orch.delegate_task("analyst", "analise os dados de vendas")
    finally:
        orchestrator_module.llm_hub.query = original

    assert result["status"] == "success"
    task_msg = calls["messages"][1]["content"]
    assert "Conteúdo relevante encontrado na memória" in task_msg
    assert "Tarefa: analise os dados de vendas" in task_msg


_TESTS = [
    test_search_memory_sem_brain_retorna_none,
    test_search_memory_formata_snippets,
    test_search_memory_sem_resultados_retorna_none,
    test_store_memory_sem_brain_nao_falha,
    test_store_memory_grava_interacao,
    test_receive_message_injeta_contexto_e_armazena,
    test_receive_message_sem_memoria_nao_injeta,
    test_delegate_task_injeta_contexto,
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
