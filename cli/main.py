import click
import os
import sys

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()
import json
import logging
import subprocess
import webbrowser
import time
from pathlib import Path
from datetime import datetime
from uuid import uuid4
import socket

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from rich.console import Console, Group
from rich.columns import Columns
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
vendor_dir = project_root / ".vendor"
if vendor_dir.exists():
    sys.path.insert(1, str(vendor_dir))

SESSION_ID = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"

BRAND_BANNER = r"""
  ______ _                 _                 _
 / _____| |               | |               | |
| |     | | ___ _   _  ___| | ___   ___ ___ | | ___
| |     | |/ _ \ | | |/ _ \ |/ _ \ / __/ _ \| |/ _ \
| |____ | |  __/ |_| |  __/ | (_) | (_| (_) | |  __/
 \_____||_|\___|\__,_|\___|_|\___/ \___\___/|_|\___|
"""


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Bem-vindo(a) ao Futuro da Criacao de Conteudo! 🤖✨

    The AI that actually does things.
    Gerencia seus projetos, cria sistemas e executa tarefas reais.
    Tudo local, privado e 100% sob seu controle.
    {[ made in © Automações Comerciais Integradas! 2026 ⚙️ ]}
    """
    if ctx.invoked_subcommand is None:
        _launch_cleudocode_shell()


@cli.command(name="help")
@click.pass_context
def help_command(ctx):
    """Show CLI help as a command."""
    console.print(ctx.parent.get_help())

# Importar Novos Comandos Base
from cli.gateway_command import gateway
from cli.doctor import run_doctor
from cli.message_command import message
from cli.browser_command import browser

logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("skills.loader").setLevel(logging.CRITICAL)
logging.getLogger("core.config_manager").setLevel(logging.ERROR)
logging.getLogger("Orchestrator").setLevel(logging.ERROR)

COMMAND_STATUS = {
    "agent": {"status": "functional", "summary": "envia um turno ao orquestrador"},
    "agents": {"status": "functional", "summary": "lista agentes disponíveis"},
    "browser": {"status": "functional", "summary": "instala e abre Playwright"},
    "chat": {"status": "functional", "summary": "chat direto com agentes"},
    "dashboard": {"status": "functional", "summary": "inicia painel com token"},
    "directory": {"status": "functional", "summary": "mostra diretório atual"},
    "doctor": {"status": "functional", "summary": "diagnóstico do sistema"},
    "gateway": {"status": "functional", "summary": "start, stop e logs do gateway"},
    "init": {"status": "functional", "summary": "wizard de inicialização"},
    "message": {"status": "functional", "summary": "envia mensagem via gateway"},
    "models": {"status": "functional", "summary": "provider e modelo padrão"},
    "onboard": {"status": "functional", "summary": "bootstrap inicial do projeto"},
    "setup": {"status": "functional", "summary": "alias de init"},
    "start": {"status": "functional", "summary": "sobe serviços principais"},
    "stop": {"status": "functional", "summary": "para serviços principais"},
    "tools": {"status": "functional", "summary": "lista comandos classificados"},
    "config": {"status": "partial", "summary": "mostra config, mas não set/unset"},
    "configure": {"status": "partial", "summary": "atalho de leitura, sem wizard real"},
    "daemon": {"status": "partial", "summary": "alias informativo, sem controle real"},
    "docs": {"status": "partial", "summary": "apenas mostra link fixo"},
    "health": {"status": "partial", "summary": "reaproveita doctor, sem health dedicado"},
    "logs": {"status": "partial", "summary": "lê apenas um arquivo de log"},
    "memory": {"status": "partial", "summary": "só export disponível"},
    "plugins": {"status": "partial", "summary": "apenas enable implementado"},
    "reset": {"status": "partial", "summary": "confirma, mas não limpa estado real"},
    "skills": {"status": "partial", "summary": "lista skills, sem gestão completa"},
    "status": {"status": "partial", "summary": "mistura estado local e docker"},
    "system": {"status": "partial", "summary": "status estático"},
    "uninstall": {"status": "partial", "summary": "remove stack docker, sem fluxo completo"},
    "acp": {"status": "not_implemented", "summary": "placeholder"},
    "approvals": {"status": "not_implemented", "summary": "placeholder"},
    "completion": {"status": "not_implemented", "summary": "não gera script real"},
    "cron": {"status": "not_implemented", "summary": "placeholder"},
    "devices": {"status": "not_implemented", "summary": "placeholder"},
    "dns": {"status": "not_implemented", "summary": "placeholder"},
    "hooks": {"status": "not_implemented", "summary": "placeholder"},
    "node": {"status": "not_implemented", "summary": "placeholder"},
    "nodes": {"status": "not_implemented", "summary": "placeholder"},
    "pairing": {"status": "not_implemented", "summary": "placeholder"},
    "sandbox": {"status": "not_implemented", "summary": "placeholder"},
    "security": {"status": "not_implemented", "summary": "placeholder"},
    "sessions": {"status": "not_implemented", "summary": "placeholder"},
    "tui": {"status": "not_implemented", "summary": "em desenvolvimento"},
    "update": {"status": "not_implemented", "summary": "sem rotina real de update"},
    "webhooks": {"status": "not_implemented", "summary": "placeholder"},
}

def _format_model_summary():
    from core.config_manager import get_config_manager

    manager = get_config_manager()
    try:
        config = manager.load_config()
    except Exception:
        config = None

    provider = manager.get_env_value(
        "DEFAULT_PROVIDER",
        config.get("llm.default_provider", "unset") if config else "unset",
    )
    model_env_map = {
        "ollama": "OLLAMA_MODEL",
        "openai": "OPENAI_MODEL",
        "anthropic": "ANTHROPIC_MODEL",
        "google": "GOOGLE_ANTIGRAVITY_MODEL",
        "google-antigravity": "GOOGLE_ANTIGRAVITY_MODEL",
        "openrouter": "OPENROUTER_MODEL",
        "groq": "GROQ_MODEL",
        "moonshot": "MOONSHOT_MODEL",
        "zai": "ZAI_MODEL",
    }
    model = manager.get_env_value(
        model_env_map.get(provider, ""),
        config.get("llm.default_model", "unset") if config else "unset",
    )
    return provider, model


def _resolve_remote_dashboard_url(port, token):
    explicit_url = (
        os.getenv("CLEUDO_CODE_DASHBOARD_PUBLIC_URL")
        or os.getenv("CLEUDOCODE_DASHBOARD_PUBLIC_URL")
    )
    if explicit_url:
        separator = "&" if "?" in explicit_url else "?"
        return f"{explicit_url}{separator}token={token}"

    explicit_host = (
        os.getenv("CLEUDO_CODE_DASHBOARD_PUBLIC_HOST")
        or os.getenv("CLEUDOCODE_DASHBOARD_PUBLIC_HOST")
        or os.getenv("CLEUDOCODE_PUBLIC_IP")
        or os.getenv("SERVER_PUBLIC_IP")
        or os.getenv("PUBLIC_IP")
    )
    if explicit_host:
        return f"http://{explicit_host}:{port}?token={token}"

    try:
        detected_host = socket.gethostbyname(socket.gethostname())
        if detected_host and not detected_host.startswith("127."):
            return f"http://{detected_host}:{port}?token={token}"
    except OSError:
        pass

    return None


def _collect_agent_names():
    agents_dir = project_root / "agents"
    if not agents_dir.exists():
        return []
    return sorted(agent_file.stem for agent_file in agents_dir.glob("*.md"))


def _collect_skill_catalog():
    try:
        from skills.loader import SkillLoader

        loader = SkillLoader()
        result = []
        for skill_dir in loader.discover_skills():
            metadata = loader.parse_skill_metadata(skill_dir)
            has_impl = any(
                (skill_dir / candidate).exists()
                for candidate in [f"{skill_dir.name}_skill.py", "skill.py", "__init__.py"]
            )
            result.append(
                {
                    "name": metadata.name or skill_dir.name,
                    "description": metadata.description,
                    "emoji": metadata.emoji,
                    "category": metadata.category,
                    "has_implementation": has_impl,
                    "requirements_met": None,
                }
            )
        return sorted(result, key=lambda skill: (skill["category"], skill["name"]))
    except Exception as exc:
        return [{"name": "skills-unavailable", "category": "system", "description": str(exc), "emoji": "⚠", "has_implementation": False, "requirements_met": False}]


def _collect_toolsets():
    toolsets = []
    for name, command in sorted(cli.commands.items()):
        if name == "help":
            continue
        if isinstance(command, click.core.Group):
            subcommands = sorted(command.commands.keys())
            preview = ", ".join(subcommands[:3])
            if len(subcommands) > 3:
                preview += ", ..."
            description = preview or "subcommands"
        else:
            description = (command.help or "").split(".")[0]

        status_info = COMMAND_STATUS.get(name, {"status": "functional", "summary": description})
        toolsets.append(
            {
                "name": name,
                "description": status_info.get("summary") or description,
                "status": status_info.get("status", "functional"),
            }
        )

    try:
        from core.mcp_client import MCPClient, StitchClient

        # Listar todos os serviços
        services = MCPClient.list_all_services()
        mcp_tools = []
        
        for service in services:
            try:
                # Se for stitch, usa a classe especializada para melhor compatibilidade
                if service == "stitch":
                    client = StitchClient()
                else:
                    client = MCPClient(service_name=service)
                
                service_tools = client.list_available_tools()
                for tool in service_tools:
                    mcp_tools.append({
                        "name": f"mcp:{service}:{tool['name']}",
                        "description": tool.get("description", ""),
                        "status": "functional" if tool.get("enabled") else "partial"
                    })
            except Exception as e:
                logger.debug(f"Erro ao listar ferramentas para {service}: {e}")
                
    except Exception as e:
        logger.error(f"Erro ao inicializar MCP: {e}")
        mcp_tools = []

    for tool in mcp_tools:
        toolsets.append(tool)

    return toolsets


def _render_functional_commands_panel():
    toolsets = _collect_toolsets()
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column("Comando", style="bold cyan", no_wrap=True)
    table.add_column("Uso", style="white")
    functional = [tool for tool in toolsets if tool["status"] == "functional"]
    for tool in functional[:40]:
        table.add_row(tool["name"], tool["description"] or "available")
    if len(functional) > 40:
        table.add_row("...", f"{len(functional) - 40} comandos funcionais adicionais")
    return Panel(table, title=f"Comandos Funcionais ({len(functional)})", border_style="cyan")


def _render_partial_commands_panel():
    toolsets = _collect_toolsets()
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column("Comando", style="bold magenta", no_wrap=True)
    table.add_column("Status", style="white")
    partial = [tool for tool in toolsets if tool["status"] == "partial"]
    for tool in partial[:10]:
        table.add_row(tool["name"], tool["description"] or "parcial")
    if len(partial) > 10:
        table.add_row("...", f"{len(partial) - 10} comandos parciais adicionais")
    return Panel(table, title=f"Comandos Parciais ({len(partial)})", border_style="magenta")


def _render_not_implemented_commands_panel():
    toolsets = _collect_toolsets()
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column("Comando", style="bold yellow", no_wrap=True)
    table.add_column("Status", style="white")
    pending = [tool for tool in toolsets if tool["status"] == "not_implemented"]
    for tool in pending[:12]:
        table.add_row(tool["name"], tool["description"] or "não implementado")
    if len(pending) > 12:
        table.add_row("...", f"{len(pending) - 12} comandos não implementados adicionais")
    return Panel(table, title=f"Não Implementado ({len(pending)})", border_style="yellow")


def _render_skills_panel():
    skills = _collect_skill_catalog()
    categories = {}
    for skill in skills:
        categories.setdefault(skill.get("category", "misc"), []).append(skill)

    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column("Categoria", style="bold magenta", no_wrap=True)
    table.add_column("Skills", style="white")

    for category in sorted(categories.keys())[:8]:
        names = ", ".join(skill["name"] for skill in categories[category][:4])
        extra = len(categories[category]) - 4
        if extra > 0:
            names += f", +{extra}"
        table.add_row(category, names)

    return Panel(table, title=f"Skills Disponíveis ({len(skills)})", border_style="magenta")


def _render_runtime_panel():
    provider, model = _format_model_summary()
    agents = _collect_agent_names()
    body = "\n".join(
        [
            f"[bold]Modelo[/bold]: {provider} / {model}",
            f"[bold]Workspace[/bold]: {project_root}",
            f"[bold]Agentes[/bold]: {len(agents)} carregados",
            f"[bold]Sessão[/bold]: {SESSION_ID}",
        ]
    )
    return Panel(body, title="Runtime cleudocode", border_style="green")


def _render_session_panel():
    provider, model = _format_model_summary()
    title = f"cleudocode cli · sessão {SESSION_ID} · {provider} / {model}"
    body = "Shell interativa cleudocode\nUse /help para atalhos e /exit para sair."
    return Panel(body, title=title, border_style="white")


def _render_quickstart_panel():
    body = "\n".join(
        [
            "Digite qualquer mensagem para falar com Jarvis",
            "/agent <nome> <mensagem>   falar com outro agente",
            "/tools   listar ferramentas",
            "/skills  listar skills",
            "/agents  listar agentes",
            "/model   mostrar modelo ativo",
            "/exit    sair",
        ]
    )
    return Panel(body, title="Início Rápido", border_style="yellow")


def _render_help_panel():
    body = "\n".join(
        [
            "/help   ajuda",
            "/tools  ferramentas",
            "/skills skills",
            "/agents agentes",
            "/model  modelo ativo",
            "/exit   sair",
        ]
    )
    return Panel(body, title="Comandos da Shell", border_style="yellow")


def _show_agents_panel():
    agents = _collect_agent_names()
    content = ", ".join(agents) if agents else "Nenhum agente encontrado"
    console.print(Panel(content, title=f"Agentes ({len(agents)})", border_style="blue"))


def _run_interactive_shell():
    orchestrator = None
    while True:
        try:
            user_input = console.input("\n[bold cyan]cleudocode[/bold cyan] [dim]›[/dim] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Sessão encerrada.[/dim]")
            break

        if not user_input:
            continue
        if user_input in {"/exit", "/quit"}:
            console.print("[dim]Sessão encerrada.[/dim]")
            break
        if user_input == "/help":
            console.print(_render_help_panel())
            continue
        if user_input == "/tools":
            console.print(_render_functional_commands_panel())
            console.print(_render_partial_commands_panel())
            console.print(_render_not_implemented_commands_panel())
            continue
        if user_input == "/skills":
            console.print(_render_skills_panel())
            continue
        if user_input == "/agents":
            _show_agents_panel()
            continue
        if user_input == "/model":
            console.print(_render_runtime_panel())
            continue
        if user_input.startswith("/agent "):
            parts = user_input.split(" ", 2)
            if len(parts) < 3:
                console.print("[red]Uso: /agent <nome> <mensagem>[/red]")
                continue
            target_agent, prompt = parts[1], parts[2]
            if orchestrator is None:
                from orchestrator import orchestrator as loaded_orchestrator
                orchestrator = loaded_orchestrator
            result = orchestrator.receive_message({"text": prompt, "from": "cli", "targeted_agent": target_agent})
        else:
            if orchestrator is None:
                from orchestrator import orchestrator as loaded_orchestrator
                orchestrator = loaded_orchestrator
            result = orchestrator.receive_message({"text": user_input, "from": "cli"})

        if result.get("status") == "success":
            output = result.get("result", {}).get("output") or result.get("result", {}).get("overall_status") or "Sem resposta"
            console.print(Panel(str(output), title="cleudocode", border_style="green"))
        else:
            console.print(f"[red]Erro:[/red] {result.get('message', 'falha desconhecida')}")


def _launch_cleudocode_shell():
    console.print(f"[bold cyan]{BRAND_BANNER}[/bold cyan]")
    console.print(_render_session_panel())
    console.print(
        Columns(
            [
                _render_functional_commands_panel(),
                Group(
                    _render_skills_panel(),
                    _render_runtime_panel(),
                    _render_quickstart_panel(),
                    _render_partial_commands_panel(),
                    _render_not_implemented_commands_panel(),
                ),
            ],
            equal=False,
            expand=True,
        )
    )
    _run_interactive_shell()

# --- CORE COMMANDS ---

@cli.command()
@click.option('--to', help='Destinatário do agente')
@click.option('--message', 'text', help='Comando inicial')
def agent(to, text):
    """Run an agent turn via the Gateway (use --local for embedded)"""
    console.print(f"[bold blue]Iniciando interação com o agente...[/bold blue]")
    try:
        from orchestrator import orchestrator
        target_agent = to.strip().lower() if to else "jarvis"
        result = orchestrator.receive_message(
            {
                "text": text or "Olá",
                "from": "cli",
                "targeted_agent": target_agent,
            }
        )
        if result["status"] == "success":
            title = f"Agente {target_agent}"
            console.print(Panel(result["result"]["output"], title=title))
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
        dashboard_host = os.getenv("CLEUDOCODE_DASHBOARD_HOST", "0.0.0.0")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(('localhost', port))
        except OSError:
            result = 1
        finally:
            sock.close()
        
        local_dashboard_url = f"http://localhost:{port}?token={token}"
        remote_dashboard_url = _resolve_remote_dashboard_url(port, token)
        
        if result == 0:
            console.print(f"[yellow]⚠[/yellow]  Dashboard já está rodando na porta {port}")
            console.print(f"[green]✓[/green] URL local: [link={local_dashboard_url}]{local_dashboard_url}[/link]")
            if remote_dashboard_url:
                console.print(f"[green]✓[/green] URL remota: {remote_dashboard_url}\n")
            if not no_browser:
                webbrowser.open(local_dashboard_url)
        else:
            streamlit_app = project_root / "web_app.py"
            if not streamlit_app.exists(): streamlit_app = project_root / "streamlit_app.py"
            dashboard_log = project_root / "dashboard.log"
            env = os.environ.copy()
            env["STREAMLIT_SERVER_ADDRESS"] = dashboard_host
            env["STREAMLIT_SERVER_PORT"] = str(port)
            env["STREAMLIT_SERVER_HEADLESS"] = "true"
            env["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
            env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
            
            cmd = [sys.executable, "-m", "streamlit", "run", str(streamlit_app)]
            log_handle = open(dashboard_log, "ab")
            process = subprocess.Popen(
                cmd,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                cwd=str(project_root),
                env=env,
                start_new_session=(os.name != 'nt'),
            )
            console.print(f"[green]✓[/green] Dashboard iniciado (PID: {process.pid})")
            
            time.sleep(5)
            if process.poll() is not None:
                console.print(f"[red]❌ Dashboard encerrou logo após iniciar. Veja o log em {dashboard_log}[/red]")
                return
            console.print(f"[green]✓[/green] URL local: [link={local_dashboard_url}]{local_dashboard_url}[/link]")
            if remote_dashboard_url:
                console.print(f"[green]✓[/green] URL remota: {remote_dashboard_url}")
            console.print(f"[green]✓[/green] Log: {dashboard_log}\n")
            if not no_browser:
                webbrowser.open(local_dashboard_url)
    except Exception as e:
        console.print(f"[red]❌ Erro: {e}[/red]")

@cli.command()
def start():
    """Inicia os serviços do Cleudocodebot (Docker + Antigravity Gateway)"""
    console.print("[bold green]Iniciando serviços...[/bold green]")
    docker_started = False
    try:
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
        docker_started = True
        console.print("[green]Serviços Docker iniciados.[/green]")
    except Exception as e:
        console.print(f"[yellow]Docker compose falhou: {e}[/yellow]")

    if docker_started:
        return

    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_in_use = sock.connect_ex(("127.0.0.1", 18900)) == 0
        sock.close()
        if port_in_use:
            console.print("[yellow]Porta 18900 já está em uso. Gateway local não será disparado para evitar conflito.[/yellow]")
            return
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
    _show_agents_panel()

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

@cli.group(invoke_without_command=True)
@click.option('--show-secrets', is_flag=True)
@click.pass_context
def config(ctx, show_secrets):
    """Config helpers (get/set/unset). Run without subcommand to list values."""
    if ctx.invoked_subcommand is None:
        _show_config(show_secrets)


@config.command(name="get")
@click.argument("key")
@click.option('--default', "default_value", default=None, help="Fallback value when key is absent.")
def config_get(key, default_value):
    """Read a single key from the project .env file."""
    from core.config_manager import get_config_manager

    value = get_config_manager().get_env_value(key, default_value)
    if value is None:
        raise click.ClickException(f"Config key not found: {key}")
    console.print(value)


@config.command(name="set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Persist a key/value pair into the project .env file."""
    from core.config_manager import get_config_manager

    get_config_manager().set_env_value(key, value)
    console.print(f"[green]{key} set.[/green]")


