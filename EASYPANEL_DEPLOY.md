# Implantação no EasyPanel

Este documento descreve como implantar o Cleudocodebot no EasyPanel nas portas 3001 e 3002 (a porta 3000 já é usada pelo EasyPanel).

## Visão Geral

O Cleudocodebot pode ser implantado no EasyPanel para execução em ambiente de produção com alta disponibilidade e gerenciamento facilitado.

## Requisitos

- Acesso SSH à VPS com EasyPanel instalado
- Portas 3001 e 3002 disponíveis (a porta 3000 já é usada pelo EasyPanel)
- Servidor Ollama rodando (local ou remoto)
- Docker e Docker Compose instalados

## Método 1: Script de Instalação Automática

Execute o script de instalação automática:

```bash
# Baixar e executar o script de instalação
wget https://raw.githubusercontent.com/automacoescomerciaisintegradas/cleudocode/main/install_easypanel.sh
chmod +x install_easypanel.sh
./install_easypanel.sh
```

O script irá:
- Instalar dependências necessárias
- Configurar o ambiente Python
- Criar arquivos de configuração para EasyPanel
- Preparar o sistema para execução via Docker

## Método 2: Implantação Manual via EasyPanel

### 1. Acesse o EasyPanel
Acesse o painel de administração do EasyPanel em: https://easypanel.automacoescomerciais.com.br/projects/vibecoding/create

### 2. Configure o Projeto
- **Project Type**: Docker Compose
- **Repository URL**: https://github.com/automacoescomerciaisintegradas/cleudocode.git
- **Branch**: main
- **Working Directory**: (deixe vazio ou use ./)
- **Docker Compose File**: docker-compose.easypanel.yml
- **Port**: 3001

### 3. Configure Variáveis de Ambiente

Adicione as seguintes variáveis de ambiente:

```
OLLAMA_HOST=http://host.docker.internal:11434
DEEPSEEK_MODEL=qwen2.5-coder:7b
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5001
STREAMLIT_SERVER_PORT=3001
STREAMLIT_SERVER_ADDRESS=0.0.0.0
FLASK_SECRET_KEY=sua_chave_secreta_aqui
SECURITY_SECRET_KEY=sua_chave_seguranca_aqui
```

### 4. Deploy

Clique em "Deploy" e o sistema será iniciado automaticamente.

## Configuração Pós-Implantação

### 1. Acesso ao Sistema
Após o deploy bem-sucedido, o sistema estará disponível em:

- **API REST**: http://seu-ip:3002
- **Interface Web**: http://seu-ip:3001
- **Dashboard de Monitoramento**: http://seu-ip:3001/dashboard

### 2. Configuração de Canais

Para configurar canais de comunicação (WhatsApp, Telegram, Discord, etc.), edite o arquivo `.env` ou adicione as variáveis de ambiente correspondentes no EasyPanel:

```
# WhatsApp
WHATSAPP_ID_INSTANCE=sua_instancia
WHATSAPP_API_TOKEN_INSTANCE=seu_token

# Telegram
TELEGRAM_BOT_TOKEN=seu_token_telegram

# Discord
DISCORD_TOKEN=seu_token_discord

# Outros canais...
```

### 3. Monitoramento

O sistema inclui endpoints de monitoramento:

- `GET /api/v1/status` - Verifica status do sistema
- `GET /api/v1/health` - Health check do sistema
- `GET /api/v1/metrics` - Métricas do sistema

## Atualização do Sistema

Para atualizar o sistema com as últimas alterações:

1. No EasyPanel, vá até o projeto cleudocodebot
2. Clique em "Update" para puxar as últimas alterações do repositório
3. O sistema será reconstruído e reiniciado automaticamente

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão com Ollama**
   - Verifique se o servidor Ollama está rodando
   - Confirme que a URL em `OLLAMA_HOST` está correta
   - Verifique se o modelo especificado em `DEEPSEEK_MODEL` está instalado

2. **Portas já em uso**
   - Verifique se as portas 3001 e 3002 estão disponíveis (a porta 3000 já é usada pelo EasyPanel)
   - Verifique se não há outros containers usando essas portas

3. **Permissões de Docker**
   - Verifique se o usuário tem permissão para executar comandos Docker
   - Execute `newgrp docker` ou faça logout/login para aplicar permissões

4. **Erro de memória**
   - Aumente os recursos alocados no EasyPanel
   - Verifique se o modelo LLM não está consumindo muita memória

### Verificação de Status

```bash
# Verificar status dos containers
docker-compose -f docker-compose.easypanel.yml ps

# Verificar logs
docker-compose -f docker-compose.easypanel.yml logs -f

# Verificar uso de recursos
docker stats
```

## Segurança

- **Nunca compartilhe chaves de API** em arquivos públicos
- **Use variáveis de ambiente** para informações sensíveis
- **Altere as chaves padrão** antes de usar em produção
- **Configure firewall** para restringir acesso às portas
- **Use HTTPS** com proxy reverso para acesso externo

## Backup e Restauração

### Backup

Para fazer backup dos dados do sistema:

```bash
# Backup dos dados persistentes
tar -czf cleudocode-backup-$(date +%Y%m%d_%H%M%S).tar.gz data/ exports/ uploads/ memory_db/
```

### Restauração

Para restaurar dados de backup:

```bash
# Parar o sistema primeiro
docker-compose -f docker-compose.easypanel.yml down

# Restaurar dados
tar -xzf seu-backup.tar.gz

# Reiniciar o sistema
docker-compose -f docker-compose.easypanel.yml up -d
```

## Suporte

- **Documentação**: Leia o README.md e DOCUMENTACAO.md no repositório
- **Issues**: Abra uma issue no GitHub se encontrar problemas
- **Contato**: contato@automacoescomerciais.com.br