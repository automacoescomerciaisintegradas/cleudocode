name: "Antigravity Sync"
description: "Sincroniza dados entre Cleudocode e Antigravity"
version: "1.0"
author: "Cleudocode Team"

variables:
  antigravity_api: "http://localhost:8080/api"
  local_data_path: "./data/antigravity"
  backup_path: "./backups/sync_{{ date }}"
  sync_log: "logs/antigravity_sync_{{ datetime }}.log"

steps:
  - name: "Criar diretórios necessários"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "{{ local_data_path }}"

  - name: "Criar diretório de backup"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "{{ backup_path }}"

  - name: "Criar diretório de logs"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "logs"

  - name: "Inicializar log de sincronização"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "{{ sync_log }}"
      content: |
        # Log de Sincronização Antigravity
        Início: {{ datetime }}
        
        ## Preparação
        ✅ Diretórios criados
        ✅ Log inicializado
        
      overwrite: true

  - name: "Fazer backup dos dados locais"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if (Test-Path '{{ local_data_path }}') { Copy-Item -Path '{{ local_data_path }}\\*' -Destination '{{ backup_path }}' -Recurse -Force -ErrorAction SilentlyContinue } else { echo 'Nenhum dado local para backup' }\""
      timeout: 60

  - name: "Verificar conectividade com Antigravity API"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -f http://localhost:18900/health"
      timeout: 30
    retry: 3
    retry_delay: 5

  - name: "Obter dados remotos do Antigravity"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -f http://localhost:18900/api/data/export -o \"{{ local_data_path }}/remote_data.json\""
      timeout: 120
    continue_on_error: true

  - name: "Comparar dados locais vs remotos"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if ((Test-Path '{{ local_data_path }}/local_data.json') -and (Test-Path '{{ local_data_path }}/remote_data.json')) { Compare-Object (Get-Content '{{ local_data_path }}/local_data.json') (Get-Content '{{ local_data_path }}/remote_data.json') | Out-File '{{ local_data_path }}/diff.txt' } else { echo 'Primeira sincronização' }\""
      timeout: 30
    continue_on_error: true

  - name: "Sincronizar dados (upload local para remoto)"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if (Test-Path '{{ local_data_path }}/local_data.json') { Invoke-RestMethod -Uri 'http://localhost:18900/api/data/import' -Method Post -InFile '{{ local_data_path }}/local_data.json' -ContentType 'application/json' } else { echo 'Nenhum dado local' }\""
      timeout: 120
    continue_on_error: true

  - name: "Atualizar dados locais com remotos"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if (Test-Path '{{ local_data_path }}/remote_data.json') { Copy-Item '{{ local_data_path }}/remote_data.json' '{{ local_data_path }}/local_data.json' -Force }\""
      timeout: 30

  - name: "Verificar integridade dos dados"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if (Test-Path '{{ local_data_path }}/local_data.json') { try { Get-Content '{{ local_data_path }}/local_data.json' | ConvertFrom-Json | Out-Null; echo 'Dados íntegros' } catch { exit 1 } }\""
      timeout: 30
    continue_on_error: true

  - name: "Atualizar log com resultados"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "{{ sync_log }}"
      content: |
        # Log de Sincronização Antigravity
        Início: {{ datetime }}
        
        ## Preparação
        ✅ Diretórios criados
        ✅ Log inicializado
        ✅ Backup criado: {{ backup_path }}
        
        ## Conectividade
        API Status: {% if step_1_result.success %}✅ Online{% else %}❌ Offline{% endif %}
        
        ## Sincronização
        Dados remotos: {% if step_2_result.success %}✅ Obtidos{% else %}❌ Falha{% endif %}
        Comparação: {% if step_3_result.success %}✅ Realizada{% else %}⚠️ Primeira sync{% endif %}
        Upload local: {% if step_4_result.success %}✅ Sucesso{% else %}⚠️ Sem dados ou falha{% endif %}
        Download remoto: {% if step_5_result.success %}✅ Sucesso{% else %}❌ Falha{% endif %}
        Integridade: {% if step_6_result.success %}✅ Verificada{% else %}⚠️ Problemas{% endif %}
        
        ## Resumo
        {% if step_1_result.success %}✅ Conectado{% else %}❌ Falha de Conexão{% endif %}
        
        Fim: {{ datetime }}
        
        ---
        Gerado pelo Cleudocode Workflow Engine
      overwrite: true

  - name: "Notificar resultado da sincronização"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        🔄 *Antigravity Sync Completo*
        
        📊 *Status:* {{ '✅ Sucesso' if step_1_result.success else '⚠️ Com problemas' }}
        
        🔗 *Conectividade:* {{ '✅ API Online' if step_1_result.success else '❌ API Offline' }}
        
        📁 *Operações:*
        • Backup: ✅ Criado em `{{ backup_path }}`
        • Download: {{ '✅ Sucesso' if step_2_result.success else '❌ Falha' }}
        • Upload: {{ '✅ Sucesso' if step_4_result.success else '⚠️ Sem dados' }}
        • Integridade: {{ '✅ OK' if step_6_result.success else '⚠️ Verificar' }}
        
        📄 *Log completo:* `{{ sync_log }}`
    continue_on_error: true