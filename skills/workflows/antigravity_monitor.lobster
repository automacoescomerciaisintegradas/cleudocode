name: "Antigravity Monitor"
description: "Monitoramento contínuo do sistema Antigravity"
version: "1.0"
author: "Cleudocode Team"

variables:
  service_name: "antigravity"
  health_check_url: "http://localhost:8080/health"
  api_endpoint: "http://localhost:8080/api"
  log_file: "/var/log/antigravity/application.log"
  error_log: "/var/log/antigravity/error.log"
  monitor_log: "logs/antigravity_monitor_{{ date }}.log"
  alert_threshold_cpu: 80
  alert_threshold_memory: 85
  alert_threshold_disk: 90
  alert_threshold_errors: 10

steps:
  - name: "Criar diretório de logs de monitoramento"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "logs"

  - name: "Inicializar log de monitoramento"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "{{ monitor_log }}"
      content: |
        # Log de Monitoramento Antigravity
        Início: {{ datetime }}
        
        ## Configuração
        Serviço: {{ service_name }}
        Health Check: {{ health_check_url }}
        API: {{ api_endpoint }}
        
        ## Thresholds de Alerta
        CPU: {{ alert_threshold_cpu }}%
        Memória: {{ alert_threshold_memory }}%
        Disco: {{ alert_threshold_disk }}%
        Erros: {{ alert_threshold_errors }} por hora
        
        ## Verificações
        
      overwrite: true

  - name: "Verificar status do serviço"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if (Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*app.py*' }) { echo 'ACTIVE' } else { echo 'INACTIVE' }\""
      timeout: 10
    continue_on_error: true

  - name: "Verificar health check da API"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -o NUL -w \"%{http_code}\" http://localhost:18900/health"
      timeout: 15
    continue_on_error: true

  - name: "Verificar tempo de resposta da API"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"$start = Get-Date; try { $res = Invoke-WebRequest -Uri http://localhost:18900/health -UseBasicParsing; (New-TimeSpan -Start $start -End (Get-Date)).TotalSeconds } catch { 0 }\""
      timeout: 20
    continue_on_error: true

  - name: "Coletar uso de CPU do processo"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"$p = Get-Process python | Where-Object { $_.Path -like '*app.py*' } | Select-Object -First 1; if ($p) { [math]::Round((Get-CimInstance Win32_Processor).LoadPercentage, 1) } else { echo 0 }\""
      timeout: 10
    continue_on_error: true

  - name: "Coletar uso de memória do processo"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"$p = Get-Process python | Where-Object { $_.Path -like '*app.py*' } | Select-Object -First 1; if ($p) { [math]::Round($p.WorkingSet64 / 1MB, 1) } else { echo 0 }\""
      timeout: 10
    continue_on_error: true

  - name: "Verificar uso de disco"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"$d = Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=''C:'''; [math]::Round(($d.Size - $d.FreeSpace) / $d.Size * 100, 1)\""
      timeout: 10
    continue_on_error: true

  - name: "Contar erros recentes nos logs"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if (Test-Path 'web_server.err') { (Get-Content 'web_server.err' -Tail 1000 | Select-String 'ERROR' -AllMatches).Count } else { echo 0 }\""
      timeout: 15
    continue_on_error: true

  - name: "Verificar conectividade de rede"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if (Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet) { echo 'OK' } else { echo 'FAIL' }\""
      timeout: 20
    continue_on_error: true

  - name: "Verificar portas em uso"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"(Get-NetTCPConnection -LocalPort 18900 -ErrorAction SilentlyContinue).Count\""
      timeout: 10
    continue_on_error: true

  - name: "Coletar últimas linhas do log de aplicação"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if (Test-Path 'web_server.log') { Get-Content 'web_server.log' -Tail 5 } else { echo 'Log não encontrado' }\""
      timeout: 10
    continue_on_error: true

  - name: "Verificar espaço em disco geral"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"$d = Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=''C:'''; [math]::Round(($d.Size - $d.FreeSpace) / $d.Size * 100, 1)\""
      timeout: 10
    continue_on_error: true

  - name: "Atualizar log de monitoramento"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "{{ monitor_log }}"
      content: |
        # Log de Monitoramento Antigravity - {{ datetime }}
        
        ### Status do Serviço
        Serviço ativo: {{ step_2_result.stdout|trim }}
        Health check: {{ step_3_result.stdout|trim }}
        Tempo resposta: {{ step_4_result.stdout|trim }}s
        
        ### Recursos do Sistema
        Processo CPU: {{ step_5_result.stdout|trim }}%
        Processo RAM: {{ step_6_result.stdout|trim }}MB
        Disco C: (Aplicação): {{ step_7_result.stdout|trim }}%
        
        ### Logs e Conectividade
        Erros recentes: {{ step_8_result.stdout|trim }}
        Conectividade: {{ step_9_result.stdout|trim }}
        Portas ativas (18900): {{ step_10_result.stdout|trim }}
        
        ---
      overwrite: true

  - name: "Enviar notificação (normal ou alerta)"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        {% set cpu = step_5_result.stdout|trim|float %}
        {% set ram = step_6_result.stdout|trim|float %}
        {% set errors = step_8_result.stdout|trim|int %}
        {% set status = step_2_result.stdout|trim %}
        
        {% if cpu > alert_threshold_cpu or errors > alert_threshold_errors or status != 'ACTIVE' %}🚨 *ALERTA - Antigravity Monitor*{% else %}📊 *Antigravity Monitor - OK*{% endif %}
        
        🕐 *Verificação:* {{ datetime }}
        
        🔧 *Serviço:* {{ '✅ ACTIVE' if status == 'ACTIVE' else '❌ INACTIVE' }}
        🌐 *API:* {{ '✅ OK' if step_3_result.stdout|trim == '200' else '❌ Falha' }}
        ⚡ *Resposta:* {{ step_4_result.stdout|trim }}s
        
        💻 *Recursos:*
        • CPU: {{ cpu }}% {{ '🚨' if cpu > alert_threshold_cpu }}
        • RAM: {{ ram }}MB
        • Disco: {{ step_7_result.stdout|trim }}%
        
        📋 *Status:*
        • Erros: {{ errors }} {{ '🚨' if errors > alert_threshold_errors }}
        • Rede: {{ '✅' if step_9_result.stdout|trim == 'OK' else '❌' }}
        
        📄 *Log:* `{{ monitor_log }}`
    continue_on_error: true