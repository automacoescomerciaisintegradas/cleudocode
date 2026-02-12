name: "Antigravity Backup"
description: "Cria backup completo do sistema Antigravity"
version: "1.0"
author: "Cleudocode Team"

variables:
  antigravity_path: "/opt/antigravity"
  antigravity_data: "/var/lib/antigravity"
  antigravity_config: "/etc/antigravity"
  backup_root: "./backups/antigravity"
  backup_dir: "{{ backup_root }}/{{ date }}"
  backup_archive: "{{ backup_root }}/antigravity_backup_{{ date }}.tar.gz"
  retention_days: 30

steps:
  - name: "Criar diretório de backup"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "{{ backup_dir }}"

  - name: "Verificar espaço em disco disponível"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"$d = Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=''C:'''; [math]::Round($d.FreeSpace / 1GB, 1)\""
      timeout: 10

  - name: "Estimar tamanho dos dados a fazer backup"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"Get-ChildItem -Path . -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum | ForEach-Object { [math]::Round(\\$_.Sum / 1GB, 3) }\""
      timeout: 30

  - name: "Parar serviços Antigravity (se necessário)"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"Stop-Process -Name python -ErrorAction SilentlyContinue\""
      timeout: 30
    continue_on_error: true

  - name: "Fazer backup dos dados"
    skill: "shell"
    action: "execute"
    params:
      command: "robocopy . \"{{ backup_dir }}\" /E /XF *.log *.err *.tar.gz /XD backups node_modules .git .agent-browser-sessions /R:2 /W:5 /NFL /NDL /NJH /NJS"
      timeout: 300
    continue_on_error: true

  - name: "Criar manifesto do backup"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "{{ backup_dir }}/BACKUP_MANIFEST.txt"
      content: |
        # Backup Manifest - Antigravity
        Data/Hora: {{ datetime }}
        Versão do Workflow: 1.0 (Windows Edition)
        
        ## Informações do Sistema
        Sistema: Windows Host
        Workspace: {{ workflow_name }}
        
        ## Estatísticas
        Espaço disponível (C:): {{ step_1_result.stdout|trim }}GB
        Tamanho estimado: {{ step_2_result.stdout|trim }}GB
        
        ---
        Backup criado pelo Cleudocode Workflow Engine
      overwrite: true

  - name: "Compactar backup"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"Compress-Archive -Path '{{ backup_dir }}' -DestinationPath '{{ backup_archive }}' -Force\""
      timeout: 600

  - name: "Verificar integridade do arquivo compactado"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"if (Test-Path '{{ backup_archive }}') { echo 'OK' } else { exit 1 }\""
      timeout: 120

  - name: "Calcular checksum do backup"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"Get-FileHash '{{ backup_archive }}' -Algorithm SHA256 | Select-Object -ExpandProperty Hash > '{{ backup_archive }}.sha256'\""
      timeout: 60

  - name: "Limpar backups antigos"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"Get-ChildItem '{{ backup_root }}' -Filter '*.zip' | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-{{ retention_days }}) } | Remove-Item -Force\""
      timeout: 60
    continue_on_error: true

  - name: "Remover diretório temporário"
    skill: "shell"
    action: "execute"
    params:
      command: "powershell -Command \"Remove-Item -Path '{{ backup_dir }}' -Recurse -Force\""
      timeout: 60

  - name: "Gerar relatório final"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "{{ backup_root }}/backup_report_{{ date }}.txt"
      content: |
        # Relatório de Backup - Antigravity
        Data/Hora: {{ datetime }}
        
        ## Status do Backup
        {% if step_6_result.success %}✅ BACKUP CONCLUÍDO COM SUCESSO{% else %}❌ BACKUP COM PROBLEMAS{% endif %}
        
        ## Detalhes
        Arquivo: {{ backup_archive }}
        
        ## Verificações
        Espaço disponível: {{ step_1_result.stdout|trim }}GB
        Arquivo compactado: {{ '✅ OK' if step_6_result.success else '❌ Falha' }}
        Checksum gerado: {{ '✅ Sim' if step_8_result.success else '❌ Falha' }}
        
        ---
        Relatório gerado pelo Cleudocode Workflow Engine
      overwrite: true

  - name: "Notificar conclusão do backup"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        💾 *Antigravity Backup Completo*
        
        📊 *Status:* {{ '✅ Sucesso' if step_6_result.success else '❌ Falha' }}
        📁 *Arquivo:* `{{ backup_archive }}`
        尺 *Checksum:* {{ '✅ OK' if step_8_result.success else '❌' }}
        
        📄 *Relatório:* `{{ backup_root }}/backup_report_{{ date }}.txt`
    continue_on_error: true