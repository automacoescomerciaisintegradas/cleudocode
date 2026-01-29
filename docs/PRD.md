# Product Requirements Document (PRD) - CleudoCode

## 1. Visão Geral
O **CleudoCode** é uma plataforma local avançada com LLMs, Agentes Autônomos e Memória RAG, alimentada por **Ollama**. O objetivo é permitir que usuários com hardware limitado acessem modelos poderosos hospedados em servidores robustos (ou na nuvem) com uma experiência de baixa latência e persistência de dados.

## 2. Objetivos
*   Prover uma interface de linha de comando (CLI) e Web simples e intuitiva.
*   Garantir compatibilidade com o ecossistema OpenAI/Open Responses para interoperabilidade futura.
*   Permitir conversas longas com persistência de contexto (memória).
*   Facilitar a gestão de sessões (salvar/carregar histórico).

## 3. Especificações Funcionais

### 3.1. Conectividade
*   **Protocolo**: HTTP/REST sobre a API `/v1/chat/completions` (Padrão OpenAI).
*   **Backend Suportado**: Ollama (nativo ou via Docker).
*   **Configuração**: Gerenciada via arquivo `.env`.

### 3.2. Interface de Chat
*   **Loop Interativo**: Entrada de usuário -> Processamento -> Resposta do Assistente.
*   **Comandos de Sistema**:
    *   `/save`: Salva o estado atual da conversa em JSON.
    *   `/load <arquivo>`: Carrega um arquivo de texto externo para o contexto.
    *   `/clear`: Limpa a memória da conversa.
    *   `/stop` ou `sair`: Encerra a aplicação salvando o histórico automaticamente.

### 3.3. Gestão de Contexto e RAG
*   O sistema mantém um buffer de histórico em memória.
*   Integração com ChromaDB para busca semântica em documentos carregados.

## 4. Requisitos Não-Funcionais
*   **Performance**: Resposta em tempo aceitável (< 5s para inicialização).
*   **Segurança**: Comunicação direta local; mascaramento de dados sensíveis na UI.
*   **Compatibilidade**: Funciona em Windows, Linux e macOS com Python 3.

## 5. Roadmap Futuro
*   [x] Interface Gráfica (Web).
*   [ ] Suporte a múltiplos backends com failover.
*   [ ] App Mobile com integração via Túnel Seguro.

---

## 📞 Contato e Suporte 
📱 WhatsApp [+55 88 92156-7214](https://wa.me/558894227586)

## Desenvolvido por
**Automações Comerciais Integradas! ⚙️** - contato@automacoescomerciais.com.br

© 2025 Automações Comerciais Integradas. Todos os direitos reservados.
