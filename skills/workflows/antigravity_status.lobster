name: "Antigravity Status Check"
description: "Verifica o status e saúde do sistema Antigravity"
version: "1.0"
author: "Cleudocode Team"

variables:
  antigravity_path: "/opt/antigravity"
  antigravity_config: "/etc/antigravity/config.yaml"
  report_file: "reports/antigravity_status.txt"
  alert_threshold_cpu: 80
  alert_threshold_memory: 85

steps:
  - name: "Verificar se Antigravity está rodando"
    skill: "shell"
    action: "execute"
    params:
      command: "tasklist /FI \"IMAGENAME eq python.exe\" /NH"
      timeout: 10
    continue_on_error: true

  - name: "Verificar conectividade com Antigravity"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -o NUL -w \"%{http_code}\" http://localhost:18900/health || echo OFFLINE"
      timeout: 15
    continue_on_error: true

  - name: "Coletar uso de CPU"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"(Get-CimInstance Win32_Processor).LoadPercentage\""
      timeout: 10
    continue_on_error: true

  - name: "Coletar uso de memória"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"$m = Get-CimInstance Win32_OperatingSystem; [math]::Round(($m.TotalVisibleMemorySize - $m.FreePhysicalMemory) / $m.TotalVisibleMemorySize * 100, 1)\""
      timeout: 10
    continue_on_error: true

  - name: "Verificar espaço em disco"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"$d = Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=''C:'''; [math]::Round(($d.Size - $d.FreeSpace) / $d.Size * 100, 1)\""
      timeout: 10
    continue_on_error: true

  - name: "Verificar logs de erro recentes"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if (Test-Path 'web_server.err') { (Get-Content 'web_server.err' -Tail 100 | Select-String 'ERROR' -AllMatches).Count } else { echo 0 }\""
      timeout: 10
    continue_on_error: true

  - name: "Criar diretório de relatórios"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "reports"

  - name: "Gerar relatório de status"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "reports/antigravity_status.txt"
      content: |
        # Relatório de Status - Antigravity
        Data/Hora: {{ datetime }}
        
        ## Status do Sistema
        Processo: {% if step_0_result.success %}Ativo{% else %}Inativo/Não encontrado{% endif %}
        Conectividade: {% if step_1_result.stdout|trim == '200' %}OK (HTTP 200){% else %}Falha ({{ step_1_result.stdout|trim }}){% endif %}
        
        ## Recursos do Sistema
        CPU: {{ step_2_result.stdout|trim }}%
        Memória: {{ step_3_result.stdout|trim }}%
        Disco: {{ step_4_result.stdout|trim }}%
        
        ## Logs
        Erros recentes (últimas 100 linhas): {{ step_5_result.stdout|trim }}
        
        ---
        Relatório gerado pelo Cleudocode Workflow Engine
      overwrite: true

  - name: "Notificar status via Telegram"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        🔍 *Antigravity Status Check*
        
        📊 *Sistema:* {% if step_0_result.success %}✅ Online{% else %}❌ Offline{% endif %}
        🌐 *API:* {% if step_1_result.stdout == '200' %}✅ Respondendo{% else %}❌ Indisponível{% endif %}
        
        💻 *Recursos:*
        • CPU: {{ step_2_result.stdout }}%
        • RAM: {{ step_3_result.stdout }}%
        • Disco: {{ step_4_result.stdout }}%
        
        {% if step_5_result.stdout|int > 5 %}⚠️ *Atenção:* {{ step_5_result.stdout }} erros nos logs{% endif %}
        
        📄 Relatório completo: `{{ report_file }}`
    continue_on_error: true