# 🏆 MASTER - Sentient Cleudocode Ecosystem
## 🌌 Visão Geral
Este arquivo centraliza a "Fonte da Verdade" (Source of Truth) para o desenvolvimento do ecossistema Cleudocode integrado ao Antigravity e Sentient Grid. Governa a estética, arquitetura e processos agentic.

## 🎨 1. Design System Pro Max (UI/UX)
### 💎 Princípios Estéticos
- **Premium Glow**: Uso de glassmorphism com blur de 12px a 20px.
- **Vibrant Dark Mode**: Fundo `#0a0a0c`, acentos em `#FF5A36` (Cleudo Orange) e `#00F2FF` (Antigravity Cyan).
- **Micro-interações**: Transições suaves de 300ms em todos os hover states.
- **Tipografia**: Outfit para títulos, Inter para corpo de texto.

### 🍱 Hierarquia de Arquivos Web
- `web/src/styles/tokens.css`: Variáveis CSS globais.
- `web/src/components/`: Componentes atômicos e reutilizáveis.
- `web/index.html`: Layout mestre com injeção dinâmica.

## 🤖 2. Arquitetura Agentic (Lobster Engine)
### 🔄 Fluxo de Trabalho
1. **Identificação**: O sistema detecta a intenção via LLM Hub.
2. **Orquestração**: O `workflow_manager.py` seleciona o `.lobster` correspondente.
3. **Execução**: Steps sequenciais com rollback automático em caso de erro crítico.
4. **Relatório**: Logs salvos em `reports/` com sumário executivo.

### 🛡️ Segurança e Autenticação
- **Google Antigravity Auth**: Obrigatório para acesso ao gateway de inferência externa.
- **OML Compliance**: Verificação de lealdade via `check_fingerprints.py`.
- **Sandbox**: Execução de scripts shell em ambiente controlado (quando aplicável).

## 📡 3. Gateway e Rede
- **Porta Padrão (Gateway)**: `18900` (Mapeada de 8501).
- **Interface Sentient**: Bridge ativa para monetização via Sentient Grid.
- **Relay Port**: `18902` para comunicação com extensão do navegador.

## 📜 4. Regras de Código (Python/JS)
- **Documentação**: Docstrings em todas as funções principais.
- **Tipagem**: Use `typing` em Python e `TypeScript` no Frontend.
- **Resiliência**: Trate erros de conexão com retentativas (Max 3).

---
*Criado por: Orquestrador Pro Max*
*Última atualização: 2026-02-06*
