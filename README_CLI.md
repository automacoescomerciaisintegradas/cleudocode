# Guia da CLI Cleudocode (OpenClaw Style)

Você agora possui uma CLI poderosa para gerenciar seu ecossistema.

## Como Usar

### Opção 1: Via Node.js (Recomendado)
Execute a partir da raiz do projeto:
```bash
node dist/cli/index.js <comando>
```

### Opção 2: Via Script Wrapper
```bash
bash cleudocode <comando>
```

## Comandos Disponíveis

### 1. Dashboard (Novo)
Abre a interface de controle com autenticação automática.
```bash
bash cleudocode dashboard
# Saída: Abre navegador em http://localhost:8501/?token=...
```

Para apenas ver a URL sem abrir o navegador:
```bash
bash cleudocode dashboard --no-open
```

### 2. Configuração Interativa
Configura modo debug, chaves de API, etc.
```bash
bash cleudocode configure
```

### 3. Gerenciamento de Plugins
Habilite ou desabilite features instantaneamente.
```bash
bash cleudocode plugins enable google-antigravity-auth
bash cleudocode plugins disable rag
```

### 4. Controle do Gateway
Reinicia a lógica do bot sem derrubar o container.
```bash
bash cleudocode gateway restart
```

## Dashboard Web
Acesse `http://localhost:8501` e verifique a aba **🛠️ Config** para gerenciar visualmente.
