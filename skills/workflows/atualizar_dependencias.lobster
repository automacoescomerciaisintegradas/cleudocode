name: "Atualização de Dependências"
description: "Verifica e atualiza dependências do projeto"
version: "1.0"
author: "Cleudocode Team"

steps:
  - name: "Listar dependências atuais"
    skill: "shell"
    action: "execute"
    params:
      command: "pip list --format=freeze"
    continue_on_error: true
    
  - name: "Verificar dependências desatualizadas"
    skill: "shell"
    action: "execute"
    params:
      command: "pip list --outdated"
    continue_on_error: true
    
  - name: "Criar backup do requirements"
    skill: "shell"
    action: "execute"
    params:
      command: "copy requirements.txt requirements.txt.backup_{{ date }}"
    continue_on_error: true
    
  - name: "Gerar novo requirements"
    skill: "shell"
    action: "execute"
    params:
      command: "pip freeze > requirements_new.txt"
    continue_on_error: false
    
  - name: "Criar relatório de atualizações"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "reports/atualizacoes_{{ date }}.md"
      content: |
        # Relatório de Atualizações - {{ date }}
        
        ## 📦 Dependências Atuais
        
        ```
        {{ step_0_result.stdout }}
        ```
        
        ## 🔄 Dependências Desatualizadas
        
        ```
        {{ step_1_result.stdout }}
        ```
        
        ## ✅ Ações Realizadas
        
        - [x] Backup criado: `requirements.txt.backup_{{ date }}`
        - [x] Novo requirements gerado: `requirements_new.txt`
        - [x] Relatório criado
        
        ## 📋 Próximos Passos
        
        1. Revisar mudanças em `requirements_new.txt`
        2. Testar aplicação com novas dependências
        3. Se OK, substituir `requirements.txt`
        4. Commitar mudanças no Git
        
        ## ⚠️ Importante
        
        - Sempre teste antes de atualizar em produção
        - Mantenha backups dos requirements
        - Documente breaking changes
        
        ---
        
        *Relatório gerado automaticamente*
      overwrite: true
    
  - name: "Notificar conclusão"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        📦 Verificação de Dependências Concluída!
        
        📅 Data: {{ datetime }}
        
        ✅ Ações realizadas:
        - Backup criado
        - Requirements atualizado
        - Relatório gerado
        
        📄 Verifique:
        reports/atualizacoes_{{ date }}.md
        
        ⚠️ Revise antes de aplicar!
