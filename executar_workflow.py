"""
Script de Entrada para o Lobster Workflow Engine
CLEUDOCODE - Hub de Automação
"""
import sys
from workflow_manager import executar_workflow, listar_workflows

def main():
    if len(sys.argv) < 2:
        listar_workflows()
        sys.exit(0)
    
    workflow_name = sys.argv[1]
    
    # Suporte a variáveis via linha de comando (opcional)
    # Ex: python executar_workflow.py "Campanha" "contatos=5511...;mensagem=Ola"
    variables = {}
    if len(sys.argv) > 2:
        try:
            vars_str = sys.argv[2]
            for pair in vars_str.split(';'):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    variables[k.strip()] = v.strip()
        except:
            print("⚠️ Erro ao processar variáveis extras. Use formato: k=v;k2=v2")

    success = executar_workflow(workflow_name, variables)
    
    if success:
        print(f"\n✅ Workflow '{workflow_name}' finalizado com sucesso.")
        sys.exit(0)
    else:
        print(f"\n❌ Falha na execução do workflow '{workflow_name}'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
