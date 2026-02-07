name: "Sincronização com Git"
description: "Sincroniza projeto com repositório Git"
version: "1.0"
author: "Cleudocode Team"

variables:
  branch: "main"
  commit_message: "Auto-commit: {{ datetime }}"

steps:
  - name: "Verificar status do Git"
    skill: "shell"
    action: "execute"
    params:
      command: "git status"
    continue_on_error: true
    
  - name: "Adicionar arquivos modificados"
    skill: "shell"
    action: "execute"
    params:
      command: "git add ."
    continue_on_error: false
    
  - name: "Criar commit"
    skill: "shell"
    action: "execute"
    params:
      command: "git commit -m \"{{ commit_message }}\""
    continue_on_error: true
    
  - name: "Pull das últimas alterações"
    skill: "shell"
    action: "execute"
    params:
      command: "git pull origin {{ branch }}"
    retry: 2
    retry_delay: 3
    continue_on_error: true
    
  - name: "Push para o repositório"
    skill: "shell"
    action: "execute"
    params:
      command: "git push origin {{ branch }}"
    retry: 2
    retry_delay: 3
    continue_on_error: true
    
  - name: "Verificar log recente"
    skill: "shell"
    action: "execute"
    params:
      command: "git log -5 --oneline"
    continue_on_error: true
    
  - name: "Criar relatório de sincronização"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "reports/git_sync_{{ date }}.txt"
      content: |
        ===================================
        SINCRONIZAÇÃO GIT
        ===================================
        
        Data: {{ datetime }}
        Branch: {{ branch }}
        Commit: {{ commit_message }}
        
        STATUS INICIAL:
        {{ step_0_result.stdout }}
        
        COMMITS RECENTES:
        {{ step_5_result.stdout }}
        
        RESULTADO:
        {% if step_4_result.success %}✅ Push realizado com sucesso{% else %}❌ Erro no push{% endif %}
        
        ===================================
      overwrite: true
    
  - name: "Notificar resultado"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        {% if step_4_result.success %}
        ✅ Git Sincronizado!
        {% else %}
        ⚠️ Problema na Sincronização Git
        {% endif %}
        
        📅 Data: {{ datetime }}
        🌿 Branch: {{ branch }}
        💬 Commit: {{ commit_message }}
        
        📄 Relatório: reports/git_sync_{{ date }}.txt
