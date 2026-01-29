# 🦞 Workflows Práticos - Lobster Engine

## 📋 Visão Geral

Este diretório contém **workflows práticos** para automação de tarefas do dia a dia usando o **Lobster Workflow Engine**.

**Total de Workflows**: 7 workflows prontos para uso

---

## 🚀 Como Usar

### Listar Workflows Disponíveis

```bash
python workflow_manager.py list
```

### Ver Detalhes de um Workflow

```bash
python workflow_manager.py info "Nome do Workflow"
```

### Executar um Workflow

```bash
python workflow_manager.py run "Nome do Workflow"
```

### Executar com Variáveis

```bash
python workflow_manager.py run "Backup Diário Automático" project_name=meu_projeto
```

### Menu Interativo

```bash
python workflow_manager.py
```

---

## 📦 Workflows Disponíveis

### 1. 💾 Backup Diário Automático

**Arquivo**: `backup_diario.lobster`

**Descrição**: Faz backup completo do projeto com compactação e notificação

**Steps**:
1. Criar diretório de backup
2. Listar arquivos do projeto
3. Criar arquivo de log
4. Copiar arquivos Python
5. Copiar configurações
6. Copiar skills e workflows
7. Criar README do backup
8. Notificar conclusão via Telegram

**Variáveis**:
- `project_path`: Caminho do projeto (padrão: ".")
- `backup_dest`: Destino do backup (padrão: "./backups")
- `project_name`: Nome do projeto (padrão: "cleudocode")

**Uso**:
```bash
python workflow_manager.py run "Backup Diário Automático"
```

**Resultado**:
- Backup completo em `backups/YYYYMMDD/`
- Log detalhado
- README com instruções de restauração
- Notificação via Telegram

---

### 2. 🧹 Limpeza de Arquivos Temporários

**Arquivo**: `limpeza_sistema.lobster`

**Descrição**: Remove arquivos temporários e cache para liberar espaço

**Steps**:
1. Verificar espaço em disco (antes)
2. Limpar cache Python (`__pycache__`, `*.pyc`)
3. Limpar logs antigos (>7 dias)
4. Limpar arquivos temporários
5. Verificar espaço em disco (depois)
6. Criar relatório de limpeza
7. Notificar conclusão

**Uso**:
```bash
python workflow_manager.py run "Limpeza de Arquivos Temporários"
```

**Resultado**:
- Cache Python removido
- Logs antigos deletados
- Relatório em `reports/limpeza_YYYYMMDD.txt`
- Notificação com espaço liberado

---

### 3. 📊 Relatório de Atividades Diário

**Arquivo**: `relatorio_diario.lobster`

**Descrição**: Gera relatório consolidado das atividades do dia

**Steps**:
1. Coletar logs do sistema
2. Contar mensagens processadas
3. Verificar erros do dia
4. Listar workflows executados
5. Gerar relatório em Markdown
6. Criar versão em texto
7. Enviar relatório por Telegram

**Uso**:
```bash
python workflow_manager.py run "Relatório de Atividades Diário"
```

**Resultado**:
- Relatório Markdown: `reports/diario_YYYYMMDD.md`
- Relatório texto: `reports/diario_YYYYMMDD.txt`
- Estatísticas consolidadas
- Notificação via Telegram

---

### 4. 🏥 Monitoramento de Saúde do Sistema

**Arquivo**: `monitoramento_sistema.lobster`

**Descrição**: Verifica saúde do sistema e alerta sobre problemas

**Steps**:
1. Verificar uso de disco
2. Verificar uso de memória
3. Verificar processos Python
4. Verificar logs de erro recentes
5. Verificar conectividade
6. Gerar relatório de saúde
7. Alertar se houver problemas

**Uso**:
```bash
python workflow_manager.py run "Monitoramento de Saúde do Sistema"
```

**Resultado**:
- Relatório completo: `reports/health_YYYYMMDD_HHMMSS.txt`
- Alertas inteligentes via Telegram
- Status de disco, memória, processos
- Verificação de conectividade

---

### 5. 📦 Atualização de Dependências

**Arquivo**: `atualizar_dependencias.lobster`

**Descrição**: Verifica e atualiza dependências do projeto

**Steps**:
1. Listar dependências atuais
2. Verificar dependências desatualizadas
3. Criar backup do requirements
4. Gerar novo requirements
5. Criar relatório de atualizações
6. Notificar conclusão

**Uso**:
```bash
python workflow_manager.py run "Atualização de Dependências"
```

**Resultado**:
- Backup: `requirements.txt.backup_YYYYMMDD`
- Novo requirements: `requirements_new.txt`
- Relatório: `reports/atualizacoes_YYYYMMDD.md`
- Lista de pacotes desatualizados

---

### 6. 🔄 Sincronização com Git

**Arquivo**: `git_sync.lobster`

**Descrição**: Sincroniza projeto com repositório Git

**Steps**:
1. Verificar status do Git
2. Adicionar arquivos modificados
3. Criar commit
4. Pull das últimas alterações
5. Push para o repositório
6. Verificar log recente
7. Criar relatório de sincronização
8. Notificar resultado

**Variáveis**:
- `branch`: Branch para sincronizar (padrão: "main")
- `commit_message`: Mensagem do commit (padrão: "Auto-commit: TIMESTAMP")

**Uso**:
```bash
python workflow_manager.py run "Sincronização com Git" branch=develop
```

**Resultado**:
- Commit automático
- Pull e push executados
- Relatório: `reports/git_sync_YYYYMMDD.txt`
- Notificação de sucesso/erro

---

### 7. ✅ Teste Rápido

