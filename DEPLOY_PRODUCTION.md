# 🚀 Guia de Deploy em Produção - Community Welcome Agent

## Visão Geral

Este guia cobre a implantação do **Community Welcome Agent** em diferentes ambientes de produção.

---

## 📋 Pré-requisitos

### Mínimos
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 20GB
- **OS:** Linux (Ubuntu 20.04+) ou Windows com WSL2

### Recomendados
- **CPU:** 4+ cores
- **RAM:** 8GB+
- **Storage:** 50GB+ SSD
- **GPU:** NVIDIA (opcional, para IA mais rápida)

---

## 🎯 Opções de Deploy

### Opção 1: Deploy com Docker (Recomendado) ⭐

#### 1. Instalar Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Verificar instalação
docker --version
docker compose version
```

#### 2. Configurar Variáveis de Ambiente

```bash
cd /root/cleudocode

# Copiar arquivo de produção
cp .env.production .env

# Editar com suas credenciais
nano .env
```

**Edite no `.env`:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OLLAMA_MODEL=llama3:8b
```

#### 3. Iniciar com Docker Compose

```bash
# Build e start
docker compose -f docker-compose.welcome.yml up -d --build

# Ver logs
docker compose -f docker-compose.welcome.yml logs -f welcome-agent

# Ver status
docker compose -f docker-compose.welcome.yml ps
```

#### 4. Testar

```bash
# Testar gateway
curl http://localhost:18900/health

# Testar Ollama
curl http://localhost:11434/api/tags
```

#### 5. Comandos Úteis

```bash
# Parar tudo
docker compose -f docker-compose.welcome.yml down

# Reiniciar
docker compose -f docker-compose.welcome.yml restart

# Ver logs em tempo real
docker compose -f docker-compose.welcome.yml logs -f

# Atualizar
docker compose -f docker-compose.welcome.yml pull
docker compose -f docker-compose.welcome.yml up -d
```

---

### Opção 2: Deploy Direto (Sem Docker)

#### 1. Instalar Dependências

```bash
# Python 3.10+
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip git curl

# Node.js (opcional)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. Configurar Ollama

```bash
# Iniciar Ollama
ollama serve &

# Baixar modelo
ollama pull llama3:8b

# Verificar
ollama list
```

#### 3. Configurar Projeto

```bash
cd /root/cleudocode

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install python-telegram-bot

# Configurar .env
cp .env.production .env
nano .env  # Edite TELEGRAM_BOT_TOKEN
```

#### 4. Criar Serviço Systemd

```bash
sudo nano /etc/systemd/system/welcome-agent.service
```

**Conteúdo:**
```ini
[Unit]
Description=CleudoCode Welcome Agent
After=network.target ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/cleudocode
Environment="PATH=/root/cleudocode/venv/bin"
ExecStart=/root/cleudocode/venv/bin/python3 telegram_welcome_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Ativar serviço:**
```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar
sudo systemctl enable welcome-agent
sudo systemctl start welcome-agent

# Ver status
sudo systemctl status welcome-agent

# Ver logs
sudo journalctl -u welcome-agent -f
```

---

### Opção 3: Deploy em VPS (Cloud)

#### Provedores Recomendados

| Provedor | Config | Preço/mês |
|----------|--------|-----------|
| **Hetzner** | 4 vCPU, 8GB RAM | ~€5 |
| **DigitalOcean** | 2 vCPU, 4GB RAM | ~$12 |
| **Linode** | 2 vCPU, 4GB RAM | ~$12 |
| **AWS EC2** | t3.medium | ~$30 |

#### Passos

1. **Criar VPS** (Ubuntu 22.04)
2. **Segurança:**
   ```bash
   # Firewall
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 18900/tcp # Gateway
   sudo ufw enable
   ```

3. **Seguir Opção 2** (Deploy Direto)

4. **Configurar Domínio (Opcional)**

   ```bash
   # Instalar Nginx
   sudo apt install -y nginx
   
   # Configurar reverse proxy
   sudo nano /etc/nginx/sites-available/cleudocode
   ```

   **Conteúdo:**
   ```nginx
   server {
       listen 80;
       server_name seu-dominio.com;
       
       location / {
           proxy_pass http://localhost:18900;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   **Ativar:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/cleudocode /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

---

### Opção 4: Deploy no Telegram (Bot)

#### 1. Criar Bot

1. Abra **@BotFather** no Telegram
2. Envie `/newbot`
3. Siga as instruções:
   - Nome: `CleudoCode Welcome Bot`
   - Username: `cleudocode_welcome_bot`
4. Copie o **token**

#### 2. Configurar

```bash
# No .env:
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

