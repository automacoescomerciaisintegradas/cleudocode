import os
import subprocess
import click
from rich.console import Console
from pathlib import Path

console = Console()
project_root = Path(__file__).parent.parent

@click.group()
def gateway():
    """Gerencia o Antigravity Gateway"""
    pass

@gateway.command()
@click.option('--port', default=18900, help='Porta do gateway')
def start(port):
    """Inicia o gateway e o daemon"""
    console.print(f"[bold green]Iniciando Gateway na porta {port}...[/bold green]")
    
    # Iniciar via Docker Compose se disponível
    try:
        subprocess.run(["docker", "compose", "up", "-d"], cwd=str(project_root), check=True)
        console.print("[green]✓ Containers levantados via Docker Compose.[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠ Docker falhou: {e}. Tentando iniciar localmente...[/yellow]")
        # Iniciar web_server.py
        if os.name == 'nt':
            subprocess.Popen(["start", "cmd", "/c", "python web_server.py"], cwd=str(project_root), shell=True)
        else:
            subprocess.Popen(["python3", "web_server.py"], cwd=str(project_root), start_new_session=True)
        console.print("[green]✓ Servidor local disparado.[/green]")

@gateway.command()
def stop():
    """Para o gateway"""
    console.print("[bold yellow]Parando serviços...[/bold yellow]")
    try:
        subprocess.run(["docker", "compose", "down"], cwd=str(project_root), check=True)
        console.print("[green]✓ Containers parados.[/green]")
    except:
        # Tentar kill no python process if local
        console.print("[yellow]Tentando parar processos locais...[/yellow]")
        if os.name == 'nt':
            subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], shell=True)
        else:
            subprocess.run(["pkill", "-f", "web_server.py"])
        console.print("[green]✓ Processos interrompidos.[/green]")

@gateway.command()
def logs():
    """Mostra os logs do gateway"""
    try:
        subprocess.run(["docker", "compose", "logs", "-f"], cwd=str(project_root))
    except:
        log_file = project_root / "web_server.log"
        if log_file.exists():
            if os.name == 'nt':
                subprocess.run(["powershell", "Get-Content", str(log_file), "-Tail", "20", "-Wait"])
            else:
                subprocess.run(["tail", "-f", str(log_file)])
        else:
            console.print("[red]Log file not found.[/red]")

if __name__ == "__main__":
    gateway()
