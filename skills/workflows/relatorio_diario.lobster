name: "Relatório de Atividades Diário"
description: "Gera relatório consolidado das atividades do dia"
version: "1.0"
author: "Cleudocode Team"

variables:
  report_date: "{{ date }}"

steps:
  - name: "Coletar logs do sistema"
    skill: "shell"
    action: "execute"
    params:
      command: "type logs\\cleudocode.log | find \"{{ date }}\""
    continue_on_error: true
    
  - name: "Contar mensagens processadas"
    skill: "shell"
    action: "execute"
    params:
      command: "type logs\\audit.jsonl | find \"{{ date }}\" /c"
    continue_on_error: true
    
  - name: "Verificar erros do dia"
    skill: "shell"
    action: "execute"
    params:
      command: "type logs\\cleudocode.log | find \"{{ date }}\" | find \"ERROR\" /c"
    continue_on_error: true
    
  - name: "Listar workflows executados"
    skill: "shell"
    action: "execute"
    params:
      command: "type logs\\cleudocode.log | find \"Executando workflow\""
    continue_on_error: true
    
  - name: "Gerar relatório em Markdown"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "reports/diario_{{ date }}.md"
      content: |
        # Relatório Diário - {{ date }}
        
        ## 📊 Resumo Executivo
        
        - **Data**: {{ datetime }}
        - **Mensagens Processadas**: {{ step_1_result.stdout }}
        - **Erros Registrados**: {{ step_2_result.stdout }}
        - **Status Geral**: {% if step_2_result.stdout == "0" %}✅ Operação Normal{% else %}⚠️ Atenção Necessária{% endif %}
        
        ## 🔄 Workflows Executados
        
        ```
        {{ step_3_result.stdout }}
        ```
        
        ## 📝 Logs do Sistema
        
        ```
        {{ step_0_result.stdout }}
        ```
        
        ## 📈 Estatísticas
        
        | Métrica | Valor |
        |---------|-------|
        | Mensagens | {{ step_1_result.stdout }} |
        | Erros | {{ step_2_result.stdout }} |
        | Workflows | Vários |
        
        ## 🎯 Próximas Ações
        
        {% if step_2_result.stdout != "0" %}
        - [ ] Investigar erros registrados
        - [ ] Verificar logs detalhados
        - [ ] Aplicar correções necessárias
        {% else %}
        - [x] Sistema operando normalmente
        - [ ] Continuar monitoramento
        {% endif %}
        
        ---
        
        *Relatório gerado automaticamente pelo Lobster Workflow Engine*
      overwrite: true
    
  - name: "Criar versão em texto"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "reports/diario_{{ date }}.txt"
      content: |
        ===================================
        RELATÓRIO DIÁRIO - {{ date }}
        ===================================
        
        Data/Hora: {{ datetime }}
        
        RESUMO:
        - Mensagens: {{ step_1_result.stdout }}
        - Erros: {{ step_2_result.stdout }}
        
        WORKFLOWS EXECUTADOS:
        {{ step_3_result.stdout }}
        
        ===================================
      overwrite: true
    
  - name: "Enviar relatório por Telegram"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        📊 Relatório Diário - {{ date }}
        
        📈 Mensagens: {{ step_1_result.stdout }}
        {% if step_2_result.stdout == "0" %}✅ Sem erros{% else %}⚠️ Erros: {{ step_2_result.stdout }}{% endif %}
        
        📄 Relatórios salvos:
        - reports/diario_{{ date }}.md
        - reports/diario_{{ date }}.txt
        
        {% if step_2_result.stdout != "0" %}⚠️ Atenção: Erros detectados! Verifique os logs.{% endif %}
