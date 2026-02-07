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
      command: "ps aux | grep antigravity | grep -v grep"
      timeout: 10
    continue_on_error: true

  - name: "Verificar conectividade com Antigravity"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/health || echo 'OFFLINE'"
      timeout: 15
    continue_on_error: true

  - name: "Coletar uso de CPU"
    skill: "shell"
    action: "execute"
    params:
      command: "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
      timeout: 10
    continue_on_error: true

  - name: "Coletar uso de memória"
    skill: "shell"
    action: "execute"
    params:
      command: "free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'"
      timeout: 10
    continue_on_error: true

  - name: "Verificar espaço em disco"
    skill: "shell"
    action: "execute"
    params:
      command: "df -h {{ antigravity_path }} | tail -1 | awk '{print $5}' | cut -d'%' -f1"
      timeout: 10
    continue_on_error: true

  - name: "Verificar logs de erro recentes"
    skill: "shell"
    action: "execute"
    params:
      command: "tail -100 /var/log/antigravity/error.log | grep -c ERROR || echo '0'"
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
        Processo Antigravity: Verificando...
        Conectividade: Verificando...
        
        ## Recursos do Sistema
        CPU: Coletando dados...
        Memória: Coletando dados...
        Disco: Coletando dados...
        
        ## Logs
        Erros recentes: Verificando logs...
        
        ## Alertas
        Sistema em monitoramento...
        
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