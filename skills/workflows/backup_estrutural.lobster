name: "Backup Estrutural Cleudocode"
description: "Cria um backup compactado de todos os arquivos de configuração e código fonte"
version: "1.0"
author: "Orquestrador Pro Max"

variables:
  backup_dir: "exports/backups"

steps:
  - name: "Criar Diretório de Backup"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "{{ backup_dir }}"

  - name: "Gerar Arquivo Compactado"
    skill: "shell"
    action: "execute"
    params:
      command: "tar -czf {{ backup_dir }}/backup_cleudo_{{ date }}.tar.gz .env *.py gateways/ skills/ --exclude='__pycache__'"
      timeout: 60

  - name: "Notificar Tamanho do Backup"
    skill: "shell"
    action: "execute"
    params:
      command: "du -h {{ backup_dir }}/backup_cleudo_{{ date }}.tar.gz"
