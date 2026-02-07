# 🚀 Guia de Início Rápido - Cleudocode (OpenClaw-like)

## O que mudou?

O Cleudocode agora funciona de forma similar ao **OpenClaw**, com:

✅ **Autenticação via Token** - Dashboard protegido por token UUID  
✅ **CLI Poderoso** - Comando `cleudocode dashboard` abre o dashboard automaticamente  
✅ **Configuração Centralizada** - Arquivo `config.yaml` em `~/.cleudocode/`  
✅ **Estrutura Organizada** - Workspace, memória, skills e logs separados  

---

## 📦 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/cleudocode/cleudocode
cd cleudocode
```

### 2. Criar Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate   # Windows
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
pip install pyyaml  # Necessário para config.yaml
```

### 4. Configurar Ollama

Certifique-se de que o Ollama está rodando:

```bash
# Verificar se está rodando
curl http://localhost:11434/api/tags

# Se não estiver, inicie:
ollama serve
```

---

## 🎯 Primeiro Uso

### 1. Inicializar o Sistema

```bash
python cli/main.py onboard
```

Isso vai:
- Criar o arquivo `.env` (se não existir)
- Verificar conexão com Ollama
- Criar estrutura de diretórios em `~/.cleudocode/`
- Gerar token de autenticação

### 2. Abrir o Dashboard

```bash
python cli/main.py dashboard
```

Isso vai:
- Gerar/ler o token de autenticação
- Iniciar o dashboard Streamlit
- Abrir automaticamente no navegador com autenticação

**Pronto!** Você está autenticado e pode usar o dashboard.

---

## 🔑 Autenticação

### Como funciona?

1. Um token UUID único é gerado em `~/.cleudocode/.gateway_token`
2. O comando `cleudocode dashboard` lê esse token
3. Abre o navegador com a URL: `http://localhost:8501?token=SEU_TOKEN`
4. O dashboard valida o token e autentica automaticamente

### Login Manual

Se você abrir o dashboard manualmente (`streamlit run web_app.py`), verá uma tela de login.

**Para obter o token:**

```bash
# Opção 1: Ver o token
cat ~/.cleudocode/.gateway_token

# Opção 2: Usar o CLI (recomendado)
python cli/main.py dashboard
```

---

## 📋 Comandos Disponíveis

### Dashboard

```bash
# Abrir dashboard (porta padrão 8501)
python cli/main.py dashboard

# Porta customizada
python cli/main.py dashboard --port 8502

# Não abrir navegador
python cli/main.py dashboard --no-browser
```

### Configuração

```bash
# Ver configuração atual
python cli/main.py config

# Ver configuração com segredos
python cli/main.py config --show-secrets
```

### Serviços

```bash
# Iniciar todos os serviços
python cli/main.py start

# Parar serviços
python cli/main.py stop

# Ver status
python cli/main.py status
```

### Canais

```bash
# Adicionar canal Telegram
python cli/main.py channels add --channel telegram --token SEU_TOKEN

# Adicionar canal Discord
python cli/main.py channels add --channel discord --token SEU_TOKEN
```

### Memória

```bash
# Exportar memória para NotebookLM
python cli/main.py memory export
```

### Workflows

```bash
# Listar workflows
python cli/main.py workflows list

# Executar workflow
python cli/main.py workflows run NOME_DO_WORKFLOW
```

---

## 📁 Estrutura de Diretórios

```
~/.cleudocode/
├── config.yaml          # Configuração centralizada
├── .gateway_token       # Token de autenticação (UUID)
├── workspace/           # Área de trabalho do agente
├── memory/              # Banco de dados ChromaDB
├── skills/              # Skills/plugins instalados
├── logs/                # Logs do sistema
├── cache/               # Cache temporário
└── browser_data/        # Dados do navegador automatizado
```

---

## ⚙️ Configuração (config.yaml)

O arquivo `~/.cleudocode/config.yaml` centraliza todas as configurações:

```yaml
# Exemplo de configuração
system:
  name: "Cleudocode"
  version: "1.0.0"

gateway:
  host: "0.0.0.0"
  port: 18900
  enable_auth: true

llm:
  default_provider: "ollama"
  default_model: "qwen2.5-coder"

channels:
  telegram:
    enabled: false
    bot_token: "${TELEGRAM_BOT_TOKEN}"
```

**Variáveis de ambiente** são expandidas automaticamente usando `${VAR_NAME}`.

---

## 🔒 Segurança

### Token de Autenticação

- Gerado automaticamente no primeiro uso
- Armazenado em `~/.cleudocode/.gateway_token`
- Permissões restritas (600 no Unix)
- Válido por 365 dias (configurável)

### Resetar Token

Se você quiser gerar um novo token:

```bash
# Deletar token atual
rm ~/.cleudocode/.gateway_token

# Próximo uso do CLI gerará novo token
python cli/main.py dashboard
```

---

## 🐛 Troubleshooting

### Dashboard não abre

```bash
# Verificar se Streamlit está instalado
pip install streamlit

# Verificar se porta está livre
netstat -an | grep 8501

# Tentar porta diferente
python cli/main.py dashboard --port 8502
```

### Erro de autenticação

```bash
# Verificar se token existe
cat ~/.cleudocode/.gateway_token

# Deletar e regenerar
rm ~/.cleudocode/.gateway_token
python cli/main.py dashboard
```

### Ollama não conecta

```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Iniciar Ollama
ollama serve

# Verificar modelo instalado
ollama list
ollama pull qwen2.5-coder:7b
```

---

## 📚 Próximos Passos

1. **Explorar o Dashboard** - Teste o chat, memória RAG e playground
2. **Adicionar Canais** - Configure Telegram, Discord ou WhatsApp
3. **Criar Skills** - Estenda as capacidades do assistente
4. **Automatizar Workflows** - Use o Lobster Engine para automações

---

## 🆘 Suporte

- **GitHub**: https://github.com/cleudocode/cleudocode
- **NotebookLM**: https://notebooklm.google.com/notebook/8dc6916e-a1b0-4cdd-b6f7-50e4dafb5c69
- **WhatsApp**: +55 88 92156-7214

---

## 📝 Comparação com OpenClaw

| Recurso | OpenClaw | Cleudocode |
|---------|----------|------------|
| Autenticação via Token | ✅ | ✅ |
| CLI com comando `dashboard` | ✅ | ✅ |
| Config centralizado (YAML) | ✅ | ✅ |
| Multi-canal (Telegram, Discord, etc.) | ✅ | ✅ |
| Memória Persistente (RAG) | ✅ | ✅ |
| Browser Control | ✅ | ✅ |
| Skills/Plugins | ✅ | 🚧 Em desenvolvimento |
| Marketplace de Skills | ✅ | 🚧 Planejado |

---

**Desenvolvido por Automações Comerciais Integradas ⚙️**  
© 2025 - Todos os direitos reservados