**Arquivo**: `test_quick.lobster`

**Descrição**: Workflow de teste para validar Lobster Engine

**Steps**:
1. Criar diretório de teste
2. Escrever arquivo de teste
3. Listar arquivos criados
4. Ler arquivo criado

**Uso**:
```bash
python workflow_manager.py run "Teste Rápido"
```

**Resultado**:
- Diretório: `test_lobster_output/`
- Arquivo de teste gerado
- Validação completa do engine

---

## 🔧 Criando Seus Próprios Workflows

### Estrutura Básica

```yaml
name: "Meu Workflow"
description: "Descrição do que faz"
version: "1.0"
author: "Seu Nome"

variables:
  var1: "valor1"
  var2: "valor2"

steps:
  - name: "Nome do Step"
    skill: "nome_da_skill"
    action: "nome_da_acao"
    params:
      param1: "{{ var1 }}"
      param2: "valor fixo"
    continue_on_error: false
    retry: 2
    retry_delay: 3
```

### Skills Disponíveis

#### 1. **filesystem**

**Ações**:
- `create_directory` - Cria diretório
  - Params: `path`
- `write_file` - Escreve arquivo
  - Params: `filepath`, `content`, `overwrite`
- `read_file` - Lê arquivo
  - Params: `filepath`

**Exemplo**:
```yaml
- name: "Criar arquivo"
  skill: "filesystem"
  action: "write_file"
  params:
    filepath: "output.txt"
    content: "Conteúdo do arquivo"
    overwrite: true
```

#### 2. **shell**

**Ações**:
- `execute` - Executa comando shell
  - Params: `command`, `timeout`

**Exemplo**:
```yaml
- name: "Listar arquivos"
  skill: "shell"
  action: "execute"
  params:
    command: "dir /s"
    timeout: 30
```

#### 3. **telegram**

**Ações**:
- `send_message` - Envia mensagem
  - Params: `message`, `chat_id`

**Exemplo**:
```yaml
- name: "Notificar"
  skill: "telegram"
  action: "send_message"
  params:
    message: "Workflow concluído!"
```

### Interpolação de Variáveis (Jinja2)

**Variáveis automáticas**:
- `{{ date }}` - Data atual (YYYYMMDD)
- `{{ datetime }}` - Data/hora (YYYYMMDD_HHMMSS)
- `{{ timestamp }}` - ISO timestamp
- `{{ workflow_name }}` - Nome do workflow

**Variáveis customizadas**:
```yaml
variables:
  nome: "João"
  
steps:
  - name: "Saudar"
    skill: "filesystem"
    action: "write_file"
    params:
      content: "Olá, {{ nome }}!"
```

**Resultados de steps anteriores**:
```yaml
steps:
  - name: "Step 1"
    # ...
  
  - name: "Step 2"
    params:
      content: "Resultado anterior: {{ step_0_result.stdout }}"
```

**Condicionais**:
```yaml
content: |
  {% if step_0_result.success %}
  Sucesso!
  {% else %}
  Erro!
  {% endif %}
```

### Opções Avançadas

**Retry Logic**:
```yaml
- name: "Comando com retry"
  skill: "shell"
  action: "execute"
  params:
    command: "git pull"
  retry: 3
  retry_delay: 5
```

**Continue on Error**:
```yaml
- name: "Step opcional"
  skill: "shell"
  action: "execute"
  params:
    command: "comando_que_pode_falhar"
  continue_on_error: true
```

---

## 📅 Agendamento de Workflows

### Windows Task Scheduler

```powershell
# Criar tarefa para executar diariamente às 9h
schtasks /create /tn "Backup Diário" /tr "python d:\projetos2025\cleudocode\workflow_manager.py run 'Backup Diário Automático'" /sc daily /st 09:00
```

### Cron (Linux/Mac)

```bash
# Adicionar ao crontab
0 9 * * * cd /path/to/cleudocode && python workflow_manager.py run "Backup Diário Automático"
```

---

## 🎯 Casos de Uso

### Rotina Matinal (9h)
1. **Relatório de Atividades Diário** - Ver o que aconteceu ontem
2. **Monitoramento de Saúde** - Verificar status do sistema
3. **Sincronização com Git** - Puxar últimas alterações

### Rotina Noturna (21h)
1. **Backup Diário Automático** - Backup completo
2. **Limpeza de Arquivos Temporários** - Liberar espaço
3. **Atualização de Dependências** - Verificar updates

### Semanal (Domingo 10h)
1. **Limpeza Profunda** - Limpar tudo
2. **Backup Completo** - Backup semanal
3. **Relatório Semanal** - Consolidar semana

---

## 🐛 Troubleshooting

### Workflow não encontrado
```bash
# Listar workflows disponíveis
python workflow_manager.py list
```

### Erro de permissão
```bash
# Executar como administrador (Windows)
# Ou verificar permissões de arquivo
```

### Skill não encontrada
```bash
# Verificar se a skill está registrada
# Ver logs em logs/cleudocode.log
```

---

## 📚 Recursos Adicionais

- **Documentação Completa**: Ver `implementation_examples.md`
- **Testes**: `test_lobster_simple.py`
- **Exemplos**: `skills/workflows/*.lobster`

---

## 🎉 Contribuindo

Para adicionar novos workflows:

1. Crie um arquivo `.lobster` em `skills/workflows/`
2. Siga a estrutura YAML padrão
3. Teste com `python workflow_manager.py run "Seu Workflow"`
4. Documente no README

---

**Última atualização**: 2026-01-27  
**Versão**: 1.0.0  
**Autor**: Cleudocode Team
