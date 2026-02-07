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
        
      overwrite: false

  - name: "Verificar status do serviço"
    skill: "shell"
    action: "execute"
    params:
      command: "systemctl is-active {{ service_name }}"
      timeout: 10
    continue_on_error: true

  - name: "Verificar health check da API"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -o /dev/null -w '%{http_code}' {{ health_check_url }}"
      timeout: 15
    continue_on_error: true

  - name: "Verificar tempo de resposta da API"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -o /dev/null -w '%{time_total}' {{ api_endpoint }}/status"
      timeout: 20
    continue_on_error: true

  - name: "Coletar uso de CPU do processo"
    skill: "shell"
    action: "execute"
    params:
      command: "ps aux | grep {{ service_name }} | grep -v grep | awk '{sum+=$3} END {print sum}' || echo '0'"
      timeout: 10
    continue_on_error: true

  - name: "Coletar uso de memória do processo"
    skill: "shell"
    action: "execute"
    params:
      command: "ps aux | grep {{ service_name }} | grep -v grep | awk '{sum+=$4} END {print sum}' || echo '0'"
      timeout: 10
    continue_on_error: true

  - name: "Verificar uso de disco"
    skill: "shell"
    action: "execute"
    params:
      command: "df -h /opt/antigravity | tail -1 | awk '{print $5}' | cut -d'%' -f1"
      timeout: 10
    continue_on_error: true

  - name: "Contar erros recentes nos logs"
    skill: "shell"
    action: "execute"
    params:
      command: "tail -1000 {{ error_log }} 2>/dev/null | grep -c \"$(date '+%Y-%m-%d %H')\" || echo '0'"
      timeout: 15
    continue_on_error: true

  - name: "Verificar conectividade de rede"
    skill: "shell"
    action: "execute"
    params:
      command: "ping -c 3 8.8.8.8 > /dev/null && echo 'OK' || echo 'FAIL'"
      timeout: 20
    continue_on_error: true

  - name: "Verificar portas em uso"
    skill: "shell"
    action: "execute"
    params:
      command: "netstat -tlnp | grep {{ service_name }} | wc -l"
      timeout: 10
    continue_on_error: true

  - name: "Coletar últimas linhas do log de aplicação"
    skill: "shell"
    action: "execute"
    params:
      command: "tail -5 {{ log_file }} 2>/dev/null || echo 'Log não encontrado'"
      timeout: 10
    continue_on_error: true

  - name: "Verificar espaço em disco geral"
    skill: "shell"
    action: "execute"
    params:
      command: "df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1"
      timeout: 10
    continue_on_error: true

  - name: "Atualizar log de monitoramento"
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
        
        ## Verificações - {{ datetime }}
        
        ### Status do Serviço
        Serviço ativo: {% if step_2_result.success %}✅ {{ step_2_result.stdout }}{% else %}❌ INATIVO{% endif %}
        Health check: {% if step_3_result.stdout == '200' %}✅ OK (200){% else %}❌ FALHA ({{ step_3_result.stdout }}){% endif %}
        Tempo resposta: {{ step_4_result.stdout }}s
        
        ### Recursos do Sistema
        CPU processo: {{ step_5_result.stdout }}%
        Memória processo: {{ step_6_result.stdout }}%
        Disco aplicação: {{ step_7_result.stdout }}%
        Disco sistema: {{ step_12_result.stdout }}%
        
        ### Logs e Conectividade
        Erros última hora: {{ step_8_result.stdout }}
        Conectividade: {% if step_9_result.stdout == 'OK' %}✅ OK{% else %}❌ FALHA{% endif %}
        Portas ativas: {{ step_10_result.stdout }}
        
        ### Alertas Detectados
        {% if step_5_result.stdout|float > alert_threshold_cpu %}🚨 ALERTA: CPU alta ({{ step_5_result.stdout }}%){% endif %}
        {% if step_6_result.stdout|float > alert_threshold_memory %}🚨 ALERTA: Memória alta ({{ step_6_result.stdout }}%){% endif %}
        {% if step_7_result.stdout|int > alert_threshold_disk %}🚨 ALERTA: Disco aplicação cheio ({{ step_7_result.stdout }}%){% endif %}
        {% if step_12_result.stdout|int > alert_threshold_disk %}🚨 ALERTA: Disco sistema cheio ({{ step_12_result.stdout }}%){% endif %}
        {% if step_8_result.stdout|int > alert_threshold_errors %}🚨 ALERTA: Muitos erros ({{ step_8_result.stdout }}){% endif %}
        {% if step_3_result.stdout != '200' %}🚨 ALERTA: API não responde{% endif %}
        {% if step_2_result.success == false %}🚨 ALERTA: Serviço inativo{% endif %}
        
        ### Últimas Linhas do Log
        ```
        {{ step_11_result.stdout }}
        ```
        
        ---
        Monitoramento executado pelo Cleudocode Workflow Engine
      overwrite: false

  - name: "Determinar se alertas são necessários"
    skill: "shell"
    action: "execute"
    params:
      command: |
        ALERTS=0
        
        # Verificar CPU
        if [ "{{ step_5_result.stdout }}" != "" ] && [ "$(echo '{{ step_5_result.stdout }} > {{ alert_threshold_cpu }}' | bc -l 2>/dev/null || echo 0)" = "1" ]; then
          ALERTS=$((ALERTS + 1))
        fi
        
        # Verificar Memória
        if [ "{{ step_6_result.stdout }}" != "" ] && [ "$(echo '{{ step_6_result.stdout }} > {{ alert_threshold_memory }}' | bc -l 2>/dev/null || echo 0)" = "1" ]; then
          ALERTS=$((ALERTS + 1))
        fi
        
        # Verificar Disco
        if [ "{{ step_7_result.stdout }}" != "" ] && [ "{{ step_7_result.stdout }}" -gt "{{ alert_threshold_disk }}" ] 2>/dev/null; then
          ALERTS=$((ALERTS + 1))
        fi
        
        # Verificar Erros
        if [ "{{ step_8_result.stdout }}" != "" ] && [ "{{ step_8_result.stdout }}" -gt "{{ alert_threshold_errors }}" ] 2>/dev/null; then
          ALERTS=$((ALERTS + 1))
        fi
        
        # Verificar API
        if [ "{{ step_3_result.stdout }}" != "200" ]; then
          ALERTS=$((ALERTS + 1))
        fi
        
        # Verificar Serviço
        if [ "{{ step_2_result.success }}" != "true" ]; then
          ALERTS=$((ALERTS + 1))
        fi
        
        echo $ALERTS
      timeout: 10

  - name: "Enviar notificação (normal ou alerta)"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        {% if step_14_result.stdout|int > 0 %}🚨 *ALERTA - Antigravity Monitor*{% else %}📊 *Antigravity Monitor - OK*{% endif %}
        
        🕐 *Verificação:* {{ datetime }}
        
        🔧 *Serviço:* {% if step_2_result.success %}✅ Ativo{% else %}❌ Inativo{% endif %}
        🌐 *API:* {% if step_3_result.stdout == '200' %}✅ OK{% else %}❌ Falha ({{ step_3_result.stdout }}){% endif %}
        ⚡ *Resposta:* {{ step_4_result.stdout }}s
        
        💻 *Recursos:*
        • CPU: {{ step_5_result.stdout }}%{% if step_5_result.stdout|float > alert_threshold_cpu %} 🚨{% endif %}
        • RAM: {{ step_6_result.stdout }}%{% if step_6_result.stdout|float > alert_threshold_memory %} 🚨{% endif %}
        • Disco: {{ step_7_result.stdout }}%{% if step_7_result.stdout|int > alert_threshold_disk %} 🚨{% endif %}
        
        📋 *Status:*
        • Erros/hora: {{ step_8_result.stdout }}{% if step_8_result.stdout|int > alert_threshold_errors %} 🚨{% endif %}
        • Rede: {% if step_9_result.stdout == 'OK' %}✅{% else %}❌{% endif %}
        • Portas: {{ step_10_result.stdout }}
        
        {% if step_14_result.stdout|int > 0 %}⚠️ *{{ step_14_result.stdout }} alerta(s) detectado(s)*{% endif %}
        
        📄 *Log:* `{{ monitor_log }}`
    continue_on_error: true