#### 3. Comandos do Bot

Configure no @BotFather:

```
/setcommands
cleudocode_welcome_bot

start - Iniciar acolhimento
help - Ajuda
status - Ver status
reset - Reiniciar conversa
```

#### 4. Iniciar Bot

```bash
# Docker
docker compose -f docker-compose.welcome.yml up -d welcome-agent

# Direto
python3 telegram_welcome_bot.py

# Serviço
sudo systemctl start welcome-agent
```

---

## 🔒 Segurança

### 1. Firewall

```bash
# Ubuntu
sudo ufw allow 22/tcp
sudo ufw allow 18900/tcp
sudo ufw enable
sudo ufw status
```

### 2. HTTPS (Recomendado)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Gerar certificado
sudo certbot --nginx -d seu-dominio.com
```

### 3. Variáveis Sensíveis

**NUNCA commitar `.env`!**

```bash
# Verificar se .env está no .gitignore
grep ".env" .gitignore

# Se não estiver:
echo ".env" >> .gitignore
```

---

## 📊 Monitoramento

### 1. Logs

```bash
# Docker
docker compose -f docker-compose.welcome.yml logs -f

# Systemd
sudo journalctl -u welcome-agent -f

# Arquivo
tail -f /root/cleudocode/logs/*.log
```

### 2. Health Check

```bash
# Gateway
curl http://localhost:18900/health

# Ollama
curl http://localhost:11434/api/tags

# Bot (via Telegram)
Envie /status para o bot
```

### 3. Métricas

**Arquivo de status:**
```bash
cat /root/cleudocode/.agent_status.json
```

---

## 🔄 Atualização

### Docker

```bash
cd /root/cleudocode
git pull
docker compose -f docker-compose.welcome.yml down
docker compose -f docker-compose.welcome.yml up -d --build
```

### Direto

```bash
cd /root/cleudocode
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart welcome-agent
```

---

## 🛠️ Troubleshooting

### Bot não responde

```bash
# Verificar token
echo $TELEGRAM_BOT_TOKEN

# Testar API Telegram
curl https://api.telegram.org/bot<SEU_TOKEN>/getMe

# Reiniciar
sudo systemctl restart welcome-agent
```

### Ollama lento

```bash
# Usar modelo menor
# No .env:
OLLAMA_MODEL=llama3:8b

# Ou usar fallback (regras)
# Já está habilitado automaticamente!
```

### Erro de conexão

```bash
# Verificar se serviços estão rodando
docker compose -f docker-compose.welcome.yml ps

# Ou
sudo systemctl status welcome-agent
sudo systemctl status ollama

# Ver logs
sudo journalctl -u welcome-agent -n 50
```

---

## 📈 Escala

### Horizontal (Múltiplos Bots)

```yaml
# docker-compose.welcome.yml
welcome-agent:
  replicas: 3
  environment:
    - INSTANCE_ID=${HOSTNAME}
```

### Cache (Redis)

```bash
# Adicionar ao docker-compose.yml
redis:
  image: redis:alpine
  ports:
    - "6379:6379"
```

### Banco de Dados

```bash
# PostgreSQL
postgres:
  image: postgres:15
  environment:
    - POSTGRES_DB=cleudocode
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

---

## ✅ Checklist de Produção

- [ ] Docker instalado
- [ ] Ollama configurado e testado
- [ ] Token do Telegram obtido
- [ ] `.env` configurado
- [ ] Firewall configurado
- [ ] HTTPS habilitado (opcional)
- [ ] Serviço rodando
- [ ] Logs monitorados
- [ ] Backup configurado
- [ ] Documentação acessível

---

## 🎉 Pós-Deploy

### Testar no Telegram

1. Busque pelo bot no Telegram
2. Envie `/start`
3. Teste diferentes mensagens:
   - "Quero aprender IA"
   - "Como criar API?"
   - "Arquitetura para alta escala"

### Monitorar

```bash
# Dashboard (se habilitado)
http://localhost:18900

# Logs em tempo real
tail -f /root/cleudocode/logs/*.log
```

---

## 📞 Suporte

**Documentação completa:**
- `WELCOME_AGENT_GUIDE.md` - Guia do agente
- `WELCOME_AGENT_SUMMARY.md` - Resumo
- `CONFIGURACAO_CORRIGIDA.md` - Configuração

**Comandos úteis:**
```bash
# Status
./start_welcome_agent.sh

# Demo
python3 welcome_agent_demo.py

# Help
python3 telegram_welcome_bot.py --help
```

---

**Última atualização:** 2026-03-06  
**Versão:** 1.0.0  
**Status:** ✅ **PRONTO PARA PRODUÇÃO**
