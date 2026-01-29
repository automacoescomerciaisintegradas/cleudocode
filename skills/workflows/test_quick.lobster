name: "Teste Rápido"
description: "Workflow de teste para validar Lobster Engine"
version: "1.0"
author: "Cleudocode Team"

variables:
  test_name: "Lobster Test"
  test_date: "{{ date }}"

steps:
  - name: "Criar diretório de teste"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "test_lobster_output"
    continue_on_error: true
    
  - name: "Escrever arquivo de teste"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "test_lobster_output/test_{{ datetime }}.txt"
      content: |
        Workflow: {{ test_name }}
        Data: {{ test_date }}
        Timestamp: {{ timestamp }}
        
        Este arquivo foi gerado pelo Lobster Workflow Engine!
      overwrite: true
    
  - name: "Listar arquivos criados"
    skill: "shell"
    action: "execute"
    params:
      command: "dir test_lobster_output"
    continue_on_error: true
    
  - name: "Ler arquivo criado"
    skill: "filesystem"
    action: "read_file"
    params:
      filepath: "test_lobster_output/test_{{ datetime }}.txt"
