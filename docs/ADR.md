# Architecture Decision Record (ADR) - Cleudocode

## 1. Contexto
O Cleudocode evoluiu de um simples wrapper de API para um **Agent Harness** robusto focado em orquestrar agentes de Inteligência Artificial para tarefas de engenharia de software e automação. O objetivo do projeto é desacoplar o modelo lógico (o LLM) do ambiente de execução local (Harness), permitindo múltiplos fluxos, failover automatizado, execução local e controle total do usuário.

## 2. Decisões Arquiteturais

### 2.1. Desacoplamento do LLM e OmniRoute (Fallback Router)
- **Decisão:** Implementar um roteador de LLMs (`core/llm_providers.py`) que suporta provedores variados (Anthropic, OpenAI, OpenRouter, Google, Groq, Z.AI, Moonshot, Ollama).
- **Justificativa:** APIs de IA frequentemente falham por limite de cota (429), timeouts ou falhas internas (500). O mecanismo de *fallback* automático garante alta disponibilidade da CLI. Se o provedor primário falhar, a requisição flui automaticamente para o próximo na fila.

### 2.2. Orquestração Multi-Agente (Mission Control)
- **Decisão:** Centralizar a lógica de delegação no `orchestrator.py`. Cada agente é definido por sua persona carregada dinamicamente da pasta `agents/`.
- **Justificativa:** Permite expansão orgânica de novos perfis. O orquestrador (geralmente sob a persona do *Jarvis*) pode usar o comando interno `delegate-task` para repassar uma tarefa a um especialista ou `/debate` para criar um brainstorming (Threaded Discussions) entre múltiplos agentes de forma autônoma.
- **Resolução Recente:** Adicionado tratamento explícito de estados (`idle`, `busy`) no dicionário `agent_status` antes de atualizá-los, prevenindo quebras brutais de `KeyError` na ausência de arquivos `.md` e unificando o controle de estado.

### 2.3. Memória Semântica (RAG)
- **Decisão:** Integrar um motor de busca semântica (RAG Engine) ao orquestrador.
- **Justificativa:** Permite que os agentes resgatem contexto de conversas ou ações executadas em instâncias anteriores sem sobrecarregar a janela de contexto principal do LLM.

### 2.4. Interface Híbrida (CLI TUI + Dashboard Web)
- **Decisão:** O núcleo de interação contínua se dá via CLI interativa, estilizada com a biblioteca `rich` e `click`. Ferramentas gerenciais, acompanhamento de uso e status do esquadrão foram delegadas a um painel web (`web_app.py` / Streamlit).
- **Justificativa:** Um terminal fornece a eficiência que desenvolvedores esperam para o dia a dia. Já o dashboard permite a visualização rica em gráficos e tabelas para telemetria de LLM e debug da fila de roteamento.

### 2.5. Model Context Protocol (MCP) e Skills
- **Decisão:** Adotar a estrutura MCP para comunicação de ferramentas (via cliente `Stitch`).
- **Justificativa:** Padroniza a maneira como a IA interage com ferramentas externas, simplificando a adição de novas *skills* como acesso ao banco de dados, execução de scripts remotos, ou interação com navegadores (`browser-harness`).

## 3. Consequências
- **Positivas:** Alta resiliência a falhas de IA. Código extensível para novas personas. Experiência de usuário fluida que não expõe exceções de LLM ao usuário graças ao *scrubbing* de logs.
- **Negativas / Riscos:** Complexidade maior na gerência de estado (os status persistidos em `.agent_status.json` precisam estar sempre sincronizados).

## 4. Status
**Ativo e em aprimoramento contínuo.**
