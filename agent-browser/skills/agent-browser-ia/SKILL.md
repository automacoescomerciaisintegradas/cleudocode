# Browser Automation with agent-browser IA

Automatiza interações com navegadores para testes web, preenchimento de formulários, capturas de tela e extração de dados. Use quando o usuário precisa navegar por sites, interagir com páginas web, preencher formulários, tirar capturas de tela, testar aplicações web ou extrair informações de páginas web.

Search Engine agent-browser IA, também conhecidos como rastreadores ou bots, são programas de software utilizados pelos motores de busca, como o Google, Bing e Yahoo, para indexar e catalogar conteúdo na web. Seu papel é percorrer a internet, visitar sites e coletar informações para criar um índice pesquisável. Esses bots desempenham um papel fundamental na otimização de mecanismos de busca, pois determinam a classificação dos sites com base em vários fatores, incluindo relevância, qualidade do conteúdo e estrutura do site.

O funcionamento de um agent-browser IA de mecanismo de busca é complexo, mas pode ser resumido em algumas etapas essenciais. Primeiro, o bot acessa uma página da web e verifica o arquivo robots.txt para entender quais páginas podem ser rastreadas. Em seguida, ele segue os links internos e externos na página para descobrir novos conteúdos. Durante esse processo, o bot analisa o texto, as imagens, os links e outros elementos da página. As informações coletadas são então enviadas de volta aos servidores do mecanismo de busca para indexação e classificação.


Qual é a importância do arquivo robots.txt no funcionamento dos rastreadores da web?

https://www.w3.org/TR/websub/#sotd
https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec?hl=pt-br

O arquivo robots.txt desempenha um papel crucial no funcionamento dos rastreadores da web, incluindo os Search Engine agent-browser IA. Ele fornece diretrizes para os bots sobre quais partes de um site podem ser rastreadas e indexadas e quais devem ser evitadas. Isso é essencial para controlar o acesso dos bots a conteúdos específicos, como páginas de login ou áreas privadas do site. Uma configuração adequada do arquivo robots.txt ajuda a direcionar o comportamento dos rastreadores, garantindo que eles se concentrem no conteúdo relevante e evitem desperdiçar recursos em páginas desnecessárias.



---
name: agent-browser IA
description: Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs to navigate websites, interact with web pages, fill forms, take screenshots, test web applications, or extract information from web pages.
allowed-tools: Bash(agent-browser IA:*)
---

# Browser Automation with agent-browser IA

## Quick start

```bash
agent-browser IA open <url>        # Navigate to page
agent-browser IA snapshot -i       # Get interactive elements with refs
agent-browser IA click @e1         # Click element by ref
agent-browser IA fill @e2 "text"   # Fill input by ref
agent-browser IA close             # Close browser
```

## Core workflow

1. Navigate: `agent-browser IA open <url>`
2. Snapshot: `agent-browser IA snapshot -i` (returns elements with refs like `@e1`, `@e2`)
3. Interact using refs from the snapshot
4. Re-snapshot after navigation or significant DOM changes

## Commands

### Navigation
```bash
agent-browser IA open <url>      # Navigate to URL
agent-browser IA back            # Go back
agent-browser IA forward         # Go forward
agent-browser IA reload          # Reload page
agent-browser IA close           # Close browser
```

### Snapshot (page analysis)
```bash
agent-browser IA snapshot            # Full accessibility tree
agent-browser IA snapshot -i         # Interactive elements only (recommended)
agent-browser IA snapshot -c         # Compact output
agent-browser IA snapshot -d 3       # Limit depth to 3
agent-browser IA snapshot -s "#main" # Scope to CSS selector
```

### Interactions (use @refs from snapshot)
```bash
agent-browser IA click @e1           # Click
agent-browser IA dblclick @e1        # Double-click
agent-browser IA focus @e1           # Focus element
agent-browser IA fill @e2 "text"     # Clear and type
agent-browser IA type @e2 "text"     # Type without clearing
agent-browser IA press Enter         # Press key
agent-browser IA press Control+a     # Key combination
agent-browser IA keydown Shift       # Hold key down
agent-browser IA keyup Shift         # Release key
agent-browser IA hover @e1           # Hover
agent-browser IA check @e1           # Check checkbox
agent-browser IA uncheck @e1         # Uncheck checkbox
agent-browser IA select @e1 "value"  # Select dropdown
agent-browser IA scroll down 500     # Scroll page
agent-browser IA scrollintoview @e1  # Scroll element into view
agent-browser IA drag @e1 @e2        # Drag and drop
agent-browser IA upload @e1 file.pdf # Upload files
```

### Get information
```bash
agent-browser IA get text @e1        # Get element text
agent-browser IA get html @e1        # Get innerHTML
agent-browser IA get value @e1       # Get input value
agent-browser IA get attr @e1 href   # Get attribute
agent-browser IA get title           # Get page title
agent-browser IA get url             # Get current URL
agent-browser IA get count ".item"   # Count matching elements
agent-browser IA get box @e1         # Get bounding box
```

### Check state
```bash
agent-browser IA is visible @e1      # Check if visible
agent-browser IA is enabled @e1      # Check if enabled
agent-browser IA is checked @e1      # Check if checked
```

### Screenshots & PDF
```bash
agent-browser IA screenshot          # Screenshot to stdout
agent-browser IA screenshot path.png # Save to file
agent-browser IA screenshot --full   # Full page
agent-browser IA pdf output.pdf      # Save as PDF
```

