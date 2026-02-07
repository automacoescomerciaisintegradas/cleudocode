name: "Antigravity Health Hub"
description: "Valida a saúde de todos os componentes do ecossistema Antigravity local"
version: "1.1"
author: "Cleudocode Team"

variables:
  gateway_url: "http://localhost:18900/health"
  relay_url: "http://localhost:18902"
  report_file: "reports/antigravity_health_report.txt"

steps:
  - name: "Validar Status do Gateway Antigravity"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s {{ gateway_url }} || echo 'GATEWAY_DOWN'"
      timeout: 10
    continue_on_error: true

  - name: "Verificar Processos Ativos"
    skill: "shell"
    action: "execute"
    params:
      command: "ps aux | grep -E 'antigravity_gateway|web_server' | grep -v grep"
      timeout: 5
    continue_on_error: true

  - name: "Testar Inferência Local (Gateway Hub)"
    skill: "shell"
    action: "execute"
    params:
      command: "python3 test_gateway_connection.py"
      timeout: 30
    continue_on_error: true

  - name: "Gerar Sumário Executivo"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "{{ report_file }}"
      content: |
        # 🌌 Antigravity Health Report
        Status report generated on: {{ datetime }}

        ## 🚦 Component Status
        - Gateway API: {{ step_0_result.stdout }}
        - Processes: 
        {{ step_1_result.stdout }}

        ## 🧠 AI Inference Test
        {{ step_2_result.stdout }}

        ---
        Validated by Orquestrador Pro Max
      overwrite: true

  - name: "Notificar via Log"
    skill: "shell"
    action: "execute"
    params:
      command: "echo '✅ Saúde do sistema validada. Veja {{ report_file }}'"
