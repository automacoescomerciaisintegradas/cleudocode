# CleudoCode 🤖🚀

CleudoCode é uma plataforma local avançada com LLMs, Agentes Autônomos e Memória RAG, alimentada por **Ollama**.

## ✨ Funcionalidades

### 1. 💬 Chat Poderoso
*   **Modelo Local:** Roda 100% offline com Ollama (padrão: `qwen2.5-coder`).
*   **Multimodal:** Envie **Imagens** (requer modelo type-vision) e **PDFs/Códigos** diretamente no chat.
*   **Streaming:** Respostas em tempo real.
*   **Playground:** Laboratório para testar prompts e parâmetros (Temp, Top-P).

### 2. 🤖 Agentes Especializados
Selecione personas na barra lateral para mudar o comportamento da IA:
*   **Analista (Mary):** Brainstorming e Requisitos.
*   **PM (John):** Documentação e Visão de Produto.
*   **Arquiteto (Winston):** Estrutura técnica e decisões.
*   **Dev (Carl):** Implementação e Código.
*   **Researcher (Sherlock):** Busca na Web e verificação de fatos.
*   **Browser IA:** Automação de navegação e extração de dados.

### 3. 🧠 Memória & RAG (Retrieval-Augmented Generation)
*   **Upload de Conhecimento:** Adicione PDFs, TXTs e Markdown.
*   **Web Scraping:** Cole uma URL e o agente aprende o conteúdo do site.
*   **Indexação Vetorial:** Usa `ChromaDB` para busca semântica ultrarrápida.
*   **Sincronização:** Exporte tudo para o **Google NotebookLM** com um clique.

### 4. 🛠️ Autonomia (Agent Loop)
*   Script `agent_loop.py` permite que a IA execute ações reais:
    *   Rodar comandos no Shell.
    *   Ler e Escrever arquivos.
    *   Navegar na Internet (`fetch_url`).

## 🚀 Como Rodar

### Pré-requisitos
*   Python 3.10+
*   [Ollama](https://ollama.com) instalado e rodando.

### Instalação
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python agent-browser/scripts/setup_production.py
```

### Iniciando (Fácil)
Basta clicar duas vezes no arquivo **`start.bat`**.

### Iniciando (Manual)
```bash
streamlit run web_app.py
```

## 📂 Estrutura
*   `web_app.py`: Interface Principal (Streamlit).
*   `rag_engine.py`: Motor de Vetores e Memória.
*   `agent_loop.py`: Loop de execução autônoma.
*   `agent-browser/`: Automação de navegador.
*   `agents/`: Prompts das personas.
*   `docs/`: Documentação técnica e PRDs.

---

## 📞 Contato e Suporte 
📱 WhatsApp [+55 88 92156-7214](https://wa.me/558894227586)

## Desenvolvido por
**Automações Comerciais Integradas! ⚙️** - contato@automacoescomerciais.com.br

© 2025 Automações Comerciais Integradas. Todos os direitos reservados.