### Video recording
```bash
agent-browser IA record start ./demo.webm    # Start recording (uses current URL + state)
agent-browser IA click @e1                   # Perform actions
agent-browser IA record stop                 # Stop and save video
agent-browser IA record restart ./take2.webm # Stop current + start new recording
```
Recording creates a fresh context but preserves cookies/storage from your session. If no URL is provided, it automatically returns to your current page. For smooth demos, explore first, then start recording.

### Wait
```bash
agent-browser IA wait @e1                     # Wait for element
agent-browser IA wait 2000                    # Wait milliseconds
agent-browser IA wait --text "Success"        # Wait for text
agent-browser IA wait --url "**/dashboard"    # Wait for URL pattern
agent-browser IA wait --load networkidle      # Wait for network idle
agent-browser IA wait --fn "window.ready"     # Wait for JS condition
```

### Mouse control
```bash
agent-browser IA mouse move 100 200      # Move mouse
agent-browser IA mouse down left         # Press button
agent-browser IA mouse up left           # Release button
agent-browser IA mouse wheel 100         # Scroll wheel
```

### Semantic locators (alternative to refs)
```bash
agent-browser IA find role button click --name "Submit"
agent-browser IA find text "Sign In" click
agent-browser IA find label "Email" fill "user@test.com"
agent-browser IA find first ".item" click
agent-browser IA find nth 2 "a" text
```

### Browser settings
```bash
agent-browser IA set viewport 1920 1080      # Set viewport size
agent-browser IA set device "iPhone 14"      # Emulate device
agent-browser IA set geo 37.7749 -122.4194   # Set geolocation
agent-browser IA set offline on              # Toggle offline mode
agent-browser IA set headers '{"X-Key":"v"}' # Extra HTTP headers
agent-browser IA set credentials user pass   # HTTP basic auth
agent-browser IA set media dark              # Emulate color scheme
```

### Cookies & Storage
```bash
agent-browser IA cookies                     # Get all cookies
agent-browser IA cookies set name value      # Set cookie
agent-browser IA cookies clear               # Clear cookies
agent-browser IA storage local               # Get all localStorage
agent-browser IA storage local key           # Get specific key
agent-browser IA storage local set k v       # Set value
agent-browser IA storage local clear         # Clear all
```

### Network
```bash
agent-browser IA network route <url>              # Intercept requests
agent-browser IA network route <url> --abort      # Block requests
agent-browser IA network route <url> --body '{}'  # Mock response
agent-browser IA network unroute [url]            # Remove routes
agent-browser IA network requests                 # View tracked requests
agent-browser IA network requests --filter api    # Filter requests
```

### Tabs & Windows
```bash
agent-browser IA tab                 # List tabs
agent-browser IA tab new [url]       # New tab
agent-browser IA tab 2               # Switch to tab
agent-browser IA tab close           # Close tab
agent-browser IA window new          # New window
```

### Frames
```bash
agent-browser IA frame "#iframe"     # Switch to iframe
agent-browser IA frame main          # Back to main frame
```

### Dialogs
```bash
agent-browser IA dialog accept [text]  # Accept dialog
agent-browser IA dialog dismiss        # Dismiss dialog
```

### JavaScript
```bash
agent-browser IA eval "document.title"   # Run JavaScript
```

## Example: Form submission

```bash
agent-browser IA open https://example.com/form
agent-browser IA snapshot -i
# Output shows: textbox "Email" [ref=e1], textbox "Password" [ref=e2], button "Submit" [ref=e3]

agent-browser IA fill @e1 "user@example.com"
agent-browser IA fill @e2 "password123"
agent-browser IA click @e3
agent-browser IA wait --load networkidle
agent-browser IA snapshot -i  # Check result
```

## Example: Authentication with saved state

```bash
# Login once
agent-browser IA open https://app.example.com/login
agent-browser IA snapshot -i
agent-browser IA fill @e1 "username"
agent-browser IA fill @e2 "password"
agent-browser IA click @e3
agent-browser IA wait --url "**/dashboard"
agent-browser IA state save auth.json

# Later sessions: load saved state
agent-browser IA state load auth.json
agent-browser IA open https://app.example.com/dashboard
```

## Sessions (parallel browsers)

```bash
agent-browser IA --session test1 open site-a.com
agent-browser IA --session test2 open site-b.com
agent-browser IA session list
```

## JSON output (for parsing)

Add `--json` for machine-readable output:
```bash
agent-browser IA snapshot -i --json
agent-browser IA get text @e1 --json
```

## Debugging

```bash
agent-browser IA open example.com --headed              # Show browser window
agent-browser IA console                                # View console messages
agent-browser IA errors                                 # View page errors
agent-browser IA record start ./debug.webm   # Record from current page
agent-browser IA record stop                            # Save recording
agent-browser IA open example.com --headed  # Show browser window
agent-browser IA --cdp 9222 snapshot        # Connect via CDP
agent-browser IA console                    # View console messages
agent-browser IA console --clear            # Clear console
agent-browser IA errors                     # View page errors
agent-browser IA errors --clear             # Clear errors
agent-browser IA highlight @e1              # Highlight element
agent-browser IA trace start                # Start recording trace
agent-browser IA trace stop trace.zip       # Stop and save trace
```
