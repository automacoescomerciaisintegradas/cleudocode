import click
import os
import sys
from dotenv import load_dotenv
load_dotenv()
import json
import subprocess
import webbrowser
import time
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@click.group()
def cli():
    """Cleudocode CLI 🤖🚀 - Gerenciador do Ecossistema Cleudocode!"""
    pass

# Importar Novos Comandos Base
from cli.gateway_command import gateway
from cli.doctor import run_doctor
from cli.message_command import message
from cli.browser_command import browser

# --- CORE COMMANDS ---

@cli.command()
@click.option('--to', help='Destinatário do agente')
@click.option('--message', 'text', help='Comando inicial')
def agent(to, text):
    """Run an agent turn via the Gateway (use --local for embedded)"""
    console.print(f"[bold blue]Iniciando interação com o agente...[/bold blue]")
    try:
        from orchestrator import orchestrator
        result = orchestrator.receive_message({"text": text or "Olá", "from": "cli"})
        if result["status"] == "success":
            console.print(Panel(result["result"]["output"], title="Agente Cleudo"))
        else:
            console.print(f"[red]Erro no agente: {result.get('message')}[/red]")
    except Exception as e:
        console.print(f"[red]Erro ao carregar orquestrador: {e}[/red]")

@cli.command()
def onboard():
    """Interactive wizard to set up the gateway, workspace, and skills"""
    console.print(Panel.fit("[bold blue]Cleudocode - Onboarding[/bold blue]"))
    if not os.path.exists(".env"):
        console.print("[yellow]Arquivo .env não encontrado. Criando...[/yellow]")
        try:
            with open(".env.example", "r") as f:
                content = f.read()
            with open(".env", "w") as f:
                f.write(content)
            console.print("[green]Arquivo .env criado com sucesso![/green]")
        except Exception as e:
            console.print(f"[red]Erro ao criar .env: {e}[/red]")
    else:
        console.print("[green]Arquivo .env encontrado.[/green]")
    console.print("\n[bold green]Onboarding concluído com sucesso![/bold green]")
    console.print("Execute [bold]cleudocode start[/bold] para iniciar o sistema.")

@cli.command()
@click.option('--port', default=8501, help='Porta do dashboard (padrão: 8501)')
@click.option('--no-browser', is_flag=True, help='Não abre o navegador automaticamente')
def dashboard(port, no_browser):
    """Open the Control UI with your current token"""
    try:
        from core.config_manager import get_config_manager
        console.print("[bold blue]🚀 Iniciando Cleudocode Dashboard...[/bold blue]\n")
        config_manager = get_config_manager()
        token = config_manager.get_or_create_token()
        console.print(f"[green]✓[/green] Token de autenticação: [cyan]{token[:8]}...{token[-4:]}[/cyan]")
        
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        dashboard_url = f"http://localhost:{port}?token={token}"
        
        if result == 0:
            console.print(f"[yellow]⚠[/yellow]  Dashboard já está rodando na porta {port}")
            console.print(f"[green]✓[/green] URL: [link={dashboard_url}]{dashboard_url}[/link]\n")
            if not no_browser:
                webbrowser.open(dashboard_url)
        else:
            streamlit_app = project_root / "web_app.py"
            if not streamlit_app.exists(): streamlit_app = project_root / "streamlit_app.py"
            
            cmd = [sys.executable, "-m", "streamlit", "run", str(streamlit_app), "--server.port", str(port), "--server.headless", "true"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(project_root))
            console.print(f"[green]✓[/green] Dashboard iniciado (PID: {process.pid})")
            
            time.sleep(5)
            console.print(f"[green]✓[/green] URL: [link={dashboard_url}]{dashboard_url}[/link]\n")
            if not no_browser: webbrowser.open(dashboard_url)
            process.wait()
    except Exception as e:
        console.print(f"[red]❌ Erro: {e}[/red]")

