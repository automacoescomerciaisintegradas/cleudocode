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
      command: "df -BG . | tail -1 | awk '{print $4}' | sed 's/G//'"
      timeout: 10

  - name: "Estimar tamanho dos dados a fazer backup"
    skill: "shell"
    action: "execute"
    params:
      command: "du -s {{ antigravity_data }} {{ antigravity_config }} 2>/dev/null | awk '{sum+=$1} END {print sum/1024/1024}' || echo '0'"
      timeout: 30

  - name: "Verificar se há espaço suficiente"
    skill: "shell"
    action: "execute"
    params:
      command: |
        AVAILABLE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
        NEEDED=$(du -s {{ antigravity_data }} {{ antigravity_config }} 2>/dev/null | awk '{sum+=$1} END {print sum/1024/1024}' || echo '0')
        if [ "$AVAILABLE" -gt "$NEEDED" ]; then
          echo "Espaço suficiente: ${AVAILABLE}GB disponível, ${NEEDED}GB necessário"
        else
          echo "ERRO: Espaço insuficiente: ${AVAILABLE}GB disponível, ${NEEDED}GB necessário"
          exit 1
        fi
      timeout: 10

  - name: "Parar serviços Antigravity (se necessário)"
    skill: "shell"
    action: "execute"
    params:
      command: "systemctl is-active antigravity && systemctl stop antigravity || echo 'Serviço não está rodando'"
      timeout: 30
    continue_on_error: true

  - name: "Fazer backup dos dados"
    skill: "shell"
    action: "execute"
    params:
      command: "cp -r {{ antigravity_data }}/* {{ backup_dir }}/ 2>/dev/null || echo 'Nenhum dado encontrado'"
      timeout: 300

  - name: "Fazer backup das configurações"
    skill: "shell"
    action: "execute"
    params:
      command: "cp -r {{ antigravity_config }}/* {{ backup_dir }}/config/ 2>/dev/null || mkdir -p {{ backup_dir }}/config"
      timeout: 60

  - name: "Fazer backup dos logs"
    skill: "shell"
    action: "execute"
    params:
      command: "cp -r /var/log/antigravity/* {{ backup_dir }}/logs/ 2>/dev/null || mkdir -p {{ backup_dir }}/logs"
      timeout: 120

  - name: "Criar manifesto do backup"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "{{ backup_dir }}/BACKUP_MANIFEST.txt"
      content: |
        # Backup Manifest - Antigravity
        Data/Hora: {{ datetime }}
        Versão do Workflow: 1.0
        
        ## Informações do Sistema
        Hostname: $(hostname)
        Sistema: $(uname -a)
        
        ## Conteúdo do Backup
        - Dados: {{ antigravity_data }}
        - Configurações: {{ antigravity_config }}
        - Logs: /var/log/antigravity
        
        ## Estatísticas
        Espaço disponível: {{ step_1_result.stdout }}GB
        Tamanho estimado: {{ step_2_result.stdout }}GB
        
        ## Verificação
        Dados copiados: {% if step_5_result.success %}✅ Sim{% else %}❌ Falha{% endif %}
        Configs copiadas: {% if step_6_result.success %}✅ Sim{% else %}❌ Falha{% endif %}
        Logs copiados: {% if step_7_result.success %}✅ Sim{% else %}❌ Falha{% endif %}
        
        ## Instruções de Restauração
        1. Parar serviços: systemctl stop antigravity
        2. Restaurar dados: cp -r {{ backup_dir }}/* {{ antigravity_data }}/
        3. Restaurar configs: cp -r {{ backup_dir }}/config/* {{ antigravity_config }}/
        4. Iniciar serviços: systemctl start antigravity
        5. Verificar logs: journalctl -u antigravity -f
        
        ---
        Backup criado pelo Cleudocode Workflow Engine
      overwrite: true

  - name: "Reiniciar serviços Antigravity"
    skill: "shell"
    action: "execute"
    params:
      command: "systemctl start antigravity && sleep 5 && systemctl is-active antigravity"
      timeout: 60
    continue_on_error: true

  - name: "Compactar backup"
    skill: "shell"
    action: "execute"
    params:
      command: "tar -czf {{ backup_archive }} -C {{ backup_root }} {{ date }}"
      timeout: 600

  - name: "Verificar integridade do arquivo compactado"
    skill: "shell"
    action: "execute"
    params:
      command: "tar -tzf {{ backup_archive }} > /dev/null && echo 'Arquivo íntegro'"
      timeout: 120

  - name: "Calcular checksum do backup"
    skill: "shell"
    action: "execute"
    params:
      command: "sha256sum {{ backup_archive }} > {{ backup_archive }}.sha256"
      timeout: 60

  - name: "Limpar backups antigos"
    skill: "shell"
    action: "execute"
    params:
      command: "find {{ backup_root }} -name '*.tar.gz' -mtime +{{ retention_days }} -delete"
      timeout: 60
    continue_on_error: true

  - name: "Remover diretório temporário"
    skill: "shell"
    action: "execute"
    params:
      command: "rm -rf {{ backup_dir }}"
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
        {% if step_10_result.success and step_11_result.success %}✅ BACKUP CONCLUÍDO COM SUCESSO{% else %}❌ BACKUP COM PROBLEMAS{% endif %}
        
        ## Detalhes
        Arquivo: {{ backup_archive }}
        Tamanho: $(ls -lh {{ backup_archive }} | awk '{print $5}')
        Checksum: $(cat {{ backup_archive }}.sha256 | awk '{print $1}')
        
        ## Verificações
        Espaço suficiente: {% if step_3_result.success %}✅ Sim{% else %}❌ Não{% endif %}
        Dados copiados: {% if step_5_result.success %}✅ Sim{% else %}❌ Falha{% endif %}
        Arquivo compactado: {% if step_10_result.success %}✅ Sim{% else %}❌ Falha{% endif %}
        Integridade verificada: {% if step_11_result.success %}✅ Sim{% else %}❌ Falha{% endif %}
        Serviço reiniciado: {% if step_9_result.success %}✅ Sim{% else %}⚠️ Verificar{% endif %}
        
        ## Limpeza
        Backups antigos removidos: {% if step_13_result.success %}✅ Sim{% else %}⚠️ Verificar{% endif %}
        Diretório temporário limpo: {% if step_14_result.success %}✅ Sim{% else %}⚠️ Verificar{% endif %}
        
        ---
        Relatório gerado pelo Cleudocode Workflow Engine
      overwrite: true

  - name: "Notificar conclusão do backup"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        💾 *Antigravity Backup Completo*
        
        📊 *Status:* {% if step_10_result.success and step_11_result.success %}✅ Sucesso{% else %}❌ Com problemas{% endif %}
        
        📁 *Arquivo:* `{{ backup_archive }}`
        📏 *Tamanho:* $(ls -lh {{ backup_archive }} 2>/dev/null | awk '{print $5}' || echo 'N/A')
        
        🔍 *Verificações:*
        • Integridade: {% if step_11_result.success %}✅ OK{% else %}❌ Falha{% endif %}
        • Checksum: {% if step_12_result.success %}✅ Gerado{% else %}❌ Falha{% endif %}
        • Serviço: {% if step_9_result.success %}✅ Reiniciado{% else %}⚠️ Verificar{% endif %}
        
        🧹 *Limpeza:* {% if step_13_result.success %}✅ Backups antigos removidos{% else %}⚠️ Verificar{% endif %}
        
        📄 *Relatório:* `{{ backup_root }}/backup_report_{{ date }}.txt`
    continue_on_error: true