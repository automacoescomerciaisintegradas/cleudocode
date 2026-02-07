name: "Monitor de Conexão CleudoBridge"
description: "Monitora a conexão entre Telegram, WhatsApp e Antigravity Gateway"
version: "1.0"
author: "Orquestrador Pro Max"

steps:
  - name: "Checar Evolution API (WhatsApp)"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s -L -H \"apikey: {{ WHATSAPP_API_TOKEN_INSTANCE }}\" {{ WHATSAPP_BASE_URL }}/instance/connectionState/{{ WHATSAPP_INSTANCE_NAME }}"
      timeout: 10
    continue_on_error: true

  - name: "Checar Telegram Bot API"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s https://api.telegram.org/bot{{ TELEGRAM_BOT_TOKEN }}/getMe"
      timeout: 10
    continue_on_error: true

  - name: "Checar Antigravity Gateway"
    skill: "shell"
    action: "execute"
    params:
      command: "curl -s http://localhost:18900/health"
      timeout: 5
    continue_on_error: true

  - name: "Consolidar Saúde do Sistema"
    skill: "shell"
    action: "execute"
    params:
      command: |
        echo "=== STATUS DE CONEXÃO ==="
        echo "WhatsApp: {{ step_0_result.stdout }}"
        echo "Telegram: {{ step_1_result.stdout }}"
        echo "Antigravity: {{ step_2_result.stdout }}"
        echo "========================="
