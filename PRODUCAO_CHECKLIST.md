# ✅ Checklist de Produção - Community Welcome Agent

## 📋 Pré-Deploy

### 1. Requisitos do Sistema

- [ ] **CPU:** 2+ cores (4+ recomendado)
- [ ] **RAM:** 4GB+ (8GB+ recomendado)
- [ ] **Storage:** 20GB+ SSD
- [ ] **OS:** Ubuntu 20.04+ ou Windows com WSL2
- [ ] **Internet:** Conexão estável

### 2. Dependências

- [ ] Docker instalado (`docker --version`)
- [ ] Docker Compose instalado (`docker compose version`)
- [ ] Git instalado (`git --version`)
- [ ] Ollama (opcional, será instalado via Docker)

### 3. Configurações

- [ ] Token do Telegram obtido via @BotFather
- [ ] `.env` configurado com token
- [ ] Firewall configurado (portas 22, 18900)
- [ ] Domínio configurado (opcional)

---

## 🚀 Deploy

### Opção A: Script Automático (Recomendado)

```bash
cd /root/cleudocode
sudo ./deploy_production.sh
```

**O script fará:**
- [ ] Instalar Docker
- [ ] Instalar Docker Compose
- [ ] Configurar .env
- [ ] Configurar Telegram
- [ ] Configurar Ollama
- [ ] Baixar modelos
- [ ] Iniciar containers
- [ ] Verificar saúde

### Opção B: Manual

```bash
# 1. Configurar .env
cp .env.production .env
nano .env  # Edite TELEGRAM_BOT_TOKEN

# 2. Iniciar containers
docker compose -f docker-compose.welcome.yml up -d --build

# 3. Verificar
docker compose -f docker-compose.welcome.yml ps
```

---

## 🧪 Pós-Deploy

### 1. Verificações

- [ ] Gateway online: `curl http://localhost:18900/health`
- [ ] Ollama online: `curl http://localhost:11434/api/tags`
- [ ] Containers rodando: `docker compose ps`
- [ ] Logs sem erros: `docker compose logs -f`

### 2. Testar Bot

- [ ] Buscar bot no Telegram
- [ ] Enviar `/start`
- [ ] Testar mensagem: "Quero aprender IA"
- [ ] Verificar diagnóstico (BEGINNER)
- [ ] Verificar roteamento

### 3. Testar Cenários

| Mensagem | Nível Esperado | Testado |
|----------|----------------|---------|
| "Quero aprender IA do zero" | BEGINNER | [ ] |
| "Como crio uma API Flask?" | INTERMEDIATE | [ ] |
| "Arquitetura para 10k req/s" | ADVANCED | [ ] |

---

## 🔒 Segurança

- [ ] `.env` no `.gitignore`
- [ ] Firewall ativo (`sudo ufw status`)
- [ ] Apenas portas necessárias abertas
- [ ] HTTPS configurado (opcional)
- [ ] Token do Telegram seguro

---

## 📊 Monitoramento

### Logs

```bash
# Em tempo real
docker compose -f docker-compose.welcome.yml logs -f

# Últimas 50 linhas
docker compose -f docker-compose.welcome.yml logs --tail=50

# Apenas welcome-agent
docker compose -f docker-compose.welcome.yml logs -f welcome-agent
```

### Saúde

```bash
# Gateway
curl http://localhost:18900/health

# Ollama
curl http://localhost:11434/api/tags

# Containers
docker compose -f docker-compose.welcome.yml ps
```

### Métricas

- [ ] Logs configurados
- [ ] Health checks rodando
- [ ] Alertas configurados (opcional)

---

## 🔄 Manutenção

### Atualização

```bash
# Pull do código
cd /root/cleudocode
git pull

# Rebuild dos containers
docker compose -f docker-compose.welcome.yml down
docker compose -f docker-compose.welcome.yml up -d --build
```

### Backup

```bash
# Backup de dados
tar -czf backup-$(date +%Y%m%d).tar.gz /root/cleudocode/data
```

### Logs

```bash
# Rotacionar logs
docker compose -f docker-compose.welcome.yml logs --tail=1000 > logs-backup-$(date +%Y%m%d).log
```

---

## 🛠️ Troubleshooting

### Bot não responde

- [ ] Verificar token: `echo $TELEGRAM_BOT_TOKEN`
- [ ] Testar API: `curl https://api.telegram.org/bot<TOKEN>/getMe`
- [ ] Reiniciar: `docker compose restart welcome-agent`

### Ollama lento

- [ ] Usar modelo menor: `OLLAMA_MODEL=llama3:8b`
- [ ] Verificar RAM: `free -h`
- [ ] Verificar GPU: `nvidia-smi` (se tiver)

### Containers caem

- [ ] Verificar logs: `docker compose logs welcome-agent`
- [ ] Verificar memória: `docker stats`
- [ ] Aumentar recursos (se necessário)

---

## 📞 Suporte

### Documentação

- [ ] `DEPLOY_PRODUCTION.md` - Guia completo
- [ ] `WELCOME_AGENT_GUIDE.md` - Guia do agente
- [ ] `WELCOME_AGENT_SUMMARY.md` - Resumo
- [ ] `CONFIGURACAO_CORRIGIDA.md` - Configuração

### Comandos

```bash
# Menu interativo
./start_welcome_agent.sh

# Demo
python3 welcome_agent_demo.py

# Status
docker compose -f docker-compose.welcome.yml ps

# Logs
docker compose -f docker-compose.welcome.yml logs -f

# Restart
docker compose -f docker-compose.welcome.yml restart

# Stop
docker compose -f docker-compose.welcome.yml down

# Update
git pull && docker compose -f docker-compose.welcome.yml up -d --build
```

---

## ✅ Checklist Final

- [ ] Todos os itens acima verificados
- [ ] Bot respondendo no Telegram
- [ ] Logs monitorados
- [ ] Backup configurado
- [ ] Documentação acessível
- [ ] Equipe treinada

---

**Status:** ✅ **PRONTO PARA PRODUÇÃO**

**Data do Deploy:** ___/___/_____

**Responsável:** _______________________

**Observações:**

_____________________________________

_____________________________________

---

**Versão:** 1.0.0  
**Última atualização:** 2026-03-06
