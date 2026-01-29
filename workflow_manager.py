"""
Gerenciador de Workflows - Lista e executa workflows do Lobster.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.lobster import LobsterWorkflow
from skills.manager import SkillManager


def listar_workflows():
    """Lista todos os workflows disponíveis."""
    
    print("\n" + "="*70)
    print(" WORKFLOWS DISPONÍVEIS - LOBSTER ENGINE")
    print("="*70 + "\n")
    
    # Inicializar
    skill_manager = SkillManager()
    lobster = LobsterWorkflow(skill_manager)
    
    # Listar workflows
    workflows = lobster.list_workflows()
    
    if not workflows:
        print("[AVISO] Nenhum workflow encontrado em skills/workflows/\n")
        return
    
    print(f"Total de workflows: {len(workflows)}\n")
    
    for i, wf in enumerate(workflows, 1):
        print(f"{i}. {wf['name']}")
        print(f"   Descrição: {wf['description']}")
        print(f"   Versão: {wf['version']}")
        print(f"   Steps: {wf['steps']}")
        print()
    
    print("="*70)
    print("\nPara executar um workflow, use:")
    print("  python executar_workflow.py \"Nome do Workflow\"")
    print()


def mostrar_detalhes(workflow_name: str):
    """Mostra detalhes de um workflow específico."""
    
    print("\n" + "="*70)
    print(f" DETALHES DO WORKFLOW: {workflow_name}")
    print("="*70 + "\n")
    
    # Inicializar
    skill_manager = SkillManager()
    lobster = LobsterWorkflow(skill_manager)
    
    # Obter informações
    info = lobster.get_workflow_info(workflow_name)
    
    if not info:
        print(f"[ERRO] Workflow '{workflow_name}' não encontrado\n")
        return
    
    print(f"Nome: {info['name']}")
    print(f"Descrição: {info['description']}")
    print(f"Versão: {info['version']}")
    print(f"Autor: {info['author']}")
    print(f"\nTotal de Steps: {len(info['steps'])}\n")
    
    print("Steps:")
    for i, step in enumerate(info['steps'], 1):
        print(f"  {i}. {step['name']}")
        print(f"     Skill: {step['skill']}")
        print(f"     Action: {step['action']}")
        print()
    
    if info['variables']:
        print("Variáveis:")
        for var, value in info['variables'].items():
            print(f"  - {var}: {value}")
        print()
    
    print("="*70)
    print()


def executar_workflow(workflow_name: str, variables: dict = None):
    """Executa um workflow."""
    
    print("\n" + "="*70)
    print(f" EXECUTANDO WORKFLOW: {workflow_name}")
    print("="*70 + "\n")
    
    # Inicializar
    skill_manager = SkillManager()
    lobster = LobsterWorkflow(skill_manager)
    
    # Executar
    print(f"Iniciando execução...\n")
    
    result = lobster.execute(workflow_name, variables=variables)
    
    # Exibir resultados
    print("\n" + "="*70)
    print(" RESULTADO DA EXECUÇÃO")
    print("="*70 + "\n")
    
    if result['success']:
        print("[OK] Workflow executado com sucesso!")
    else:
        print("[ERRO] Workflow falhou")
    
    print(f"\nWorkflow: {result['workflow']}")
    print(f"Steps executados: {result['steps_executed']}/{result['steps_total']}")
    
    # Detalhes dos steps
    print("\nDetalhes dos Steps:\n")
    
    for i, step_result in enumerate(result['results'], 1):
        step_name = step_result['step']
        success = step_result['success']
        
        status = "[OK]" if success else "[ERRO]"
        print(f"{status} Step {i}: {step_name}")
        
        if not success and 'error' in step_result:
            print(f"   Erro: {step_result['error']}")
    
    print("\n" + "="*70)
    print()
    
    return result['success']


def menu_interativo():
    """Menu interativo para gerenciar workflows."""
    
    while True:
        print("\n" + "="*70)
        print(" LOBSTER WORKFLOW MANAGER")
        print("="*70)
        print("\n1. Listar todos os workflows")
        print("2. Ver detalhes de um workflow")
        print("3. Executar workflow")
        print("4. Sair")
        print()
        
        escolha = input("Escolha uma opção: ").strip()
        
        if escolha == "1":
            listar_workflows()
        
        elif escolha == "2":
            nome = input("\nNome do workflow: ").strip()
            if nome:
                mostrar_detalhes(nome)
        
        elif escolha == "3":
            nome = input("\nNome do workflow: ").strip()
            if nome:
                # Perguntar se quer passar variáveis
                usar_vars = input("Deseja passar variáveis? (s/n): ").strip().lower()
                
                variables = {}
                if usar_vars == 's':
                    print("\nDigite as variáveis (formato: chave=valor, vazio para terminar):")
                    while True:
                        var = input("  ").strip()
                        if not var:
                            break
                        if '=' in var:
                            key, value = var.split('=', 1)
                            variables[key.strip()] = value.strip()
                
                executar_workflow(nome, variables if variables else None)
        
        elif escolha == "4":
            print("\nAté logo!\n")
            break
        
        else:
            print("\n[ERRO] Opção inválida")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "list":
            listar_workflows()
        
        elif comando == "info" and len(sys.argv) > 2:
            mostrar_detalhes(sys.argv[2])
        
        elif comando == "run" and len(sys.argv) > 2:
            workflow_name = sys.argv[2]
            
            # Variáveis opcionais
            variables = {}
            for arg in sys.argv[3:]:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    variables[key] = value
            
            success = executar_workflow(workflow_name, variables if variables else None)
            sys.exit(0 if success else 1)
        
        else:
            print("\nUso:")
            print("  python workflow_manager.py list")
            print("  python workflow_manager.py info \"Nome do Workflow\"")
            print("  python workflow_manager.py run \"Nome do Workflow\" [var1=valor1 var2=valor2]")
            print("\nOu execute sem argumentos para o menu interativo\n")
    
    else:
        # Menu interativo
        try:
            menu_interativo()
        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário\n")
            sys.exit(0)