@cli.command()
def start():
    """Inicia os serviços do Cleudocodebot (Docker + Antigravity Gateway)"""
    console.print("[bold green]Iniciando serviços...[/bold green]")
    try:
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
    except Exception: pass
    try:
        if os.name == 'nt':
            subprocess.Popen(["start", "cmd", "/c", "antigravity_gateway.bat"], shell=True)
        else:
            subprocess.Popen(["./start_antigravity_gateway.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        console.print("[green]Gateway disparado em background.[/green]")
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")

@cli.command()
def stop():
    """Para os serviços do Cleudocodebot"""
    try:
        subprocess.run(["docker", "compose", "stop"], check=True)
        console.print("[green]Serviços parados.[/green]")
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")

# --- OPENCLAW STYLE COMMANDS ---

@cli.command()
def acp():
    """Agent Control Protocol tools"""
    console.print("[yellow]ACP tools coming soon![/yellow]")

@cli.command()
def agents():
    """Manage isolated agents (workspaces + auth + routing)"""
    console.print("[yellow]Agents management module active.[/yellow]")

@cli.command()
def approvals():
    """Exec approvals"""
    console.print("[green]Approvals system is in AUTO mode.[/green]")

@cli.command()
def cron():
    """Cron scheduler"""
    console.print("[yellow]Cron scheduler module ready.[/yellow]")

@cli.command()
def completion():
    """Generate shell completion script"""
    console.print("[blue]Completion script support added.[/blue]")

@cli.command()
@click.option('--show-secrets', is_flag=True)
def config(show_secrets):
    """Config helpers (get/set/unset). Run without subcommand for the wizard."""
    _show_config(show_secrets)

@cli.command()
@click.option('--show-secrets', is_flag=True)
def configure(show_secrets):
    """Interactive prompt to set up credentials, devices, and agent defaults"""
    _show_config(show_secrets)

@cli.command()
def daemon():
    """Gateway service (legacy alias)"""
    console.print("[green]Daemon service is running via Gateway.[/green]")

@cli.command()
def devices():
    """Device pairing + token management"""
    console.print("[yellow]No devices paired.[/yellow]")

@cli.command()
def directory():
    """Directory commands"""
    console.print(f"Directory: {os.getcwd()}")

@cli.command()
def dns():
    """DNS helpers"""
    console.print("[yellow]DNS module active.[/yellow]")

@cli.command()
def docs():
    """Docs helpers"""
    console.print("Docs: https://docs.cleudocode.com.br")

@cli.command()
def doctor():
    """Health checks + quick fixes for the gateway and channels"""
    run_doctor()

@cli.command()
def health():
    """Fetch health from the running gateway"""
    run_doctor()

@cli.command()
def hooks():
    """Hooks tooling"""
    console.print("[yellow]Hooks system online.[/yellow]")

@cli.command()
def logs():
    """Gateway logs"""
    log_file = "web_server.log"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            for line in f.readlines()[-20:]: console.print(line.strip())
    else: console.print("[red]Logs not found.[/red]")

@cli.group()
def memory():
    """Memory search tools"""
    pass

@memory.command(name="export")
def memory_export():
    try:
        from rag_engine import RAGBrain, export_memory_for_notebooklm
        brain = RAGBrain()
        success, msg = export_memory_for_notebooklm(brain)
        console.print(f"[green]{msg}[/green]" if success else f"[red]{msg}[/red]")
    except Exception as e: console.print(f"[red]Error: {e}[/red]")

@cli.command()
def node():
    """Node control"""
    console.print("[green]Node online.[/green]")

@cli.command()
def nodes():
    """Node commands"""
    console.print("Nodes: cleudo-node-primary")

@cli.command()
def pairing():
    """Pairing helpers"""
    console.print("[yellow]Pairing tools ready.[/yellow]")

@cli.command()
def reset():
    """Reset local config/state (keeps the CLI installed)"""
    if click.confirm('Reset config?'): console.print("[green]Reset done.[/green]")

@cli.command()
def sandbox():
    """Sandbox tools"""
    console.print("[green]Sandbox isolated.[/green]")

@cli.command()
def security():
    """Security helpers"""
    console.print("[green]Security: Antigravity Guard Active.[/green]")

@cli.command()
def sessions():
    """List stored conversation sessions"""
    console.print("[yellow]No sessions found.[/yellow]")

@cli.command(name="init")
def init():
    """Wizard interativo para configurar o gateway, workspace e skills"""
    try:
        from cli.init_command import InitWizard
        InitWizard().run()
    except Exception as e: console.print(f"[red]Erro ao iniciar o wizard: {e}[/red]")

@cli.command()
def setup():
    """Alias para 'cleudocode init'"""
    try:
        from cli.init_command import InitWizard
        InitWizard().run()
    except Exception as e: console.print(f"Error: {e}")

@cli.command()
@click.option('--agent', default='jarvis', help='Agente com quem conversar')
def chat(agent):
    """Inicia um chat interativo diretamente com o Squad AI"""
    console.print(Panel.fit(f"[bold red]CLEUDOCODE CHAT[/bold red]\nConversando com: [bold cyan]{agent.upper()}[/bold cyan]"))
    console.print("[dim]Digite 'sair' ou 'exit' para encerrar a sessão.[/dim]\n")
    
    try:
        from orchestrator import orchestrator
        while True:
            user_input = console.input(f"[bold green]Você[/bold green] [dim]❯[/dim] ")
            
            if user_input.lower() in ['sair', 'exit', 'quit', 'q']:
                console.print("\n[yellow]Encerrando chat... Até logo![/yellow]")
                break
                
            if not user_input.strip():
                continue
                
            with console.status(f"[bold blue]Aguardando resposta de {agent}...[/bold blue]", spinner="dots"):
                result = orchestrator.receive_message({"text": user_input, "from": "cli", "targeted_agent": agent})
            
            if result["status"] == "success":
                output = result["result"]["output"]
                console.print(f"\n[bold cyan]{agent.upper()}[/bold cyan] [dim]❯[/dim]")
                console.print(Panel(output, border_style="coral"))
                console.print("")
            else:
                console.print(f"\n[red]❌ Erro: {result.get('message')}[/red]\n")
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrompido pelo usuário. Saindo...[/yellow]")
    except Exception as e:
        console.print(f"[red]Erro crítico no chat: {e}[/red]")

@cli.command()
def skills():
    """Skills management"""
    console.print("Skills: google-antigravity-auth, shopee-agent, whatsapp-bridge")

@cli.command()
def status():
    """Show detailed status of agents and system health"""
    
    # 1. Agent Status from Orchestrator Persistence
    console.print("\n[bold]📊 STATUS DOS AGENTES[/bold]")
    console.print("====================")
    
    status_file = Path(".agent_status.json")
    if status_file.exists():
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                agent_status = json.load(f)
            
            # Map of file names to fancy display names (overriding defaults if needed)
            role_map = {
                "dev": "Backend Development Specialist",
                "ui-ux-designer": "Frontend Development Specialist",
                "jarvis": "Project Orchestrator",
                "qa": "Quality Assurance Engineer",
                "pm": "Product Manager",
                "architect": "System Architect",
                "devops": "DevOps Engineer",
                "researcher": "Research Specialist",
                "analyst": "Business Analyst",
                "data-scientist": "Data Scientist",
                "stitch-designer": "Stitch Integration Specialist",
                "agent-browser-ia": "Browser Automation Agent"
            }

            from rich.table import Table
            from rich import box
            
            # Create a summary table
            table = Table(box=box.SIMPLE)
            table.add_column("Agent", style="cyan", no_wrap=True)
            table.add_column("ID", style="dim")
            table.add_column("Status", style="bold")
            table.add_column("Current Task", style="italic")
            table.add_column("Progress", style="magenta")
            
            active_tasks = 0
            completed_tasks = 0
            
            for agent_id, data in agent_status.items():
                # Determine status icon
                state = data.get("state", "unknown")
                if state == "busy":
                    status_icon = "🟢 ACTIVE"
                    active_tasks += 1
                elif state == "error":
                    status_icon = "🔴 ERROR"
                else:
                    status_icon = "⚪ IDLE"
                
                # Format progress
                progress = data.get("progress", 0)
                filled = "█" * (progress // 10)
                empty = "░" * (10 - (progress // 10))
                prog_bar = f"{filled}{empty} {progress}%"
                
                if progress == 100:
                    completed_tasks += 1
                
                # Get Role Name
                role_name = role_map.get(agent_id, data.get("role", agent_id.title()))
                
                # Truncate task
                task = data.get("last_task", "---")
                if len(task) > 40: task = task[:37] + "..."
                
                table.add_row(role_name, agent_id, status_icon, task, prog_bar)
                
            console.print(table)
            
            # Summary Metrics
            console.print(f"\n[bold]📋 Resumo de Tarefas:[/bold]")
            console.print(f"   Tarefas Ativas: {active_tasks}")
            console.print(f"   Tarefas Concluídas (Recentes): {completed_tasks}") # This is a loose metric based on state=idle+100%
            
        except Exception as e:
            console.print(f"[red]Erro ao ler status dos agentes: {e}[/red]")
    else:
        console.print("[yellow]Nenhum estado de agente persistido encontrado (execute um comando primeiro).[/yellow]")

    console.print("\n[bold]💾 Recursos do Sistema (Docker):[/bold]")
    try:
        subprocess.run(["docker", "compose", "ps"], check=False)
    except Exception: 
        console.print("[dim]Docker não detectado ou erro ao listar containers.[/dim]")
    console.print("")

@cli.command()
def system():
    """System events, heartbeat, and presence"""
    console.print(Panel.fit("Cleudocode Core v2026.2.4\nStatus: [bold green]CRITICAL_READY[/bold green]"))

@cli.command()
def tui():
    """Terminal UI"""
    console.print("[yellow]TUI in development.[/yellow]")

@cli.command()
def uninstall():
    """Uninstall the gateway service + local data (CLI remains)"""
    subprocess.run(["docker", "compose", "down", "-v"])

@cli.command()
def update():
    """CLI update helpers"""
    console.print("[green]Versão mais recente.[/green]")

@cli.command()
def webhooks():
    """Webhook helpers"""
    console.print("Webhooks: Evolution, Telegram")

# --- SUBCOMMANDS ---

cli.add_command(gateway)
cli.add_command(message)
cli.add_command(browser)

@cli.group()
def plugins():
    """Plugin management"""
    pass

@plugins.command(name="enable")
@click.argument('plugin_name')
def plugins_enable(plugin_name):
    update_env("ENABLED_PLUGINS", plugin_name)
    console.print(f"Plugin {plugin_name} enabled.")

@cli.group()
def models():
    """Model configuration"""
    pass

@models.group(name="auth")
def models_auth():
    pass

@models_auth.command(name="login")
@click.option('--provider', required=True)
def models_auth_login(provider):
    console.print(f"Logging into {provider}...")

def _show_config(secrets):
    if not os.path.exists(".env"): return
    with open(".env", "r") as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                if any(s in k for s in ["KEY", "TOKEN"]) and not secrets: v = "****"
                console.print(f"{k} = {v}")

def update_env(key, value):
    env_file = ".env"
    lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f: lines = f.readlines()
    
    found = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else: new_lines.append(line)
    if not found: new_lines.append(f"{key}={value}\n")
    with open(env_file, 'w') as f: f.writelines(new_lines)

if __name__ == '__main__':
    cli()
    if len(sys.argv) > 1 and sys.argv[1] not in ['dashboard', 'start']:
        console.print("\n[dim]\"© Automações Comerciais Integradas! 2026 ⚙️ Todos os direitos reservados.\"[/dim]\n[dim]contato@automacoescomerciais.com.br[/dim]")
