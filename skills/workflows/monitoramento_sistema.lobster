name: "Monitoramento de Saúde do Sistema"
description: "Verifica saúde do sistema e alerta sobre problemas"
version: "1.0"
author: "Cleudocode Team"

steps:
  - name: "Verificar uso de disco"
    skill: "shell"
    action: "execute"
    params:
      command: "wmic logicaldisk get caption,freespace,size /format:list"
    continue_on_error: true
    
  - name: "Verificar uso de memória"
    skill: "shell"
    action: "execute"
    params:
      command: "wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /format:list"
    continue_on_error: true
    
  - name: "Verificar processos Python"
    skill: "shell"
    action: "execute"
    params:
      command: "tasklist | find \"python\""
    continue_on_error: true
    
  - name: "Verificar logs de erro recentes"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell \"Get-Content logs\\cleudocode.log -Tail 100 | Select-String 'ERROR'\""
    continue_on_error: true
    
  - name: "Verificar conectividade"
    skill: "shell"
    action: "execute"
    params:
      command: "ping -n 1 8.8.8.8"
    continue_on_error: true
    
  - name: "Gerar relatório de saúde"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "reports/health_{{ datetime }}.txt"
      content: |
        ===================================
        RELATÓRIO DE SAÚDE DO SISTEMA
        ===================================
        
        Data/Hora: {{ datetime }}
        Timestamp: {{ timestamp }}
        
        DISCO:
        {{ step_0_result.stdout }}
        
        MEMÓRIA:
        {{ step_1_result.stdout }}
        
        PROCESSOS PYTHON:
        {{ step_2_result.stdout }}
        
        ERROS RECENTES:
        {{ step_3_result.stdout }}
        
        CONECTIVIDADE:
        {{ step_4_result.stdout }}
        
        ===================================
        STATUS: {% if step_3_result.stdout %}⚠️ ATENÇÃO{% else %}✅ NORMAL{% endif %}
        ===================================
      overwrite: true
    
  - name: "Alertar se houver problemas"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        {% if step_3_result.stdout %}
        ⚠️ ALERTA DE SISTEMA!
        
        🔴 Erros detectados no sistema
        📅 Data: {{ datetime }}
        
        Verifique o relatório:
        reports/health_{{ datetime }}.txt
        
        Ação recomendada:
        - Verificar logs detalhados
        - Investigar erros
        - Aplicar correções
        {% else %}
        ✅ Sistema Saudável
        
        📅 Data: {{ datetime }}
        💚 Todos os sistemas operando normalmente
        
        Relatório salvo em:
        reports/health_{{ datetime }}.txt
        {% endif %}
