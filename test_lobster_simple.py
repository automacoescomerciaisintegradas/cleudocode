"""
Teste simples do Lobster Workflow Engine (sem rich para compatibilidade Windows).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.lobster import LobsterWorkflow
from skills.manager import SkillManager


def create_test_workflow():
    """Cria workflow de teste."""
    
    workflow_content = """name: "Teste Rápido"
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
"""
    
    # Criar diretório de workflows se não existir
    os.makedirs("skills/workflows", exist_ok=True)
    
    # Salvar workflow
    workflow_path = "skills/workflows/test_quick.lobster"
    with open(workflow_path, "w", encoding="utf-8") as f:
        f.write(workflow_content)
    
    print(f"[OK] Workflow de teste criado: {workflow_path}\n")
    
    return workflow_path


def test_lobster():
    """Executa testes do Lobster Workflow Engine."""
    
    print("\n" + "="*60)
    print(" TESTE DO LOBSTER WORKFLOW ENGINE")
    print("="*60 + "\n")
    
    try:
        # Criar workflow de teste
        workflow_path = create_test_workflow()
        
        # Inicializar componentes
        print("Inicializando SkillManager...")
        skill_manager = SkillManager()
        
        print("Inicializando LobsterWorkflow...")
        lobster = LobsterWorkflow(skill_manager)
        
        # Listar workflows disponíveis
        print("\nWorkflows Disponíveis:")
        workflows = lobster.list_workflows()
        
        for wf in workflows:
            print(f"  - {wf['name']} (v{wf['version']}) - {wf['steps']} steps")
        
        # Executar workflow de teste
        print("\nExecutando Workflow 'Teste Rápido'...\n")
        
        result = lobster.execute(
            "Teste Rápido",
            variables={
                "test_name": "Lobster Quick Test"
            }
        )
        
        # Exibir resultados
        print("\n" + "="*60)
        print(" RESULTADOS DA EXECUÇÃO")
        print("="*60 + "\n")
        
        if result['success']:
            print(f"[OK] Workflow executado com sucesso!")
            print(f"Workflow: {result['workflow']}")
            print(f"Steps executados: {result['steps_executed']}/{result['steps_total']}")
        else:
            print(f"[ERRO] Workflow falhou")
            print(f"Workflow: {result['workflow']}")
            print(f"Steps executados: {result['steps_executed']}/{result['steps_total']}")
        
        # Detalhes de cada step
        print("\nDetalhes dos Steps:\n")
        
        for i, step_result in enumerate(result['results'], 1):
            step_name = step_result['step']
            success = step_result['success']
            
            status = "[OK]" if success else "[ERRO]"
            
            print(f"{status} Step {i}: {step_name}")
            
            if success:
                step_data = step_result.get('result', {})
                if 'stdout' in step_data:
                    print(f"   Output: {step_data['stdout'][:100]}...")
                elif 'content' in step_data:
                    print(f"   Content: {len(step_data['content'])} caracteres")
                elif 'filepath' in step_data:
                    print(f"   Arquivo: {step_data['filepath']}")
            else:
                error = step_result.get('error', 'Erro desconhecido')
                print(f"   Erro: {error}")
            
            print()
        
        # Verificar arquivo gerado
        print("Verificando arquivo gerado...")
        
        import glob
        generated_files = glob.glob("test_lobster_output/test_*.txt")
        
        if generated_files:
            print(f"[OK] Arquivo encontrado: {generated_files[0]}\n")
            
            # Ler e exibir conteúdo
            with open(generated_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("-" * 60)
            print("Conteúdo do Arquivo Gerado:")
            print("-" * 60)
            print(content)
            print("-" * 60)
        else:
            print("[ERRO] Nenhum arquivo foi gerado")
        
        # Resumo final
        print("\n" + "="*60)
        if result['success'] and generated_files:
            print(" [OK] TESTE CONCLUÍDO COM SUCESSO!")
            print("="*60)
            print("\n[OK] Workflow executado")
            print("[OK] Variáveis interpoladas")
            print("[OK] Arquivo gerado")
            print("[OK] Todos os steps funcionaram\n")
            return True
        else:
            print(" [AVISO] TESTE PARCIALMENTE CONCLUÍDO")
            print("="*60)
            print("\nVerifique os erros acima para mais detalhes.\n")
            return False
            
    except Exception as e:
        print(f"\n[ERRO] Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = test_lobster()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[AVISO] Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO] Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
