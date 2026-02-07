name: "Campanha de Massa WhatsApp"
description: "Executa disparos em massa para uma lista de contatos via Evolution API"
version: "1.0"
author: "Orquestrador Pro Max"

variables:
  contatos: "5511999999999" # Defina aqui os números ou caminho do arquivo
  mensagem: "Olá! Esta é uma mensagem automática do Cleudocode. 🚀"

steps:
  - name: "Validar Conexão WhatsApp"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -L -H \"apikey: {{ WHATSAPP_API_TOKEN_INSTANCE }}\" {{ WHATSAPP_BASE_URL }}/instance/connectionState/{{ WHATSAPP_INSTANCE_NAME }} | grep open"
      timeout: 10
    continue_on_error: false

  - name: "Executar Disparos"
    skill: "shell"
    action: "execute"
    params:
      command: "python3 disparo_massa_whatsapp.py \"{{ contatos }}\" \"{{ mensagem }}\""
      timeout: 300
    
  - name: "Registrar Log de Campanha"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "logs/campanhas/log_{{ datetime_compact }}.txt"
      content: |
        # Relatório de Campanha
        Data: {{ datetime }}
        Contatos: {{ contatos }}
        Resultado: {{ step_1_result.stdout }}
      overwrite: true

  - name: "Notificar Sucesso"
    skill: "shell"
    action: "execute"
    params:
      command: "echo '✅ Campanha de massa processada. Verifique os logs em logs/campanhas/'"
