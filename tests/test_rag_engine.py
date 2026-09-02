"""Testes da memória semântica (rag_engine.py) — foco na conversão numpy -> list.

Regressão: o DefaultEmbeddingFunction do ChromaDB retorna numpy array, e o
truthiness check em array com mais de um elemento levanta ValueError. O
_generate_embedding deve devolver lista de floats.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from rag_engine import RAGBrain


def _fake_brain():
    """RAGBrain sem abrir ChromaDB (evita concorrência com o daemon rodando)."""
    return RAGBrain.__new__(RAGBrain)


def test_generate_embedding_converte_numpy_para_lista():
    brain = _fake_brain()
    # Reproduz o caso real: np.float32 dentro do array retornado pelo chromadb.
    brain.local_ef = lambda texts: np.array([[np.float32(0.1), np.float32(0.2), np.float32(0.3)]])

    vec = brain._generate_embedding("teste")

    assert isinstance(vec, list), f"esperava list, veio {type(vec)}"
    # float32(0.1) != 0.1 exato: compara com arredondamento
    assert [round(v, 6) for v in vec] == [0.1, 0.2, 0.3]
    assert all(isinstance(v, float) for v in vec), "elementos devem ser float nativo"


class FakeCollection:
    """Registra add() e devolve os documentos gravados em query()."""

    def __init__(self):
        self.added = None

    def add(self, ids, embeddings, metadatas, documents):
        self.added = {
            "ids": ids,
            "embeddings": embeddings,
            "metadatas": metadatas,
            "documents": documents,
        }

    def query(self, query_embeddings, n_results):
        return {
            "documents": [self.added["documents"]],
            "metadatas": [self.added["metadatas"]],
        }


def test_add_document_e_search_funcionam_com_embedding_numpy():
    brain = _fake_brain()
    brain.collection = FakeCollection()
    brain.local_ef = lambda texts: np.array([[np.float32(0.1), np.float32(0.2), np.float32(0.3)]] * len(texts))

    ok, msg = brain.add_document("conteúdo de teste para a memória", "teste.txt", "conversation")
    assert ok, msg
    # embebdings persistidos como lista de floats nativos, não numpy
    stored = brain.collection.added["embeddings"]
    assert [round(v, 6) for v in stored[0]] == [0.1, 0.2, 0.3]
    assert all(isinstance(v, float) for v in stored[0])

    snippets = brain.search("teste")
    assert snippets, "busca não retornou o documento gravado"
    assert "teste.txt" in snippets[0]


def test_search_retorna_vazio_sem_collection():
    brain = _fake_brain()
    brain.collection = None
    assert brain.search("qualquer") == []


_TESTS = [
    test_generate_embedding_converte_numpy_para_lista,
    test_add_document_e_search_funcionam_com_embedding_numpy,
    test_search_retorna_vazio_sem_collection,
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
