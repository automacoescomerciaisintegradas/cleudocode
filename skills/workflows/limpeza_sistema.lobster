name: "Limpeza de Arquivos Temporários"
description: "Remove arquivos temporários e cache para liberar espaço"
version: "1.0"
author: "Cleudocode Team"

steps:
  - name: "Verificar espaço em disco antes"
    skill: "shell"
    action: "execute"
    params:
      command: "wmic logicaldisk get size,freespace,caption"
    continue_on_error: true
    
  - name: "Limpar cache Python"
    skill: "shell"
    action: "execute"
    params:
      command: "del /s /q __pycache__ *.pyc *.pyo"
    continue_on_error: true
    
  - name: "Limpar logs antigos"
    skill: "shell"
    action: "execute"
    params:
      command: "forfiles /p logs /s /m *.log /d -7 /c \"cmd /c del @path\""
    continue_on_error: true
    
  - name: "Limpar arquivos temporários"
    skill: "shell"
    action: "execute"
    params:
      command: "del /s /q temp\\*.* test_lobster_output\\*.*"
    continue_on_error: true
    
  - name: "Verificar espaço em disco depois"
    skill: "shell"
    action: "execute"
    params:
      command: "wmic logicaldisk get size,freespace,caption"
    continue_on_error: true
    
  - name: "Criar relatório de limpeza"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "reports/limpeza_{{ date }}.txt"
      content: |
        ===================================
        RELATÓRIO DE LIMPEZA
        ===================================
        
        Data: {{ datetime }}
        
        ANTES:
        {{ step_0_result.stdout }}
        
        DEPOIS:
        {{ step_4_result.stdout }}
        
        AÇÕES REALIZADAS:
        ✓ Cache Python removido
        ✓ Logs antigos (>7 dias) removidos
        ✓ Arquivos temporários removidos
        
        ===================================
      overwrite: true
    
  - name: "Notificar conclusão"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        🧹 Limpeza Concluída!
        
        📅 Data: {{ datetime }}
        📄 Relatório: reports/limpeza_{{ date }}.txt
        
        ✓ Cache Python removido
        ✓ Logs antigos removidos
        ✓ Arquivos temporários removidos
