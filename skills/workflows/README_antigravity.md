# 🚀 Workflows Antigravity - Cleudocode

## 📋 Visão Geral
Workflows automatizados para interagir com o sistema **Antigravity** da Automações Comerciais Integradas.

**Total de Workflows**: 5 workflows especializados

---

## 🎯 Workflows Disponíveis

### 1. 🔍 Antigravity Status Check
**Arquivo**: `antigravity_status.lobster`  
**Descrição**: Verifica o status e saúde do sistema Antigravity  
**Frequência**: Diário (9h da manhã)  

**Funcionalidades**:
- ✅ Verifica se o processo está rodando
- ✅ Testa conectividade da API
- ✅ Monitora uso de recursos (CPU, memória, disco)
- ✅ Analisa logs de erro
- ✅ Gera relatório detalhado
- ✅ Envia notificações via Telegram

**Uso**:
```bash
python workflow_manager.py run "Antigravity Status Check"
```

---

### 2. 🔄 Antigravity Sync
**Arquivo**: `antigravity_sync.lobster`  
**Descrição**: Sincroniza dados entre Cleudocode e Antigravity  
**Frequência**: A cada hora  

**Funcionalidades**:
- ✅ Backup automático antes da sincronização
- ✅ Conectividade com API Antigravity
- ✅ Download de dados remotos
- ✅ Upload de dados locais
- ✅ Comparação e detecção de diferenças
- ✅ Verificação de integridade
- ✅ Log detalhado de operações

**Uso**:
```bash
python workflow_manager.py run "Antigravity Sync"
```

---

### 3. 💾 Antigravity Backup
**Arquivo**: `antigravity_backup.lobster`  
**Descrição**: Cria backup completo do sistema Antigravity  
**Frequência**: Diário (2h da manhã)  

**Funcionalidades**:
- ✅ Verificação de espaço em disco
- ✅ Parada segura de serviços
- ✅ Backup de dados, configurações e logs
- ✅ Compactação e verificação de integridade
- ✅ Geração de checksum SHA256
- ✅ Limpeza automática de backups antigos
- ✅ Reinicialização de serviços

**Uso**:
```bash
python workflow_manager.py run "Antigravity Backup"
```

---

### 4. 🚀 Antigravity Deploy
**Arquivo**: `antigravity_deploy.lobster`  
**Descrição**: Deploy automatizado do sistema Antigravity  
**Frequência**: Sob demanda  

**Funcionalidades**:
- ✅ Testes pré-deploy
- ✅ Backup da versão atual
- ✅ Clone/pull do repositório
- ✅ Instalação de dependências
- ✅ Build automatizado
- ✅ Health checks pós-deploy
- ✅ Rollback automático em caso de falha
- ✅ Testes de fumaça

**Uso**:
```bash
python workflow_manager.py run "Antigravity Deploy"
```

**Com parâmetros**:
```bash
python workflow_manager.py run "Antigravity Deploy" branch=develop
```

---

### 5. 📊 Antigravity Monitor
**Arquivo**: `antigravity_monitor.lobster`  
**Descrição**: Monitoramento contínuo do sistema Antigravity  
**Frequência**: A cada 5 minutos  

**Funcionalidades**:
- ✅ Monitoramento de status do serviço
- ✅ Health check da API
- ✅ Medição de tempo de resposta
- ✅ Monitoramento de recursos (CPU, memória, disco)
- ✅ Análise de logs de erro
- ✅ Verificação de conectividade
- ✅ Alertas inteligentes
- ✅ Log contínuo de métricas

**Uso**:
```bash
python workflow_manager.py run "Antigravity Monitor"
```

---

## ⚙️ Configuração

### Variáveis Globais
Edite os workflows para ajustar as seguintes variáveis:

```yaml
# Caminhos do Antigravity
antigravity_path: "/opt/antigravity"
antigravity_data: "/var/lib/antigravity"
antigravity_config: "/etc/antigravity"

# API e Conectividade
antigravity_api: "http://localhost:8080/api"
health_check_url: "http://localhost:8080/health"

# Repositório
antigravity_repo: "https://github.com/automacoescomerciaisintegradas/antigravity.git"

# Backup
backup_root: "./backups/antigravity"
retention_days: 30

# Alertas
alert_threshold_cpu: 80
alert_threshold_memory: 85
alert_threshold_disk: 90
alert_threshold_errors: 10
```

### Agendamento Automático

#### Windows (Task Scheduler)
```powershell
# Monitoramento (a cada 5 minutos)
schtasks /create /tn "Antigravity Monitor" /tr "python workflow_manager.py run 'Antigravity Monitor'" /sc minute /mo 5

# Status diário (9h)
schtasks /create /tn "Antigravity Status" /tr "python workflow_manager.py run 'Antigravity Status Check'" /sc daily /st 09:00

# Backup diário (2h)
schtasks /create /tn "Antigravity Backup" /tr "python workflow_manager.py run 'Antigravity Backup'" /sc daily /st 02:00

# Sincronização (a cada hora)
schtasks /create /tn "Antigravity Sync" /tr "python workflow_manager.py run 'Antigravity Sync'" /sc hourly
```

