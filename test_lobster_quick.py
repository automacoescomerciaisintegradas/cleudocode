"""
Teste rápido do Lobster Workflow Engine.
Valida execução de workflows e interpolação de variáveis.
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.lobster import LobsterWorkflow
from skills.manager import SkillManager
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


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
    
    console.print(f"[green]✅ Workflow de teste criado:[/green] {workflow_path}\n")
    
    return workflow_path


def test_lobster():
    """Executa testes do Lobster Workflow Engine."""
    
    console.print("\n[bold cyan]TESTE DO LOBSTER WORKFLOW ENGINE[/bold cyan]\n")

    
    try:
        # Criar workflow de teste
        workflow_path = create_test_workflow()
        
        # Inicializar componentes
        console.print("[yellow]Inicializando SkillManager...[/yellow]")
        skill_manager = SkillManager()
        
        console.print("[yellow]Inicializando LobsterWorkflow...[/yellow]")
        lobster = LobsterWorkflow(skill_manager)
        
        # Listar workflows disponíveis
        console.print("\n[bold]Workflows Disponíveis:[/bold]")
        workflows = lobster.list_workflows()
        
        for wf in workflows:
            console.print(f"  • {wf['name']} (v{wf['version']}) - {wf['steps']} steps")
        
        # Executar workflow de teste
        console.print("\n[bold]Executando Workflow 'Teste Rápido'...[/bold]\n")
        
        result = lobster.execute(
            "Teste Rápido",
            variables={
                "test_name": "Lobster Quick Test"
            }
        )
        
        # Exibir resultados
        console.print("\n[bold cyan]📊 RESULTADOS DA EXECUÇÃO[/bold cyan]\n")
        
        if result['success']:
            console.print(Panel(
                f"[bold green]✅ Workflow executado com sucesso![/bold green]\n\n"
                f"Workflow: {result['workflow']}\n"
                f"Steps executados: {result['steps_executed']}/{result['steps_total']}",
                title="Status",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[bold red]❌ Workflow falhou[/bold red]\n\n"
                f"Workflow: {result['workflow']}\n"
                f"Steps executados: {result['steps_executed']}/{result['steps_total']}",
                title="Status",
                border_style="red"
            ))
        
        # Detalhes de cada step
        console.print("\n[bold]Detalhes dos Steps:[/bold]\n")
        
        for i, step_result in enumerate(result['results'], 1):
            step_name = step_result['step']
            success = step_result['success']
            
            status_icon = "✅" if success else "❌"
            status_color = "green" if success else "red"
            
            console.print(f"{status_icon} [bold]Step {i}:[/bold] {step_name}")
            
            if success:
                step_data = step_result.get('result', {})
                if 'stdout' in step_data:
                    console.print(f"   [dim]Output:[/dim] {step_data['stdout'][:100]}...")
                elif 'content' in step_data:
                    console.print(f"   [dim]Content:[/dim] {len(step_data['content'])} caracteres")
                elif 'filepath' in step_data:
                    console.print(f"   [dim]Arquivo:[/dim] {step_data['filepath']}")
            else:
                error = step_result.get('error', 'Erro desconhecido')
                console.print(f"   [red]Erro:[/red] {error}")
            
            console.print()
        
        # Verificar arquivo gerado
        console.print("\n[bold]Verificando arquivo gerado...[/bold]")
        
        import glob
        generated_files = glob.glob("test_lobster_output/test_*.txt")
        
        if generated_files:
            console.print(f"[green]✅ Arquivo encontrado:[/green] {generated_files[0]}\n")
            
            # Ler e exibir conteúdo
            with open(generated_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
            
            syntax = Syntax(content, "text", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Conteúdo do Arquivo Gerado", border_style="cyan"))
        else:
            console.print("[red]❌ Nenhum arquivo foi gerado[/red]")
        
        # Resumo final
        console.print("\n")
        if result['success'] and generated_files:
            console.print(Panel(
                "[bold green]🎉 TESTE CONCLUÍDO COM SUCESSO![/bold green]\n\n"
                "✅ Workflow executado\n"
                "✅ Variáveis interpoladas\n"
                "✅ Arquivo gerado\n"
                "✅ Todos os steps funcionaram",
                title="Resultado Final",
                border_style="green"
            ))
            return True
        else:
            console.print(Panel(
                "[bold yellow]⚠️ TESTE PARCIALMENTE CONCLUÍDO[/bold yellow]\n\n"
                "Verifique os erros acima para mais detalhes.",
                title="Resultado Final",
                border_style="yellow"
            ))
            return False
            
    except Exception as e:
        console.print(f"\n[bold red]❌ Erro durante teste:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        return False


if __name__ == "__main__":
    try:
        success = test_lobster()
        sys.exit(0 if success else 1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Erro fatal:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)
