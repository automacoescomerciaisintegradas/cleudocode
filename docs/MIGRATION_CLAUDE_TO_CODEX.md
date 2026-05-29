# Migracao Claude -> Codex (Adapter Setup)

Data: 2026-05-29

## Arquivos criados
- .codex/config.toml
- .codex/agents/*.toml (convertidos de .claude/agents/*.md)

## Arquivos atualizados
- AGENTS.md (secoes de mapa de adaptador Codex)

## Decisoes
- AGENTS.md permanece como instrucoes de alto nivel do repo para Codex.
- Conhecimento de projeto permanece em docs/.
- Conversao de agentes preserva o corpo das instrucoes em developer_instructions.

## Observacoes
- Nao foi encontrado .claude/skills/; portanto nao houve copia para .agents/skills/.
- Hooks de .claude/settings.json foram mapeados para .codex/config.toml apenas como referencia de comando.