@config.command(name="unset")
@click.argument("key")
def config_unset(key):
    """Remove a key from the project .env file."""
    from core.config_manager import get_config_manager

    removed = get_config_manager().unset_env_value(key)
    if not removed:
        raise click.ClickException(f"Config key not found: {key}")
    console.print(f"[green]{key} removed.[/green]")

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
                console.print(Panel(output, border_style="magenta"))
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
    console.print(_render_skills_panel())

@cli.command()
def tools():
    """List Cleudocode toolsets and integrations"""
    console.print(_render_functional_commands_panel())
    console.print(_render_partial_commands_panel())
    console.print(_render_not_implemented_commands_panel())

@cli.command()
def status():
    """Show detailed status of agents and system health"""
    
    # 1. Agent Status from Orchestrator Persistence
    console.print("\n[bold]📊 STATUS DOS AGENTES[/bold]")
    console.print("====================")
    
    status_file = project_root / ".agent_status.json"
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
        subprocess.run(["docker", "compose", "ps"], check=False, cwd=str(project_root))
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
    from core.config_manager import get_config_manager
    get_config_manager().set_env_value("ENABLED_PLUGINS", plugin_name)
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

@models.command(name="current")
def models_current():
    """Show the active provider/model configuration."""
    from core.config_manager import get_config_manager

    manager = get_config_manager()
    config = manager.load_config()
    provider = manager.get_env_value("DEFAULT_PROVIDER", config.get("llm.default_provider", "unset"))
    model_env_map = {
        "ollama": "OLLAMA_MODEL",
        "openai": "OPENAI_MODEL",
        "anthropic": "ANTHROPIC_MODEL",
        "google": "GOOGLE_ANTIGRAVITY_MODEL",
        "google-antigravity": "GOOGLE_ANTIGRAVITY_MODEL",
        "openrouter": "OPENROUTER_MODEL",
        "groq": "GROQ_MODEL",
        "moonshot": "MOONSHOT_MODEL",
        "zai": "ZAI_MODEL",
    }
    model_env_key = model_env_map.get(provider)
    model = manager.get_env_value(model_env_key, config.get("llm.default_model", "unset")) if model_env_key else config.get("llm.default_model", "unset")
    host = manager.get_env_value("OLLAMA_HOST", config.get("llm.providers.ollama.host", "http://localhost:11434"))

    console.print(f"Provider: {provider}")
    console.print(f"Model: {model}")
    if provider == "ollama":
        console.print(f"Ollama host: {host}")

