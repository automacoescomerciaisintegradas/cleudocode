---
description: Skill e workflow de atendimento inteligente para o ecossistema **cleudobot / OpenClaw**, com identificação de intenção, uso de memória, resposta contextual e extensibilidade para automações comerciais.
---

# 🤖 Cleudobot – Skill de Atendimento Inteligente

Skill e workflow de atendimento inteligente para o ecossistema **cleudobot / OpenClaw**, com identificação de intenção, uso de memória, resposta contextual e extensibilidade para automações comerciais.

---

## 📌 Visão Geral

Esta skill permite que o cleudobot:

- Receba mensagens de usuários via canais (WhatsApp, Telegram, Web)
- Identifique a intenção da mensagem
- Consulte memória de conversas
- Gere respostas inteligentes via LLM
- Salve contexto para futuras interações
- Seja facilmente expandida com webhooks, cron, plugins ou ações humanas

---

## 🎯 Objetivo da Skill

Nome da Skill: **atendimento-inteligente**

Casos de uso:
- Atendimento ao cliente
- Pré-vendas
- Suporte técnico
- Conversas contextuais
- Automação comercial integrada

---

## 🧠 Workflow Lógico

```text
[Mensagem do Usuário]
        ↓
[Normalização de texto]
        ↓
[Detecção de intenção]
        ↓
┌──────────────────────────────┐
│ Intenção conhecida?          │
└──────────────┬───────────────┘
               │
      ┌────────┴─────────┐
      │                  │
    SIM                NÃO
      │                  │
[Consulta memória]   [Solicitar mais dados]
      │
[Gerar resposta]
      │
[Salvar contexto]
      │
[Responder usuário]
