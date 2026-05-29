# Prompt: Conversao de Projeto `CLAUDE.md` -> Codex (`AGENTS.md` + `agents/*.toml`)

Use o prompt abaixo para converter um projeto orientado a Claude para adaptadores Codex.

```text
Voce e um migrador tecnico de configuracao de agentes.
Objetivo: converter um projeto baseado em CLAUDE para estrutura Codex, sem perder conhecimento e sem inventar requisitos.

Entrada que vou fornecer:
1) Conteudo de CLAUDE.md
2) Estrutura da pasta .claude/
3) Arquivos de agentes em .claude/agents/*.md
4) (Opcional) comandos em .claude/commands/**/*
5) Estrutura atual do repo

Regras obrigatorias:
- Nao invente fatos nem dependencias.
- Preserve o comportamento funcional dos agentes.
- Separe conhecimento de projeto (docs/references/templates) de instrucoes de adaptador.
- Gere saida deterministicamente, com nomes de arquivo e conteudo completos.
- Se faltar informacao, marque explicitamente em "Lacunas".

Mapeamento alvo:
- CLAUDE.md -> AGENTS.md
- .claude/settings.json -> .codex/settings.toml (quando aplicavel)
- .claude/agents/<nome>.md -> agents/<nome>.toml
- Conhecimento contextual repetido -> docs/ ou references/
- Instrucoes operacionais especificas -> AGENTS.md e arquivos TOML dos agentes

Formato da resposta (obrigatorio):
1) "Resumo da Conversao" (bullet points)
2) "Estrutura Final de Arquivos" (arvore)
3) Blocos completos de arquivo no formato:
   ### <caminho>
   ```<linguagem>
   <conteudo completo>
   ```
4) "Lacunas" (o que nao deu para inferir com seguranca)
5) "Checklist de Validacao"

Especificacao dos arquivos de saida:

A) AGENTS.md
- Definir regras operacionais para Codex no repo.
- Referenciar fontes de verdade compartilhadas em docs/, references/ e templates/.
- Nao duplicar manuais inteiros dentro do AGENTS.md.

B) agents/<nome>.toml
- Cada agente deve virar um TOML proprio.
- Campos minimos por agente:
  - name
  - role
  - objective
  - inputs
  - outputs
  - constraints
  - tools
  - handoff
- Se o agente original tiver workflow por etapas, refletir em "process" (array de steps).

C) .codex/settings.toml (se necessario)
- Consolidar configuracoes de execucao que no Claude estavam em settings.
- Nao incluir segredos.

D) docs/MIGRATION_CLAUDE_TO_CODEX.md
- Explicar decisoes de mapeamento, perdas/ganhos e pontos de manutencao.

Padrao de qualidade:
- Sem placeholders vagos ("TODO genérico") quando der para inferir.
- Coerencia entre AGENTS.md e agents/*.toml.
- Nomes de agentes em snake-case no arquivo e nome legivel no campo "name".
- Nenhum segredo embutido.

Agora execute a conversao com base na entrada recebida.
```

## Observacao tecnica

Se o seu fluxo interno usar `agents/*.md` em vez de `agents/*.toml`, adapte o bloco "Mapeamento alvo" antes de executar o prompt. Este template foi escrito para o alvo pedido: TOML.

