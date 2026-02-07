---
name: browser
description: Controla navegador para automação web, scraping e screenshots.
homepage: https://playwright.dev
metadata:
  cleudocode:
    emoji: "🌐"
    category: "builtin"
    requires:
      packages: ["playwright"]
    install:
      - id: pip
        kind: pip
        package: playwright
        label: "Instalar Playwright (pip install playwright)"
      - id: browsers
        kind: shell
        command: "playwright install chromium"
        label: "Instalar navegadores"
---

# Browser Skill

Controle de navegador para automação web, scraping e capturas de tela usando Playwright.

## Setup

```bash
# Instalar Playwright
pip install playwright

# Instalar navegadores
playwright install chromium
```

## Funcionalidades

- **navigate**: Navegar para uma URL
- **screenshot**: Capturar screenshot da página
- **extract**: Extrair texto ou HTML da página
- **click**: Clicar em um elemento
- **type**: Digitar texto em um campo
- **eval**: Executar JavaScript na página

## Uso

### Navegar e Capturar Screenshot

```python
browser action:navigate url:"https://example.com"
browser action:screenshot output:"screenshot.png"
```

### Extrair Conteúdo

```python
browser action:extract selector:"h1"
browser action:extract selector:"body" format:text
```

### Automação

```python
browser action:click selector:"#login-button"
browser action:type selector:"#username" text:"meu_usuario"
```

### JavaScript

```python
browser action:eval script:"document.title"
```

## Exemplos de Uso no Cleudocode

```python
# Navegar e extrair título
browser action:navigate url:"https://news.ycombinator.com"
browser action:extract selector:"title"

# Screenshot de página
browser action:navigate url:"https://github.com"
browser action:screenshot output:"/tmp/github.png" fullpage:true

# Preencher formulário
browser action:navigate url:"https://example.com/login"
browser action:type selector:"#email" text:"user@example.com"
browser action:type selector:"#password" text:"senha123"
browser action:click selector:"button[type=submit]"
```

## Notas

- Usa Playwright (Chromium) em modo headless por padrão
- Para debugging, use `headless:false`
- Screenshots são salvos em PNG por padrão
- Suporta seletores CSS e XPath
- Rate limit recomendado: 1 req/seg para evitar bloqueios
