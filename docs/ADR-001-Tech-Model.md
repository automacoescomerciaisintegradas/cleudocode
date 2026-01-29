# ADR-001: Stack Tecnológico

**Status**: Aceito
**Data**: 2026-01-17

## Contexto
Precisamos selecionar as tecnologias base para o cliente de chat.

## Decisão
Utilizar **Python** com `requests` e `python-dotenv`.

## Justificativa
*   **Simplicidade**: Python é a linguagem franca de IA.
*   **Manutenibilidade**: Mínimas dependências externas.
*   **Portabilidade**: Roda em Windows/Linux/Mac facilmente.

---

# ADR-002: Seleção de Modelo e Gestão de Memória

**Status**: Aceito
**Data**: 2026-01-17

## Contexto
Tentativa inicial de usar `deepseek-coder:6.7b` e posteriormente `qwen2.5:14b`.
O servidor possui **11GB de RAM Total** (sem GPU dedicada para inferência rápida, usando CPU offload).

## Problema
O modelo `qwen2.5:14b` (~9GB) causou **OOM (Out of Memory)** e erro 500 no servidor, pois o sistema operacional + modelo excederam a RAM física disponível.

## Decisão
Padronizar o uso do modelo **`qwen2.5:7b`** (~4.7GB).

## Justificativa
*   O modelo de 7B parâmetros deixa ~3-4GB livres para o Sistema Operacional e buffers.
*   Oferece o melhor equilíbrio entre inteligência e estabilidade no hardware atual.
*   Evita travamentos e falhas de alocação de memória durante inferência.
