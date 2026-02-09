import os
import sys
import subprocess
import shutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def check_command(cmd, name=None):
    name = name or cmd
    path = shutil.which(cmd)
    if not path:
        try:
            # Fallback para subprocess
            result = subprocess.run(["which", cmd], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
        except:
            pass
            
    if path:
        return True, f"[green]✓[/green] {name} encontrado em {path}"
    return False, f"[red]✗[/red] {name} não encontrado"

def check_python_module(module):
    try:
        __import__(module)
        return True, f"[green]✓[/green] Módulo Python {module} instalado"
    except ImportError:
        return False, f"[red]✗[/red] Módulo Python {module} não encontrado"

def run_doctor():
    console.print(Panel.fit("[bold blue]Cleudocode Doctor - Verificação de Saúde[/bold blue]"))
    
    table = Table(title="Dependências do Sistema")
    table.add_column("Componente", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Mensagem", style="green")

    # 1. Ferramentas de Sistema
    deps = [
        ("python3", "Python 3"),
        ("pip3", "Pip"),
        ("git", "Git"),
        ("docker", "Docker"),
        ("ffmpeg", "FFmpeg"),
        ("curl", "Curl"),
    ]

    for cmd, name in deps:
        # Tentar python se python3 falhar, e vice-versa
        success, msg = check_command(cmd, name)
        if not success and cmd == "python3":
            success, msg = check_command("python", name)
        if not success and cmd == "pip3":
            success, msg = check_command("pip", name)
            
        status = "[bold green]OK[/bold green]" if success else "[bold red]FALHA[/bold red]"
        table.add_row(name, status, msg)

    # 2. Módulos Python Críticos
    py_modules = [
        "streamlit",
        "flask",
        "requests",
        "anthropic",
        "openai",
        "faster_whisper",
        "playwright",
        "dotenv",
        "pypdf",
    ]

    for mod in py_modules:
        success, msg = check_python_module(mod)
        status = "[bold green]OK[/bold green]" if success else "[bold red]FALHA[/bold red]"
        table.add_row(f"Python: {mod}", status, msg)

    console.print(table)

    # 3. Verificações de Hardware/Ambiente
    console.print("\n[bold]Ambiente:[/bold]")
    console.print(f"  OS: {sys.platform}")
    console.print(f"  WSL: {'Sim' if 'microsoft-standard' in os.uname().release.lower() else 'Não'}")
    
    # 4. Status do Gateway (se rodando)
    console.print("\n[bold]Serviços:[/bold]")
    try:
        import requests
        resp = requests.get("http://localhost:18900/health", timeout=2)
        if resp.status_code == 200:
            console.print("  [green]✓[/green] Gateway: Online (Porta 18900)")
        else:
            console.print(f"  [yellow]⚠[/yellow] Gateway: Respondeu com erro {resp.status_code}")
    except:
        console.print("  [red]✗[/red] Gateway: Offline")

    console.print("\n[bold green]Doutor finalizou a consulta![/bold green]")
    console.print("\n[dim]\"© Automações Comerciais Integradas! 2026 ⚙️ Todos os direitos reservados.\"[/dim]")
    console.print("[dim]contato@automacoescomerciais.com.br[/dim]")

if __name__ == "__main__":
    run_doctor()
