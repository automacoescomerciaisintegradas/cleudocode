"""
Script Mestre de Testes - Cleudocodebot
Executa todos os testes de validação do sistema.
"""

import sys
import os
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def run_test(test_name, test_script):
    """Executa um script de teste."""
    
    console.print(f"\n[bold cyan]▶️ Executando: {test_name}[/bold cyan]")
    console.print(f"[dim]Script: {test_script}[/dim]\n")
    
    try:
        result = subprocess.run(
            [sys.executable, test_script],
            capture_output=False,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        success = result.returncode == 0
        
        if success:
            console.print(f"\n[green]✅ {test_name} concluído com sucesso[/green]")
        else:
            console.print(f"\n[red]❌ {test_name} falhou[/red]")
        
        return success
        
    except Exception as e:
        console.print(f"\n[red]❌ Erro ao executar {test_name}:[/red] {e}")
        return False


def main():
    """Executa todos os testes."""
    
    console.print(Panel(
        "[bold cyan]🧪 CLEUDOCODEBOT - BATERIA COMPLETA DE TESTES[/bold cyan]\n\n"
        "Este script executa todos os testes de validação:\n\n"
        "1. 🔒 Sandbox Security\n"
        "2. 🦞 Lobster Workflow Engine\n"
        "3. 🎙️ Voice Integration (Whisper + Coqui TTS)",
        title="Test Suite",
        border_style="cyan"
    ))
    
    # Definir testes
    tests = [
        ("🔒 Sandbox Security", "test_sandbox_quick.py"),
        ("🦞 Lobster Workflow", "test_lobster_quick.py"),
        ("🎙️ Voice Integration", "test_whisper_quick.py")
    ]
    
    # Executar testes
    results = {}
    
    for test_name, test_script in tests:
        # Verificar se script existe
        if not os.path.exists(test_script):
            console.print(f"[red]❌ Script não encontrado:[/red] {test_script}")
            results[test_name] = False
            continue
        
        # Executar teste
        success = run_test(test_name, test_script)
        results[test_name] = success
        
        # Separador
        console.print("\n" + "="*60)
    
    # Resumo final
    console.print("\n")
    console.print("[bold cyan]📊 RESUMO GERAL DOS TESTES[/bold cyan]\n")
    
    # Criar tabela de resultados
    table = Table(title="Resultados")
    table.add_column("Teste", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Resultado")
    
    for test_name, success in results.items():
        if success:
            table.add_row(test_name, "✅ PASSOU", "[green]Sucesso[/green]")
        else:
            table.add_row(test_name, "❌ FALHOU", "[red]Erro[/red]")
    
    console.print(table)
    
    # Estatísticas
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    console.print("\n")
    
    if failed == 0:
        console.print(Panel(
            f"[bold green]🎉 TODOS OS TESTES PASSARAM![/bold green]\n\n"
            f"✅ Total: {total}\n"
            f"✅ Aprovados: {passed}\n"
            f"❌ Falhas: {failed}\n\n"
            f"[bold]O sistema está pronto para uso![/bold]",
            title="Resultado Final",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[bold yellow]⚠️ ALGUNS TESTES FALHARAM[/bold yellow]\n\n"
            f"📊 Total: {total}\n"
            f"✅ Aprovados: {passed}\n"
            f"❌ Falhas: {failed}\n\n"
            f"[bold]Revise os erros acima para mais detalhes.[/bold]",
            title="Resultado Final",
            border_style="yellow"
        ))
    
    return failed == 0


if __name__ == "__main__":
    try:
        console.print("\n")
        success = main()
        console.print("\n")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️ Testes interrompidos pelo usuário[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Erro fatal:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)
