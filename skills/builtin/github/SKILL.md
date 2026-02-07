---
name: github
description: "Interage com o GitHub usando a CLI `gh`. Use para issues, PRs, CI runs e queries avançadas."
metadata:
  cleudocode:
    emoji: "🐙"
    category: "productivity"
    requires:
      bins: ["gh"]
    install:
      - id: winget
        kind: winget
        package: "GitHub.cli"
        bins: ["gh"]
        label: "Instalar GitHub CLI (winget)"
      - id: scoop
        kind: scoop
        package: "gh"
        bins: ["gh"]
        label: "Instalar GitHub CLI (scoop)"
      - id: choco
        kind: choco
        package: "gh"
        bins: ["gh"]
        label: "Instalar GitHub CLI (chocolatey)"
---

# GitHub Skill

Use a CLI `gh` para interagir com o GitHub. Sempre especifique `--repo owner/repo` quando não estiver em um diretório git, ou use URLs diretamente.

## Setup

```bash
# Autenticação
gh auth login

# Verificar status
gh auth status
```

## Pull Requests

### Verificar status de CI em um PR

```bash
gh pr checks 55 --repo owner/repo
```

### Listar workflow runs recentes

```bash
gh run list --repo owner/repo --limit 10
```

### Ver detalhes de um run

```bash
gh run view <run-id> --repo owner/repo
```

### Ver logs de steps que falharam

```bash
gh run view <run-id> --repo owner/repo --log-failed
```

## Issues

### Listar issues abertas

```bash
gh issue list --repo owner/repo --state open
```

### Criar uma issue

```bash
gh issue create --repo owner/repo --title "Bug: ..." --body "Descrição do bug"
```

### Fechar uma issue

```bash
gh issue close <issue-number> --repo owner/repo
```

## API para Queries Avançadas

O comando `gh api` é útil para acessar dados não disponíveis via outros subcomandos.

### Obter PR com campos específicos

```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

### Listar releases

```bash
gh api repos/owner/repo/releases --jq '.[].tag_name'
```

## JSON Output

A maioria dos comandos suporta `--json` para output estruturado. Use `--jq` para filtrar:

```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

## Exemplos de Uso no Cleudocode

```python
# Listar PRs abertos
github action:pr_list repo:"owner/repo" state:open

# Criar issue
github action:issue_create repo:"owner/repo" title:"Bug encontrado" body:"Descrição"

# Verificar CI
github action:pr_checks repo:"owner/repo" pr:55
```

## Notas

- Requer autenticação via `gh auth login`
- Para repositórios privados, precisa de permissões adequadas
- Rate limit: 5000 requests/hora para usuários autenticados
