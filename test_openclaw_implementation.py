#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para validar implementação OpenClaw-like
"""

import os
import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_config_manager():
    """Testa o config manager"""
    console.print("\n[bold blue]1. Testando Config Manager...[/bold blue]")
    
    try:
        from core.config_manager import ConfigManager, get_config
        
        # Criar config manager
        manager = ConfigManager()
        console.print("  ✓ ConfigManager importado")
        
        # Carregar config
        config = manager.load_config()
        console.print("  ✓ Config carregado")
        
        # Testar valores
        system_name = config.get('system.name')
        gateway_port = config.get('gateway.port')
        
        console.print(f"  ✓ System Name: {system_name}")
        console.print(f"  ✓ Gateway Port: {gateway_port}")
        
        # Testar token
        token = manager.get_or_create_token()
        console.print(f"  ✓ Token gerado: {token[:8]}...{token[-4:]}")
        
        # Verificar diretórios
        workspace = manager.get_workspace_dir()
        memory = manager.get_memory_dir()
        
        console.print(f"  ✓ Workspace: {workspace}")
        console.print(f"  ✓ Memory: {memory}")
        
        return True
        
    except Exception as e:
        console.print(f"  ✗ Erro: {e}", style="red")
        return False


def test_auth_middleware():
    """Testa o middleware de autenticação"""
    console.print("\n[bold blue]2. Testando Auth Middleware...[/bold blue]")
    
    try:
        from core.auth_middleware import check_authentication
        
        console.print("  ✓ Auth middleware importado")
        
        # Nota: check_authentication precisa de streamlit context
        # então só testamos a importação
        
        return True
        
    except Exception as e:
        console.print(f"  ✗ Erro: {e}", style="red")
        return False


def test_cli_commands():
    """Testa comandos do CLI"""
    console.print("\n[bold blue]3. Testando CLI Commands...[/bold blue]")
    
    try:
        from cli.main import cli
        
        console.print("  ✓ CLI importado")
        
        # Verificar se comando dashboard existe
        commands = [cmd.name for cmd in cli.commands.values()]
        
        required_commands = ['onboard', 'start', 'stop', 'status', 'dashboard', 'config']
        
        for cmd in required_commands:
            if cmd in commands:
                console.print(f"  ✓ Comando '{cmd}' disponível")
            else:
                console.print(f"  ✗ Comando '{cmd}' não encontrado", style="red")
                return False
        
        return True
        
    except Exception as e:
        console.print(f"  ✗ Erro: {e}", style="red")
        return False


def test_directory_structure():
    """Testa estrutura de diretórios"""
    console.print("\n[bold blue]4. Testando Estrutura de Diretórios...[/bold blue]")
    
    try:
        home = Path.home()
        cleudocode_dir = home / ".cleudocode"
        
        required_dirs = [
            cleudocode_dir,
            cleudocode_dir / "workspace",
            cleudocode_dir / "memory",
            cleudocode_dir / "skills",
            cleudocode_dir / "logs",
            cleudocode_dir / "cache",
            cleudocode_dir / "browser_data"
        ]
        
        all_exist = True
        for dir_path in required_dirs:
            if dir_path.exists():
                console.print(f"  ✓ {dir_path}")
            else:
                console.print(f"  ✗ {dir_path} não existe", style="yellow")
                all_exist = False
        
        # Verificar arquivos
        config_file = cleudocode_dir / "config.yaml"
        token_file = cleudocode_dir / ".gateway_token"
        
        if config_file.exists():
            console.print(f"  ✓ {config_file}")
        else:
            console.print(f"  ✗ {config_file} não existe", style="yellow")
            all_exist = False
        
        if token_file.exists():
            console.print(f"  ✓ {token_file}")
        else:
            console.print(f"  ⚠ {token_file} será criado no primeiro uso", style="yellow")
        
        return all_exist
        
    except Exception as e:
        console.print(f"  ✗ Erro: {e}", style="red")
        return False


def test_project_files():
    """Testa arquivos do projeto"""
    console.print("\n[bold blue]5. Testando Arquivos do Projeto...[/bold blue]")
    
    try:
        project_root = Path(__file__).parent
        
        required_files = [
            "core/config_manager.py",
            "core/auth_middleware.py",
            "cli/main.py",
            "web_app.py",
            ".cleudocode/config.yaml",
            "ucm/context.md",
            "ucm/todos.md",
            "ucm/insights.md",
            "QUICKSTART.md",
            "OPENCLAW_IMPLEMENTATION.md"
        ]
        
        all_exist = True
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists():
                console.print(f"  ✓ {file_path}")
            else:
                console.print(f"  ✗ {file_path} não existe", style="red")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        console.print(f"  ✗ Erro: {e}", style="red")
        return False


def generate_report(results):
    """Gera relatório final"""
    console.print("\n" + "="*60)
    
    table = Table(title="Relatório de Testes")
    table.add_column("Teste", style="cyan")
    table.add_column("Status", style="bold")
    
    for test_name, passed in results.items():
        status = "[green]✓ PASSOU[/green]" if passed else "[red]✗ FALHOU[/red]"
        table.add_row(test_name, status)
    
    console.print(table)
    
    total = len(results)
    passed = sum(results.values())
    percentage = (passed / total) * 100
    
    console.print(f"\n[bold]Resultado: {passed}/{total} testes passaram ({percentage:.1f}%)[/bold]")
    
    if percentage == 100:
        console.print(Panel.fit(
            "[bold green]✅ TODOS OS TESTES PASSARAM![/bold green]\n"
            "O sistema está pronto para uso.",
            title="Sucesso"
        ))
    elif percentage >= 80:
        console.print(Panel.fit(
            "[bold yellow]⚠️ MAIORIA DOS TESTES PASSOU[/bold yellow]\n"
            "Alguns componentes podem precisar de atenção.",
            title="Atenção"
        ))
    else:
        console.print(Panel.fit(
            "[bold red]❌ VÁRIOS TESTES FALHARAM[/bold red]\n"
            "Revise a instalação e configuração.",
            title="Erro"
        ))


def main():
    """Função principal"""
    console.print(Panel.fit(
        "[bold blue]Teste de Validação - Cleudocode OpenClaw-like[/bold blue]\n"
        "Validando implementação...",
        title="Iniciando Testes"
    ))
    
    # Adicionar project root ao path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Executar testes
    results = {
        "Config Manager": test_config_manager(),
        "Auth Middleware": test_auth_middleware(),
        "CLI Commands": test_cli_commands(),
        "Directory Structure": test_directory_structure(),
        "Project Files": test_project_files()
    }
    
    # Gerar relatório
    generate_report(results)
    
    # Retornar código de saída
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
