# RFC-001: Arquitetura Cliente-Servidor para LLM Remoto

**Status**: Aceito
**Data**: 2026-01-17
**Autor**: Equipe de Desenvolvimento LLM P2P

## 1. Contexto
A necessidade de executar modelos de linguagem grande (LLMs) excede a capacidade de hardware de estações de trabalho comuns. Atualmente, o projeto requer acesso a modelos como Qwen 2.5 (7b ou 14b), que demandam VRAM e RAM significativas.

## 2. Proposta
Adotar uma arquitetura **Cliente-Servidor Restrita** onde:
1.  **Servidor**: Uma instância Ollama rodando em um VPS dedicado (IP: 144.91.x.x), expondo a API na porta 11434.
2.  **Cliente**: Script Python leve rodando localmente, responsável apenas pela gestão do input/output e manutenção do estado da conversa.

## 3. Decisões de Design

### 3.1. Padrão de API
Optamos por usar o endpoint `/v1/chat/completions` em vez da API nativa do Ollama (`/api/chat`).
*   **Motivo**: Aderência ao padrão **Open Responses**. Isso nos permite trocar o backend no futuro (ex: vLLM, OpenAI, LocalAI) sem alterar o código do cliente.

### 3.2. Persistência
A persistência é **Local (Client-Side)**.
*   O servidor é stateless.
*   O cliente salva os JSONs de histórico.
*   **Motivo**: Privacidade e simplicidade. O servidor não precisa gerenciar sessões de usuários múltiplos.

## 4. Alternativas Consideradas

### A. Rodar Localmente (Ollama Local)
*   **Pros**: Privacidade total, sem latência de rede.
*   **Contras**: Hardware insuficiente para modelos >3B parâmetros. Descartado.

### B. Interface Web (Open WebUI)
*   **Pros**: UX visual.
*   **Contras**: Complexidade de setup e dependências pesadas Docker.
*   **Decisão**: Manter CLI python para agilidade e integração com scripts de automação.

## 5. Riscos
*   **Latência de Rede**: Depende da conexão entre cliente e VPS.
*   **Segurança**: A porta do Ollama foi aberta para `0.0.0.0`. Recomenda-se implementar firewall ou usar via túnel SSH para produção.
