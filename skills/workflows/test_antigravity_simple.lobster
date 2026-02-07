name: "Test Antigravity Simple"
description: "Teste simples dos workflows Antigravity"
version: "1.0"
author: "Cleudocode Team"

variables:
  test_message: "Teste do sistema Antigravity"
  report_path: "reports"

steps:
  - name: "Criar diretório de relatórios"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "reports"

  - name: "Verificar data e hora"
    skill: "shell"
    action: "execute"
    params:
      command: "echo Teste executado em: %date% %time%"
      timeout: 5

  - name: "Criar relatório de teste"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "reports/test_antigravity.txt"
      content: |
        # Teste Antigravity - Relatório
        
        ## Informações
        Mensagem: {{ test_message }}
        Data/Hora: {{ datetime }}
        
        ## Status
        ✅ Diretório criado
        ✅ Comando executado
        ✅ Arquivo gerado
        
        ## Resultado
        Teste concluído com sucesso!
        
        ---
        Gerado pelo Cleudocode Workflow Engine
      overwrite: true

  - name: "Notificar conclusão"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        🧪 *Teste Antigravity Concluído*
        
        ✅ Workflow executado com sucesso
        📄 Relatório: reports/test_antigravity.txt
        🕐 Horário: {{ datetime }}
        
        Sistema funcionando corretamente!
    continue_on_error: true