#### Linux/Mac (Cron)
```bash
# Adicionar ao crontab
crontab -e

# Monitoramento (a cada 5 minutos)
*/5 * * * * cd /path/to/cleudocode && python workflow_manager.py run "Antigravity Monitor"

# Status diário (9h)
0 9 * * * cd /path/to/cleudocode && python workflow_manager.py run "Antigravity Status Check"

# Backup diário (2h)
0 2 * * * cd /path/to/cleudocode && python workflow_manager.py run "Antigravity Backup"

# Sincronização (a cada hora)
0 * * * * cd /path/to/cleudocode && python workflow_manager.py run "Antigravity Sync"
```

---

## 📊 Monitoramento e Alertas

### Métricas Coletadas
- **Status do Serviço**: Ativo/Inativo
- **API Health**: Tempo de resposta e código HTTP
- **Recursos**: CPU, memória, disco
- **Logs**: Contagem de erros por período
- **Conectividade**: Rede e portas
- **Integridade**: Verificação de dados

### Alertas Configurados
- 🚨 **Serviço Inativo**: Antigravity parou de funcionar
- 🚨 **API Indisponível**: Health check falhou
- 🚨 **CPU Alta**: Acima de 80%
- 🚨 **Memória Alta**: Acima de 85%
- 🚨 **Disco Cheio**: Acima de 90%
- 🚨 **Muitos Erros**: Mais de 10 erros por hora
- 🚨 **Deploy Falhou**: Processo de deploy com problemas
- 🚨 **Backup Falhou**: Backup não foi concluído

### Notificações
Todas as notificações são enviadas via **Telegram** com:
- ✅ Status resumido
- 📊 Métricas principais
- 🚨 Alertas destacados
- 📄 Links para logs detalhados

---

## 🔧 Troubleshooting

### Workflow não executa
```bash
# Verificar se o workflow existe
python workflow_manager.py list | grep Antigravity

# Executar com debug
python workflow_manager.py run "Antigravity Status Check" --debug
```

### Erro de conectividade
```bash
# Testar conectividade manual
curl -f http://localhost:8080/health

# Verificar se o serviço está rodando
systemctl status antigravity
```

### Backup falha
```bash
# Verificar espaço em disco
df -h

# Verificar permissões
ls -la /opt/antigravity
```

### Deploy falha
```bash
# Verificar logs do deploy
cat reports/deploy_*.txt

# Verificar status do serviço
systemctl status antigravity
journalctl -u antigravity -f
```

---

## 📁 Estrutura de Arquivos

```
skills/workflows/
├── antigravity_status.lobster      # Status check
├── antigravity_sync.lobster        # Sincronização
├── antigravity_backup.lobster      # Backup
├── antigravity_deploy.lobster      # Deploy
├── antigravity_monitor.lobster     # Monitoramento
└── README_antigravity.md           # Esta documentação

backups/antigravity/                # Backups automáticos
├── 20260204/                       # Backup por data
├── antigravity_backup_20260204.tar.gz
└── backup_report_20260204.txt

reports/                            # Relatórios
├── antigravity_status_20260204.txt
├── deploy_20260204_143022.txt
└── health_20260204_143022.txt

logs/                               # Logs dos workflows
├── antigravity_sync_20260204_143022.log
└── antigravity_monitor_20260204.log
```

---

## 🎯 Casos de Uso

### Rotina de Produção
1. **Monitor contínuo** (5 min) - Detecta problemas rapidamente
2. **Status matinal** (9h) - Relatório diário de saúde
3. **Backup noturno** (2h) - Proteção de dados
4. **Sync horária** - Dados sempre atualizados

### Deploy de Nova Versão
1. Executar `Antigravity Deploy`
2. Monitorar alertas automáticos
3. Verificar relatório de deploy
4. Rollback automático se necessário

### Recuperação de Desastre
1. Parar serviços
2. Restaurar do backup mais recente
3. Executar `Antigravity Status Check`
4. Verificar integridade dos dados

---

## 🔐 Segurança

### Boas Práticas
- ✅ Logs não contêm informações sensíveis
- ✅ Backups são verificados por integridade
- ✅ Credenciais são armazenadas de forma segura
- ✅ Acesso restrito aos workflows críticos
- ✅ Auditoria de todas as operações

### Permissões Necessárias
- **Leitura**: Logs e configurações do Antigravity
- **Escrita**: Diretórios de backup e relatórios
- **Execução**: Comandos systemctl e curl
- **Rede**: Acesso à API do Antigravity

---

## 📚 Recursos Adicionais

- **Especificação Completa**: `.kiro/specs/antigravity-workflows.md`
- **Documentação Lobster**: `skills/workflows/README.md`
- **Logs do Sistema**: `logs/cleudocode.log`
- **Repositório Antigravity**: https://github.com/automacoescomerciaisintegradas/antigravity

---

**Última atualização**: 2026-02-04  
**Versão**: 1.0  
**Autor**: Cleudocode Team