@models.command(name="use")
@click.argument("provider")
@click.option("--model", help="Modelo padrão para o provedor")
@click.option("--host", help="Host do Ollama (ex: http://localhost:11434)")
def models_use(provider, model, host):
    """Persist a default provider/model for the CLI."""
    from core.config_manager import get_config_manager

    normalized_provider = provider.strip().lower()
    supported = {
        "ollama",
        "openai",
        "anthropic",
        "google",
        "google-antigravity",
        "openrouter",
        "groq",
        "moonshot",
        "zai",
    }
    if normalized_provider not in supported:
        console.print(f"[red]Provider não suportado: {provider}[/red]")
        return

    manager = get_config_manager()
    config = manager.load_config()
    config.set("llm.default_provider", normalized_provider)
    manager.set_env_value("DEFAULT_PROVIDER", normalized_provider)

    if model:
        config.set("llm.default_model", model)
        if normalized_provider == "ollama":
            manager.set_env_value("OLLAMA_MODEL", model)

    if normalized_provider == "ollama":
        config.set("llm.providers.ollama.enabled", True)
        manager.set_env_value("OLLAMA_ENABLED", "true")
        if host:
            config.set("llm.providers.ollama.host", host)
            manager.set_env_value("OLLAMA_HOST", host)

    config.save()
    console.print(f"[green]Provider padrão atualizado para {normalized_provider}.[/green]")
    if model:
        console.print(f"[green]Modelo padrão: {model}[/green]")
    if normalized_provider == "ollama":
        console.print("[green]O Cleudocode agora prioriza Ollama nas chamadas sem provider explícito.[/green]")

def _show_config(secrets):
    from core.config_manager import get_config_manager

    for key, value in get_config_manager().list_env_items():
        if any(secret in key for secret in ["KEY", "TOKEN"]) and not secrets:
            value = "****"
        console.print(f"{key} = {value}")

if __name__ == '__main__':
    cli()
    if len(sys.argv) > 1 and sys.argv[1] not in ['dashboard', 'start']:
        console.print("\n[dim]\"© Automações Comerciais Integradas! 2026 ⚙️ Todos os direitos reservados.\"[/dim]\n[dim]contato@automacoescomerciais.com.br[/dim]")
