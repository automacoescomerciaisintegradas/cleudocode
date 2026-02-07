import click
import os
import sys
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
    """Cleudocode CLI - Gerenciador do Assistente"""
    pass

@cli.command()
@click.option('--no-install-daemon', is_flag=True, help='Pula instalação do Daemon')
@click.option('--force', is_flag=True, help='Força reconfiguração')
def onboard(no_install_daemon, force):
    """Executa o assistente de configuração inicial"""
    console.print(Panel.fit("[bold blue]Cleudocode - Onboarding[/bold blue]"))
    
    # 1. Verificar .env
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

    # 2. Verificar Ollama
    console.print("\n[bold]Verificando Conexão com Ollama...[/bold]")
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        # Tenta conexão simples usando curl (já que requests pode não estar no env do CLI puro)
        # Mas aqui estamos python, vamos tentar requests se der
        import requests
        try:
            resp = requests.get(f"{ollama_host}/api/tags", timeout=5)
            if resp.status_code == 200:
                console.print(f"[green]Conectado ao Ollama em {ollama_host}[/green]")
            else:
                console.print(f"[red]Ollama respondeu com erro: {resp.status_code}[/red]")
        except:
             console.print(f"[red]Falha ao conectar no Ollama ({ollama_host}). Verifique se está rodando.[/red]")
    except ImportError:
        console.print("[yellow]Requests não instalado, pulando teste de rede.[/yellow]")

    console.print("\n[bold green]Onboarding concluído com sucesso![/bold green]")
    console.print("Execute [bold]cleudocode start[/bold] para iniciar o sistema.")

