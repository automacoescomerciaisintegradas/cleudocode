# Guia de Configuração: Stitch MCP com ADC

## 📋 Pré-requisitos

- ✅ Google Cloud SDK instalado
- ✅ Conta Google Cloud
- ⏳ Autenticação ADC em andamento

## 🔧 Processo de Configuração

### 1. Instalação do Google Cloud SDK

```bash
# Já concluído! ✅
gcloud --version
# Google Cloud SDK 555.0.0
```

### 2. Autenticação com Application Default Credentials (ADC)

```bash
# Em andamento... ⏳
gcloud auth application-default login
```

**Ação necessária**: Faça login no navegador que foi aberto automaticamente.

### 3. Configurar Projeto Google Cloud

Após a autenticação, você precisará:

1. **Criar ou selecionar um projeto**:
   ```bash
   # Criar novo projeto
   gcloud projects create cleudocode-PROJECT_ID --name="CleudoCode"
   
   # Ou usar projeto existente
   gcloud config set project SEU_PROJECT_ID
   ```

2. **Habilitar a API do Stitch**:
   ```bash
   gcloud services enable stitch.googleapis.com
   ```

### 4. Configuração MCP

Após habilitar a API, a configuração MCP será criada automaticamente em:
```
~/.cleudocode/mcp_stitch_config.json
```

Conteúdo:
```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": [
        "-y",
        "@google-labs/stitch-mcp-server"
      ],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "SEU_PROJECT_ID"
      }
    }
  }
}
```

### 5. Integração com Cleudocode

Para usar o Stitch MCP no Cleudocode, adicione ao `config.yaml`:

```yaml
mcp:
  enabled: true
  servers:
    stitch:
      type: "command"
      command: "npx"
      args:
        - "-y"
        - "@google-labs/stitch-mcp-server"
      env:
        GOOGLE_CLOUD_PROJECT: "SEU_PROJECT_ID"
```

## 🛠️ Ferramentas Disponíveis via Stitch MCP

Após a configuração, você terá acesso a:

1. **`extract_design_context`**: Extrai elementos de design (fontes, cores, layouts)
2. **`fetch_screen_code`**: Baixa código HTML/frontend de uma tela
3. **`fetch_screen_image`**: Baixa screenshot em alta resolução
4. **`generate_screen_from_text`**: Gera telas a partir de prompts de texto
5. **`create_project`**: Cria novo workspace/projeto
6. **`list_projects`**: Lista projetos disponíveis
7. **`list_screens`**: Lista todas as telas de um projeto
8. **`get_project`**: Obtém detalhes de um projeto específico
9. **`get_screen`**: Obtém metadados de uma tela específica

## 📝 Exemplo de Uso

```python
from core.mcp_client import MCPClient

# Inicializar cliente
mcp = MCPClient("stitch")

# Gerar uma tela
screen = mcp.call_tool(
    "generate_screen_from_text",
    {
        "prompt": "Create a modern login page with dark theme",
        "project_id": "my-project"
    }
)

# Baixar código
code = mcp.call_tool(
    "fetch_screen_code",
    {
        "screen_id": screen["id"]
    }
)
```

## 🔐 Segurança

- **Credenciais ADC** são armazenadas em: `~/.config/gcloud/application_default_credentials.json`
- **Permissões necessárias**: 
  - `stitch.projects.create`
  - `stitch.screens.create`
  - `stitch.screens.get`
  - `stitch.screens.list`

## 🐛 Troubleshooting

### Erro: "API not enabled"
```bash
gcloud services enable stitch.googleapis.com --project=SEU_PROJECT_ID
```

### Erro: "Credentials not found"
```bash
gcloud auth application-default login
```

### Erro: "Permission denied"
```bash
# Verificar permissões do projeto
gcloud projects get-iam-policy SEU_PROJECT_ID
```

## 📚 Referências

- [Stitch Documentation](https://stitch.withgoogle.com/docs)
- [MCP Servers](https://mcpservers.org)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs)
- [ADC Guide](https://cloud.google.com/docs/authentication/application-default-credentials)

---

**Status Atual**: ⏳ Aguardando autenticação no navegador

**Próximo Passo**: Complete o login no navegador e retorne ao terminal
