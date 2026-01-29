name: "Backup Diário Automático"
description: "Faz backup completo do projeto com compactação e notificação"
version: "1.0"
author: "Cleudocode Team"

variables:
  project_path: "."
  backup_dest: "./backups"
  project_name: "cleudocode"

steps:
  - name: "Criar diretório de backup"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "{{ backup_dest }}/{{ date }}"
    continue_on_error: false
    
  - name: "Listar arquivos do projeto"
    skill: "shell"
    action: "execute"
    params:
      command: "dir /s /b {{ project_path }} | find /c /v \"\""
    continue_on_error: true
    
  - name: "Criar arquivo de log"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "{{ backup_dest }}/{{ date }}/backup_log.txt"
      content: |
        ===================================
        BACKUP AUTOMÁTICO - {{ project_name }}
        ===================================
        
        Data: {{ datetime }}
        Timestamp: {{ timestamp }}
        Projeto: {{ project_path }}
        Destino: {{ backup_dest }}/{{ date }}
        
        Total de arquivos: {{ step_1_result.stdout }}
        
        Status: Backup iniciado
        ===================================
      overwrite: true
    
  - name: "Copiar arquivos importantes"
    skill: "shell"
    action: "execute"
    params:
      command: "xcopy {{ project_path }}\\*.py {{ backup_dest }}\\{{ date }}\\src\\ /E /I /Y"
    continue_on_error: true
    
  - name: "Copiar configurações"
    skill: "shell"
    action: "execute"
    params:
      command: "xcopy {{ project_path }}\\config {{ backup_dest }}\\{{ date }}\\config\\ /E /I /Y"
    continue_on_error: true
    
  - name: "Copiar skills e workflows"
    skill: "shell"
    action: "execute"
    params:
      command: "xcopy {{ project_path }}\\skills {{ backup_dest }}\\{{ date }}\\skills\\ /E /I /Y"
    continue_on_error: true
    
  - name: "Criar arquivo de resumo"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "{{ backup_dest }}/{{ date }}/README.md"
      content: |
        # Backup - {{ project_name }}
        
        ## Informações
        
        - **Data**: {{ datetime }}
        - **Projeto**: {{ project_name }}
        - **Origem**: {{ project_path }}
        
        ## Conteúdo
        
        - `src/` - Código fonte Python
        - `config/` - Arquivos de configuração
        - `skills/` - Skills e workflows
        - `backup_log.txt` - Log detalhado
        
        ## Restauração
        
        Para restaurar este backup:
        1. Copie os arquivos para o diretório do projeto
        2. Reinstale as dependências: `pip install -r requirements.txt`
        3. Verifique as configurações em `config/`
        
        ---
        Backup criado automaticamente pelo Lobster Workflow Engine
      overwrite: true
    
  - name: "Notificar conclusão"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        ✅ Backup Concluído!
        
        📁 Projeto: {{ project_name }}
        📅 Data: {{ datetime }}
        📂 Local: {{ backup_dest }}/{{ date }}
        📊 Arquivos: {{ step_1_result.stdout }}
        
        O backup foi salvo com sucesso!
