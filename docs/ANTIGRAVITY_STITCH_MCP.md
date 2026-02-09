# Configuração do Stitch MCP no Antigravity

## 🎯 Problema Resolvido

O erro "serverUrl or command must be specified" ocorre porque o Antigravity requer um formato específico de configuração MCP.

## ✅ Solução Implementada

### Arquivos Criados

1. **`stitch_mcp_server.py`** - Servidor MCP standalone
   - Usa stdio (stdin/stdout) para comunicação
   - Adiciona autenticação OAuth2 ADC automaticamente
   - Compatível com protocolo MCP oficial

2. **`mcp_config.json`** - Configuração para Antigravity
   - Usa `command` ao invés de `serverUrl`
   - Executa via WSL
   - Passa variáveis de ambiente necessárias

## 📝 Configuração Atual

```json
{
    "mcpServers": {
        "stitch": {
            "command": "wsl",
            "args": [
                "python3",
                "/root/cleudocode/stitch_mcp_server.py"
            ],
            "env": {
                "GOOGLE_CLOUD_PROJECT": "gen-lang-client-0700279835"
            }
        }
    }
}
```

## 🚀 Como Usar

### 1. Testar o Servidor MCP Manualmente

```bash
# No WSL
cd /root/cleudocode
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python3 stitch_mcp_server.py
```

### 2. Configurar no Antigravity

1. Abra o Antigravity
2. Vá em **Settings** → **MCP Servers**
3. Clique em **"View raw config"**
4. Cole o conteúdo do `mcp_config.json`
5. Clique em **"Refresh"**

### 3. Verificar Ferramentas

Após configurar, você deve ver:
- ✅ `list_projects` - Lista projetos do Stitch
- ✅ `get_project` - Detalhes de projeto
- ✅ `generate_screen_from_text` - Gera UI com IA

## 🔧 Troubleshooting

### Erro: "command not found: wsl"

Se você não estiver no Windows com WSL, use:

```json
{
    "mcpServers": {
        "stitch": {
            "command": "python3",
            "args": [
                "/root/cleudocode/stitch_mcp_server.py"
            ],
            "env": {
                "GOOGLE_CLOUD_PROJECT": "gen-lang-client-0700279835"
            }
        }
    }
}
```

### Erro: "Falha ao obter token"

Verifique se o gcloud ADC está configurado:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project gen-lang-client-0700279835
```

### Erro: "Permission denied"

Torne o servidor executável:

```bash
chmod +x /root/cleudocode/stitch_mcp_server.py
```

## 📊 Ferramentas Disponíveis

### 1. list_projects

Lista todos os projetos do Stitch.

**Exemplo:**
```json
{
    "name": "list_projects",
    "arguments": {}
}
```

### 2. get_project

Obtém detalhes de um projeto específico.

**Exemplo:**
```json
{
    "name": "get_project",
    "arguments": {
        "project_id": "projects/10240666840827325357"
    }
}
```

### 3. generate_screen_from_text

Gera uma tela de UI a partir de um prompt.

**Exemplo:**
```json
{
    "name": "generate_screen_from_text",
    "arguments": {
        "prompt": "Crie uma tela de login moderna com campos de email e senha",
        "device_type": "MOBILE"
    }
}
```

## 🎨 Exemplo de Uso no Antigravity

Depois de configurado, você pode usar no chat:

```
Você: Liste meus projetos do Stitch

Antigravity: [Chama list_projects]
Você tem 6 projetos:
1. AI Conversation Platform Dashboard
2. Painel do Usuário
3. Shopee Blog Content Generator
...

Você: Gere uma tela de dashboard para analytics

Antigravity: [Chama generate_screen_from_text]
Tela gerada com sucesso! ID: projects/...
```

## 📁 Localização dos Arquivos

- **Servidor MCP**: `/root/cleudocode/stitch_mcp_server.py`
- **Config Antigravity**: `C:\Users\autom\.gemini\antigravity\mcp_config.json`
- **Credenciais ADC**: `~/.config/gcloud/application_default_credentials.json`

## ✅ Checklist de Validação

- [ ] Google Cloud SDK instalado
- [ ] ADC configurado (`gcloud auth application-default login`)
- [ ] Quota project definido
- [ ] Stitch API habilitada
- [ ] Servidor MCP criado
- [ ] Config MCP atualizado no Antigravity
- [ ] Ferramentas aparecem no Antigravity

## 🎉 Resultado Esperado

Após a configuração, você verá no Antigravity:

```
Manage MCP servers
3 / 100 tools

stitch
✅ Connected
- list_projects
- get_project  
- generate_screen_from_text
```

---

**Status**: ✅ Pronto para uso!
