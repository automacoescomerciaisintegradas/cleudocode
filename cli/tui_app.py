import time
import os
import psutil
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.align import Align

def get_docker_status():
    try:
        status = os.popen("docker inspect -f '{{.State.Status}}' cleudocode-app 2>/dev/null").read().strip()
        if status == "running":
            return "[green]Online[/green]"
        elif status:
            return f"[yellow]{status}[/yellow]"
        return "[red]Offline / Não encontrado[/red]"
    except:
        return "[red]Erro[/red]"

def get_agents_count():
    agents_dir = "/root/cleudocode/agents"
    if os.path.exists(agents_dir):
        return str(len([name for name in os.listdir(agents_dir) if name.endswith('.md')]))
    return "0"

def generate_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    return layout

def update_ui(layout):
    # Header
    header_text = Text("Cleudocode TUI Dashboard - Mission Control", style="bold white on blue", justify="center")
    layout["header"].update(Panel(header_text, style="blue"))

    # Left: Sistema e Docker
    mem = psutil.virtual_memory()
    sys_info = f"[bold]Uso de RAM:[/bold] {mem.percent}%\n"
    sys_info += f"[bold]Uso de CPU:[/bold] {psutil.cpu_percent()}%\n\n"
    sys_info += f"[bold]Cleudocode Docker:[/bold] {get_docker_status()}\n"
    layout["left"].update(Panel(sys_info, title="[bold cyan]Status do Sistema[/bold cyan]", border_style="cyan"))

    # Right: Agentes e Gateway
    agents_count = get_agents_count()
    gw_info = f"[bold]Agentes Ativos:[/bold] {agents_count}\n\n"
    gw_info += f"[bold]Gateway OmniRoute:[/bold] [green]Disponível (Porta 20128)[/green]\n"
    layout["right"].update(Panel(gw_info, title="[bold magenta]Serviços[/bold magenta]", border_style="magenta"))

    # Footer
    layout["footer"].update(Panel(Align.center("[dim]Pressione Ctrl+C para sair[/dim]")))

def run_tui():
    console = Console()
    layout = generate_layout()
    with Live(layout, refresh_per_second=2, screen=True) as live:
        try:
            while True:
                update_ui(layout)
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