@cli.command()
def start():
    """Inicia os serviços do Cleudocodebot (Docker + Antigravity Gateway)"""
    console.print("[bold green]Iniciando serviços...[/bold green]")
    
    # 1. Docker Compose
    try:
        console.print("[blue]Levantando containers Docker...[/blue]")
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
    except Exception as e:
        console.print(f"[yellow]Aviso: Docker falhou ou não presente ({e}). Continuando com serviços locais...[/yellow]")
    
    # 2. Antigravity Gateway
    try:
        console.print("[blue]Iniciando Antigravity Gateway...[/blue]")
        if os.name == 'nt':
            subprocess.Popen(["start", "cmd", "/c", "antigravity_gateway.bat"], shell=True)
        else:
            # No Linux/WSL, iniciamos em background
            subprocess.Popen(["./start_antigravity_gateway.sh"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
        console.print("[green]Antigravity Gateway disparado em background.[/green]")
    except Exception as e:
        console.print(f"[red]Erro ao iniciar Gateway: {e}[/red]")

    console.print("\n[bold green]✅ Todos os serviços foram disparados![/bold green]")
    console.print("Acesse a interface em: [bold]http://localhost:18900[/bold]")

@cli.command()
@click.option('--port', default=8501, help='Porta do dashboard (padrão: 8501)')
@click.option('--no-browser', is_flag=True, help='Não abre o navegador automaticamente')
def dashboard(port, no_browser):
    """Abre o Dashboard Web com autenticação automática"""
    try:
        # Import config manager
        from core.config_manager import get_config_manager
        
        console.print("[bold blue]🚀 Iniciando Cleudocode Dashboard...[/bold blue]\n")
        
        # Get or create token
        config_manager = get_config_manager()
        token = config_manager.get_or_create_token()
        
        console.print(f"[green]✓[/green] Token de autenticação: [cyan]{token[:8]}...{token[-4:]}[/cyan]")
        
        # Check if dashboard is already running
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        dashboard_url = f"http://localhost:{port}?token={token}"
        
        if result == 0:
            # Dashboard already running
            console.print(f"[yellow]⚠[/yellow]  Dashboard já está rodando na porta {port}")
            console.print(f"[green]✓[/green] URL: [link={dashboard_url}]{dashboard_url}[/link]\n")
            
            if not no_browser:
                console.print("[blue]🌐 Abrindo navegador...[/blue]")
                webbrowser.open(dashboard_url)
        else:
            # Start dashboard
            console.print(f"[blue]📊 Iniciando dashboard na porta {port}...[/blue]")
            
            # Find streamlit app
            streamlit_app = project_root / "web_app.py"
            if not streamlit_app.exists():
                streamlit_app = project_root / "streamlit_app.py"
            
            if not streamlit_app.exists():
                console.print("[red]❌ Arquivo do dashboard não encontrado![/red]")
                console.print("[yellow]Procurado em:[/yellow]")
                console.print(f"  - {project_root / 'web_app.py'}")
                console.print(f"  - {project_root / 'streamlit_app.py'}")
                return
            
            # Start streamlit in background
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                str(streamlit_app),
                "--server.port", str(port),
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(project_root)
            )
            
            console.print(f"[green]✓[/green] Dashboard iniciado (PID: {process.pid})")
            
            # Wait for dashboard to be ready
            console.print("[blue]⏳ Aguardando dashboard ficar pronto...[/blue]")
            
            max_attempts = 30
            for attempt in range(max_attempts):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    console.print(f"[green]✓[/green] Dashboard pronto!\n")
                    break
                
                time.sleep(1)
            else:
                console.print("[yellow]⚠[/yellow]  Dashboard demorou para iniciar, mas pode estar funcionando...\n")
            
            console.print(f"[green]✓[/green] URL: [link={dashboard_url}]{dashboard_url}[/link]\n")
            
            if not no_browser:
                console.print("[blue]🌐 Abrindo navegador...[/blue]")
                time.sleep(2)  # Give it a bit more time
                webbrowser.open(dashboard_url)
            
            console.print("\n[bold green]✅ Dashboard rodando![/bold green]")
            console.print("[dim]Pressione Ctrl+C para parar o dashboard[/dim]")
            
            try:
                process.wait()
            except KeyboardInterrupt:
                console.print("\n[yellow]Parando dashboard...[/yellow]")
                process.terminate()
                process.wait()
                console.print("[green]Dashboard parado.[/green]")
    
    except ImportError as e:
        console.print(f"[red]❌ Erro ao importar módulos: {e}[/red]")
        console.print("[yellow]Certifique-se de que está no diretório do projeto.[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Erro ao iniciar dashboard: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")

@cli.command()
def stop():
    """Para os serviços do Cleudocodebot"""
    console.print("[bold yellow]Parando serviços...[/bold yellow]")
    try:
        subprocess.run(["docker", "compose", "stop", "cleudocode-gateway"], check=True)
        console.print("[green]Serviços parados.[/green]")
    except Exception as e:
        console.print(f"[red]Erro ao parar serviços: {e}[/red]")

@cli.command()
def status():
    """Verifica o status dos serviços"""
    try:
        result = subprocess.run(["docker", "compose", "ps"], capture_output=True, text=True)
        console.print(result.stdout)
    except Exception as e:
        console.print(f"[red]Erro ao verificar status: {e}[/red]")

@cli.command()
@click.option('--show-secrets', is_flag=True, help='Mostra valores ocultos (CUIDADO)')
def config(show_secrets):
    """Exibe a configuração atual (.env)"""
    _show_config(show_secrets)

@cli.command(name="configure")
@click.option('--show-secrets', is_flag=True, help='Mostra valores ocultos (CUIDADO)')
def configure(show_secrets):
    """Alias para o comando config"""
    _show_config(show_secrets)

def _show_config(show_secrets):
    """Função interna para exibir configuração"""
    console.print(Panel.fit("[bold]Configuração Atual[/bold]"))
    if not os.path.exists(".env"):
        console.print("[red]Arquivo .env não encontrado![/red]")
        return
        
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            
            # Mascarar segredos
            is_secret = any(s in key for s in ["TOKEN", "KEY", "PASSWORD", "SECRET"])
            display_value = value
            if is_secret and not show_secrets:
                display_value = f"{value[:4]}...******"
                
            console.print(f"[blue]{key}[/blue] = {display_value}")

@cli.group()
def channels():
    """Gerencia canais de comunicação (Telegram, Discord...)"""
    pass

@channels.command(name="add")
@click.option('--channel', required=True, type=click.Choice(['telegram', 'discord']), help='Tipo do canal')
@click.option('--token', required=True, help='Token de acesso do canal')
def add_channel(channel, token):
    """Adiciona um novo canal"""
    console.print(f"Configurando canal [bold]{channel}[/bold]...")
    
    # Atualiza .env
    env_file = ".env"
    key = ""
    if channel == 'telegram':
        key = "TELEGRAM_BOT_TOKEN"
    elif channel == 'discord':
        key = "DISCORD_BOT_TOKEN"
        
    try:
        # Le lines
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        found = False
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={token}\n")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f"\n{key}={token}\n")
            
        with open(env_file, 'w') as f:
            f.writelines(new_lines)
            
        console.print(f"[green]Token do {channel} salvo com sucesso no .env![/green]")
        console.print("Reinicie o gateway para aplicar: [bold]docker compose restart cleudocode-gateway[/bold]")
        
    except Exception as e:
        console.print(f"[red]Erro ao salvar configuração: {e}[/red]")

@cli.group()
def memory():
    """Gerencia a memória RAG do assistente"""
    pass

@memory.command(name="export")
def export_memory():
    """Exporta memória para importar no NotebookLM"""
    console.print("[bold]Iniciando exportação da memória...[/bold]")
    try:
        # Importa apenas quando necessário para evitar dependências pesadas no startup
        sys.path.append(os.getcwd())
        from rag_engine import RAGBrain, export_memory_for_notebooklm
        
        brain = RAGBrain()
        success, msg = export_memory_for_notebooklm(brain)
        
        if success:
            console.print(f"[green]✅ {msg}[/green]")
        else:
            console.print(f"[red]❌ {msg}[/red]")
            
    except Exception as e:
        console.print(f"[red]Erro fatal na exportação: {e}[/red]")

@cli.group()
def plugins():
    """Gerencia plugins do sistema"""
    pass

@plugins.command(name="enable")
@click.argument('plugin_name')
def plugins_enable(plugin_name):
    """Ativa um plugin específico"""
    console.print(f"[bold green]Ativando plugin: {plugin_name}[/bold green]")
    plugins_list = os.getenv("ENABLED_PLUGINS", "")
    if plugin_name not in plugins_list:
        new_list = f"{plugins_list},{plugin_name}".strip(",")
        update_env("ENABLED_PLUGINS", new_list)
        console.print(f"[green]Plugin {plugin_name} ativado com sucesso![/green]")
    else:
        console.print(f"[yellow]Plugin {plugin_name} já está ativado.[/yellow]")

@cli.group()
def models():
    """Gerencia modelos e provedores de IA"""
    pass

@models.group(name="auth")
def models_auth():
    """Gerencia autenticação de provedores"""
    pass

@models_auth.command(name="login")
@click.option('--provider', required=True, help='Provedor (ex: google-antigravity)')
@click.option('--set-default', is_flag=True, help='Define como provedor padrão')
def models_auth_login(provider, set_default):
    """Realiza o login em um provedor de IA"""
    console.print(f"[bold blue]Iniciando login para o provedor: {provider}[/bold blue]")
    
    if provider == "google-antigravity":
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth?client_id=1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A51121%2Foauth-callback&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcclog+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fexperimentsandconfigs&code_challenge=CHLG-uBL8X-7Xdk0W83-_E82qKkrgQNJ5h3YUml0deg&code_challenge_method=S256&state=32c19a6b7c2705af55ffbf04316daeeb&access_type=offline&prompt=consent"
        console.print(f"\n[yellow]Por favor, autorize o acesso no seu navegador:[/yellow]")
        console.print(f"[link={auth_url}]{auth_url}[/link]\n")
        console.print("[cyan]Aguardando callback em http://localhost:51121/oauth-callback...[/cyan]")
        
        if set_default:
            update_env("DEFAULT_PROVIDER", provider)
            console.print(f"[green]Provedor {provider} definido como padrão![/green]")

@cli.group()
def workflows():
    """Gerencia e executa workflows automatizados (Lobster Engine)"""
    pass

@workflows.command(name="list")
def workflows_list():
    """Lista todos os workflows disponíveis"""
    try:
        from workflow_manager import listar_workflows
        listar_workflows()
    except Exception as e:
        console.print(f"[red]Erro ao listar workflows: {e}[/red]")

@workflows.command(name="run")
@click.argument('name')
def workflows_run(name):
    """Executa um workflow pelo nome"""
    try:
        from workflow_manager import executar_workflow
        success = executar_workflow(name)
        if success:
            console.print(f"[bold green]Workflow '{name}' concluído![/bold green]")
        else:
            console.print(f"[bold red]Workflow '{name}' falhou.[/bold red]")
    except Exception as e:
        console.print(f"[red]Erro ao executar workflow: {e}[/red]")

def update_env(key, value):
    """Auxiliar para atualizar o arquivo .env"""
    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write(f"{key}={value}\n")
        return

    with open(env_file, 'r') as f:
        lines = f.readlines()

    new_lines = []
    found = False
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}\n")

    with open(env_file, 'w') as f:
        f.writelines(new_lines)


if __name__ == '__main__':
    cli()
