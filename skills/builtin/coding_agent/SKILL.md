---
name: coding-agent
description: Executa agentes de código (Codex CLI, Claude Code, Pi) via processo em background para controle programático.
metadata:
  cleudocode:
    emoji: "🧩"
    category: "builtin"
    requires:
      anyBins: ["claude", "codex", "opencode", "pi"]
    install:
      - id: npm-codex
        kind: npm
        package: "@openai/codex"
        global: true
        bins: ["codex"]
        label: "Instalar Codex CLI (npm)"
      - id: npm-pi
        kind: npm
        package: "@mariozechner/pi-coding-agent"
        global: true
        bins: ["pi"]
        label: "Instalar Pi Coding Agent (npm)"
---

# Coding Agent (bash-first)

Use **bash** (com modo background opcional) para todo trabalho com agentes de código. Simples e efetivo.

## ⚠️ Modo PTY Necessário!

Agentes de código (Codex, Claude Code, Pi) são **aplicações de terminal interativas** que precisam de um pseudo-terminal (PTY) para funcionar corretamente. Sem PTY, você terá output quebrado, cores faltando, ou o agente pode travar.

**Sempre use `pty:true`** ao executar agentes de código:

```bash
# ✅ Correto - com PTY
bash pty:true command:"codex exec 'Seu prompt'"

# ❌ Errado - sem PTY, agente pode quebrar
bash command:"codex exec 'Seu prompt'"
```

## Parâmetros da Tool Bash

| Parâmetro     | Tipo    | Descrição                                                                    |
|---------------|---------|------------------------------------------------------------------------------|
| `command`     | string  | O comando shell a executar                                                   |
| `pty`         | boolean | **Use para coding agents!** Aloca um pseudo-terminal para CLIs interativas  |
| `workdir`     | string  | Diretório de trabalho (agente vê apenas o contexto desta pasta)             |
| `background`  | boolean | Executa em background, retorna sessionId para monitoramento                 |
| `timeout`     | number  | Timeout em segundos (mata processo ao expirar)                              |
| `elevated`    | boolean | Executa no host ao invés do sandbox (se permitido)                          |

## Ações da Tool Process (para sessões background)

| Ação        | Descrição                                             |
|-------------|-------------------------------------------------------|
| `list`      | Lista todas as sessões ativas/recentes                |
| `poll`      | Verifica se a sessão ainda está rodando               |
| `log`       | Obtém output da sessão (com offset/limit opcional)    |
| `write`     | Envia dados raw para stdin                            |
| `submit`    | Envia dados + newline (como digitar e pressionar Enter)|
| `send-keys` | Envia tokens de tecla ou bytes hex                    |
| `paste`     | Cola texto (com modo bracketed opcional)              |
| `kill`      | Termina a sessão                                      |

---

## Quick Start: Tarefas One-Shot

Para prompts/chats rápidos, crie um repo git temporário e execute:

```bash
# Chat rápido (Codex precisa de um repo git!)
SCRATCH=$(mktemp -d) && cd $SCRATCH && git init && codex exec "Seu prompt aqui"

# Ou em um projeto real - com PTY!
bash pty:true workdir:~/Projects/meuproj command:"codex exec 'Adicionar tratamento de erros nas chamadas de API'"
```

**Por que git init?** Codex se recusa a rodar fora de um diretório git confiável. Criar um repo temporário resolve isso para trabalhos rápidos.

---

## O Padrão: workdir + background + pty

Para tarefas mais longas, use modo background com PTY:

```bash
# Iniciar agente no diretório alvo (com PTY!)
bash pty:true workdir:~/project background:true command:"codex exec --full-auto 'Construir um jogo snake'"
# Retorna sessionId para rastreamento

# Monitorar progresso
process action:log sessionId:XXX

# Verificar se terminou
process action:poll sessionId:XXX

# Enviar input (se agente fizer pergunta)
process action:write sessionId:XXX data:"y"

# Submeter com Enter
process action:submit sessionId:XXX data:"yes"

# Matar se necessário
process action:kill sessionId:XXX
```

**Por que workdir importa:** Agente acorda em um diretório focado, não fica vagando lendo arquivos não relacionados.

---

## Codex CLI

**Modelo:** `gpt-5.2-codex` é o padrão (configurado em ~/.codex/config.toml)

### Flags

| Flag            | Efeito                                              |
|-----------------|-----------------------------------------------------|
| `exec "prompt"` | Execução one-shot, sai quando termina               |
| `--full-auto`   | Sandboxed mas auto-aprova no workspace              |
| `--yolo`        | SEM sandbox, SEM aprovações (mais rápido, perigoso) |

### Build/Criação

```bash
# One-shot rápido (auto-aprova) - lembre do PTY!
bash pty:true workdir:~/project command:"codex exec --full-auto 'Criar toggle de dark mode'"

# Background para trabalho longo
bash pty:true workdir:~/project background:true command:"codex --yolo 'Refatorar módulo de auth'"
```

---

## Claude Code

```bash
# Com PTY para output de terminal adequado
bash pty:true workdir:~/project command:"claude 'Sua tarefa'"

# Background
bash pty:true workdir:~/project background:true command:"claude 'Sua tarefa'"
```

---

## Pi Coding Agent

```bash
# Install: npm install -g @mariozechner/pi-coding-agent
bash pty:true workdir:~/project command:"pi 'Sua tarefa'"

# Modo não-interativo (PTY ainda recomendado)
bash pty:true command:"pi -p 'Resumir src/'"

# Provider/modelo diferente
bash pty:true command:"pi --provider openai --model gpt-4o-mini -p 'Sua tarefa'"
```

---

## ⚠️ Regras

1. **Sempre use pty:true** - agentes de código precisam de terminal!
2. **Respeite a escolha de tool** - se usuário pedir Codex, use Codex.
3. **Seja paciente** - não mate sessões porque estão "lentas"
4. **Monitore com process:log** - verifique progresso sem interferir
5. **--full-auto para building** - auto-aprova mudanças
6. **vanilla para review** - sem flags especiais necessárias
7. **Paralelo é OK** - execute vários processos Codex de uma vez

---

## Atualizações de Progresso (Crítico)

Quando você spawn agentes de código em background, mantenha o usuário informado.

- Envie 1 mensagem curta quando iniciar (o que está rodando + onde).
- Depois só atualize quando algo mudar:
  - um milestone completa (build terminou, testes passaram)
  - o agente faz pergunta / precisa de input
  - você encontrou erro ou precisa de ação do usuário
  - o agente termina (inclua o que mudou + onde)
- Se você matar uma sessão, diga imediatamente que matou e por quê.

---

## Exemplos de Uso no Cleudocode

```python
# Executar Codex one-shot
coding_agent action:exec agent:codex prompt:"Criar função de validação de email"

# Background com monitoramento
coding_agent action:start agent:pi workdir:~/project prompt:"Refatorar API"
# Retorna: sessionId: abc123

coding_agent action:log sessionId:abc123
coding_agent action:poll sessionId:abc123
```
