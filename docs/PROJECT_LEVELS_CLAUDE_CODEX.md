# Niveis de Projeto: Claude + Codex

Este documento define niveis para manter um unico projeto com dois adaptadores de agente (Claude e Codex), sem duplicar conhecimento de dominio.

## Nivel 0: Global (maquina do usuario)

Escopo:
- Configuracoes que valem para todos os repositorios.

Claude:
- `~/.claude/`

Codex:
- `~/.codex/` para configuracao global
- `~/.agents/skills/` para skills globais

Regras:
- Nao colocar conhecimento especifico de um repo aqui.
- Usar apenas defaults, auth local e preferencias gerais.

## Nivel 1: Projeto Compartilhado (dentro do repo)

Escopo:
- Fonte unica da verdade do produto.

Pastas recomendadas:
- `docs/`
- `references/`
- `templates/`
- `scripts/`
- `projects/`
- `README.md`

Regras:
- Regras de negocio, arquitetura e contexto devem ficar aqui.
- Evitar repetir o mesmo conhecimento em arquivos de adaptador.

## Nivel 2: Adaptador Claude (projeto)

Escopo:
- Arquivos que o Claude Code procura neste repo.

Arquivos:
- `CLAUDE.md`
- `.claude/`
- `.claude/agents/*.md`
- `.claude/commands/**/*.md`

Regras:
- Somente instrucoes operacionais para Claude.
- Referenciar `docs/` como fonte de conhecimento.

## Nivel 3: Adaptador Codex (projeto)

Escopo:
- Arquivos que o Codex procura neste repo.

Arquivos:
- `AGENTS.md`
- `.codex/`
- `agents/*.toml` (definicoes de agente para Codex)
- `.agents/skills/*/SKILL.md` (skills do projeto)

Regras:
- Somente instrucoes operacionais para Codex.
- Reutilizar o mesmo conhecimento central de `docs/`, `references/` e `templates/`.

## Mapeamento direto Claude -> Codex

- `CLAUDE.md` -> `AGENTS.md`
- `.claude/settings.json` -> `.codex/settings.toml` (ou equivalente suportado)
- `.claude/agents/<nome>.md` -> `agents/<nome>.toml`
- `.claude/commands/**/*.md` -> `scripts/` + documentacao em `docs/` (quando fizer sentido)
- Conhecimento de produto dentro de prompts Claude -> `docs/`, `references/`, `templates/`

## Checklist de consistencia

- Existe apenas uma fonte de verdade para arquitetura em `docs/`.
- `AGENTS.md` e `CLAUDE.md` nao entram em conflito.
- Todo agente em `agents/*.toml` aponta para contexto compartilhado (evitar contexto duplicado).
- Skills locais em `.agents/skills/` estao desacopladas de segredos.

