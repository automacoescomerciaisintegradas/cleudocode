# Documento de Requisitos do Produto (PRD) - Agente Autônomo de Desenvolvimento
**Status:** Rascunho Inicial
**Data:** 17/01/2026
**Autor:** John (AI Product Manager)

## 1. Visão do Produto
Criar um assistente de desenvolvimento local, privado e autônomo, capaz de interagir com o sistema de arquivos do usuário para escrever, testar e evoluir software complexo através de uma interface de chat intuitiva.

## 2. Personas Alvo
- **Desenvolvedor Sênior:** Quer automatizar tarefas repetitivas (boilerplate, testes, docs).
- **Desenvolvedor Iniciante:** Quer um "Pair Programmer" que explique e corrija erros.

## 3. Objetivos Estratégicos
- **Autonomia:** O agente deve ser capaz de realizar ciclos completos de desenvolvimento (Escrever -> Testar -> Corrigir) sem intervenção humana constante.
- **Privacidade:** Todo o código e contexto devem permanecer locais ou no servidor privado do usuário (Ollama).
- **Usabilidade:** Interface Web limpa e responsiva (Streamlit) com feedbacks claros em PT-BR.

## 4. Requisitos Funcionais (Features)

### F1. Execução de Código (Code Execution)
- **O quê:** O agente deve poder executar scripts Python gerados.
- **Por quê:** Para validar se o código funciona antes de entregá-lo ao usuário.
- **Requisito:** Implementar um mecanismo de `exec()` ou `subprocess` seguro.

### F2. Manipulação de Arquivos (File System Tools)
- **O quê:** Capacidade de Criar, Ler, Editar e Deletar arquivos no projeto.
- **Por quê:** Para que o agente possa efetivamente "codar" o projeto.
- **Requisito:** Ferramentas de `read_file`, `write_file`, `list_dir`.

### F3. Agentes Especializados (Multi-Agent System)
- **O quê:** O usuário pode trocar de "chapéu" (PM, Dev, QA, Arquiteto).
- **Por quê:** Diferentes fases do projeto exigem diferentes mindsets.
- **Implementação:** Já iniciada com o seletor na Sidebar.

### F4. Injeção de Contexto (RAG Simplificado)
- **O quê:** O agente deve saber sobre os arquivos existentes do projeto.
- **Por quê:** Para evitar alucinações e reescrita de código existente.
- **Requisito:** Ler automaticamente a estrutura de pastas e arquivos abertos.

## 5. Requisitos Não-Funcionais
- **Performance:** Respostas de streaming em < 2s.
- **Compatibilidade:** Funcionar em Windows, Linux e Mac.
- **Segurança:** O agente não pode deletar arquivos fora do diretório do projeto (Jail).

## 6. Métricas de Sucesso (KPIs)
- **Taxa de Compilação:** % de códigos gerados que rodam sem erro na primeira tentativa.
- **Retenção:** Frequência de uso do chat vs. IDE padrão.

## 7. Próximos Passos (Roadmap)
1.  Implementar ferramenta de execução de código no `agent_loop.py`.
2.  Melhorar o carregamento de contexto na Web UI.
3.  Criar testes automatizados para as novas ferramentas.
