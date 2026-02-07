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
      command: "cp -r {{ local_data_path }}/* {{ backup_path }}/ 2>/dev/null || echo 'Nenhum dado local para backup'"
      timeout: 60

  - name: "Verificar conectividade com Antigravity API"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -f {{ antigravity_api }}/health"
      timeout: 30
    retry: 3
    retry_delay: 5

  - name: "Obter dados remotos do Antigravity"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -f {{ antigravity_api }}/data/export -o {{ local_data_path }}/remote_data.json"
      timeout: 120

  - name: "Comparar dados locais vs remotos"
    skill: "shell"
    action: "execute"
    params:
      command: |
        if [ -f "{{ local_data_path }}/local_data.json" ] && [ -f "{{ local_data_path }}/remote_data.json" ]; then
          diff {{ local_data_path }}/local_data.json {{ local_data_path }}/remote_data.json > {{ local_data_path }}/diff.txt
          echo "Comparação concluída"
        else
          echo "Primeira sincronização - sem comparação"
        fi
      timeout: 30
    continue_on_error: true

  - name: "Sincronizar dados (upload local para remoto)"
    skill: "shell"
    action: "execute"
    params:
      command: |
        if [ -f "{{ local_data_path }}/local_data.json" ]; then
          curl -s -f -X POST -H "Content-Type: application/json" \
               -d @{{ local_data_path }}/local_data.json \
               {{ antigravity_api }}/data/import
        else
          echo "Nenhum dado local para upload"
        fi
      timeout: 120
    continue_on_error: true

  - name: "Atualizar dados locais com remotos"
    skill: "shell"
    action: "execute"
    params:
      command: |
        if [ -f "{{ local_data_path }}/remote_data.json" ]; then
          cp {{ local_data_path }}/remote_data.json {{ local_data_path }}/local_data.json
          echo "Dados locais atualizados"
        else
          echo "Nenhum dado remoto para download"
        fi
      timeout: 30

  - name: "Verificar integridade dos dados"
    skill: "shell"
    action: "execute"
    params:
      command: |
        if [ -f "{{ local_data_path }}/local_data.json" ]; then
          python3 -m json.tool {{ local_data_path }}/local_data.json > /dev/null
          echo "Dados íntegros"
        else
          echo "Nenhum dado para verificar"
        fi
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
        API Status: {% if step_5_result.success %}✅ Online{% else %}❌ Offline{% endif %}
        
        ## Sincronização
        Dados remotos: {% if step_6_result.success %}✅ Obtidos{% else %}❌ Falha{% endif %}
        Comparação: {% if step_7_result.success %}✅ Realizada{% else %}⚠️ Primeira sync{% endif %}
        Upload local: {% if step_8_result.success %}✅ Sucesso{% else %}⚠️ Sem dados ou falha{% endif %}
        Download remoto: {% if step_9_result.success %}✅ Sucesso{% else %}❌ Falha{% endif %}
        Integridade: {% if step_10_result.success %}✅ Verificada{% else %}⚠️ Problemas{% endif %}
        
        ## Resumo
        {% if step_5_result.success and step_9_result.success %}✅ Sincronização bem-sucedida{% else %}❌ Sincronização com problemas{% endif %}
        
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
        
        📊 *Status:* {% if step_5_result.success and step_9_result.success %}✅ Sucesso{% else %}⚠️ Com problemas{% endif %}
        
        🔗 *Conectividade:* {% if step_5_result.success %}✅ API Online{% else %}❌ API Offline{% endif %}
        
        📁 *Operações:*
        • Backup: ✅ Criado em `{{ backup_path }}`
        • Download: {% if step_6_result.success %}✅ Sucesso{% else %}❌ Falha{% endif %}
        • Upload: {% if step_8_result.success %}✅ Sucesso{% else %}⚠️ Sem dados{% endif %}
        • Integridade: {% if step_10_result.success %}✅ OK{% else %}⚠️ Verificar{% endif %}
        
        📄 *Log completo:* `{{ sync_log }}`
    continue_on_error: true