# Product Requirements Document (PRD) - Cleudocode Agent Harness

## 1. Visão Geral do Produto
O **Cleudocode** é um Agent Harness para tarefas de engenharia de software e automação de negócios. Ele atua como um maestro (orquestrador) executando localmente na máquina do usuário, delegando tarefas para um esquadrão de perfis (personas) da IA, sem amarrar a execução a um provedor específico de LLM.

## 2. Público-Alvo
- Desenvolvedores de Software
- Engenheiros DevOps e SysAdmins
- Empreendedores técnicos focados em automações
- Entusiastas de IA Open Source

## 3. Casos de Uso
1. **Assistência de Codificação Local**: Solicitar ao agente a criação, refatoração ou debug de scripts, rodando diretamente no ambiente do usuário.
2. **Brainstorming Técnico**: Provocar uma discussão (`/debate`) técnica entre agentes especializados (ex: Arquiteto vs. Especialista em Segurança) para desenhar a melhor solução.
3. **Automação de Ferramentas Web**: Integrar com a *skill* de navegação (`browser-harness`) para navegar em páginas web e raspar informações ou testar sites em tempo real.
4. **Resiliência na Execução**: Continuar trabalhando em missões extensas mesmo se a chave de um provedor LLM específico estourar o limite de *rate limit*, rotacionando provedores perfeitamente em plano de fundo (OmniRoute).

## 4. Requisitos Principais

### 4.1. Funcionais
- **Terminal Interativo (CLI)**: Uma shell rica baseada em `click` e `rich` para conversar com agentes. Comandos administrativos (como `agents`, `tools`, `skills`, `model`) devem ser executados de forma nativa e ergonômica.
- **Roteamento Inteligente (OmniRoute)**: Suporte obrigatório a múltiplos LLMs (Ollama para local, Anthropic, OpenAI, Google Gemini, OpenRouter, etc.). O roteador deve fazer fallback transparente (failover automático em erros de autenticação, timeout e excesso de requisições).
- **Mission Control**: O núcleo (`orchestrator.py`) deve gerenciar o estado (`idle`, `busy`) de múltiplos agentes. Um agente líder (como Jarvis) pode convocar outros e delegar tarefas usando diretivas (`delegate-task`).
- **Dashboard de Gestão**: Uma UI local (`web_app.py`) via Streamlit, subida como serviço secundário, para monitorar o status do ecossistema, os tokens gastos, as keys atuais, o status de RAG, entre outros dados telemétricos.
- **Memória de Longo Prazo (RAG)**: O sistema armazena interações na memória semântica e puxa contextos passados de maneira imperceptível em novas interações.

### 4.2. Não-Funcionais
- **Privacidade e Segurança**: As chaves de API não podem de forma alguma ser vazadas em logs de terminal durante os processos de exceção (implementado scrub de chaves no logger do `core.llm_providers`).
- **Execução Desacoplada**: A ferramenta não é dona dos servidores LLM. Ela funciona em arquitetura híbrida (execução do ambiente local e cérebro na nuvem ou local via Ollama).
- **Idempotência de Setup**: O instalador (`install_vps.sh`) deve garantir a implantação confiável do ecossistema independentemente de pré-existência parcial de pacotes.

## 5. Escopo Futuro (Roadmap)
- Pleno suporte à automação massiva em containers distribuídos.
- Acoplamento fino com o protocolo MCP para expandir ferramentas de forma "plug and play".
