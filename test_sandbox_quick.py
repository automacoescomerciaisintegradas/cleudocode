"""
Teste rápido do Sistema de Sandbox.
Valida segurança e funcionalidades básicas.
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.sandbox import SandboxExecutor
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def test_sandbox():
    """Executa bateria de testes do sandbox."""
    
    console.print("\n[bold cyan]🔒 TESTE DO SISTEMA DE SANDBOX[/bold cyan]\n")
    
    # Criar sandbox
    sandbox = SandboxExecutor(
        sandbox_root="./sandbox",
        allowed_commands=["ls", "dir", "cat", "echo", "pwd"],
        max_file_size_mb=5,
        default_timeout=10
    )
    
    # Tabela de resultados
    table = Table(title="Resultados dos Testes")
    table.add_column("Teste", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Detalhes", style="yellow")
    
    # ========================================
    # TESTE 1: Comando Permitido
    # ========================================
    console.print("[bold]Teste 1:[/bold] Executar comando permitido (echo)")
    result = sandbox.execute_shell("echo 'Hello, Sandbox!'")
    
    if result['success'] and "Hello, Sandbox!" in result['stdout']:
        table.add_row("✅ Comando Permitido", "PASSOU", "echo executado com sucesso")
    else:
        table.add_row("❌ Comando Permitido", "FALHOU", result.get('error', 'Erro desconhecido'))
    
    # ========================================
    # TESTE 2: Comando Bloqueado
    # ========================================
    console.print("[bold]Teste 2:[/bold] Bloquear comando perigoso (rm)")
    result = sandbox.execute_shell("rm -rf /")
    
    if not result['success'] and "não permitido" in result.get('error', ''):
        table.add_row("✅ Comando Bloqueado", "PASSOU", "rm bloqueado corretamente")
    else:
        table.add_row("❌ Comando Bloqueado", "FALHOU", "Comando perigoso não foi bloqueado!")
    
    # ========================================
    # TESTE 3: Caracteres Perigosos
    # ========================================
    console.print("[bold]Teste 3:[/bold] Bloquear caracteres perigosos (&&)")
    result = sandbox.execute_shell("echo test && rm -rf /")
    
    if not result['success'] and "perigoso" in result.get('error', ''):
        table.add_row("✅ Caracteres Perigosos", "PASSOU", "Caractere && bloqueado")
    else:
        table.add_row("❌ Caracteres Perigosos", "FALHOU", "Caractere perigoso não bloqueado!")
    
    # ========================================
    # TESTE 4: Escrita de Arquivo
    # ========================================
    console.print("[bold]Teste 4:[/bold] Escrever arquivo no sandbox")
    result = sandbox.write_file("test.txt", "Conteúdo de teste do sandbox\nLinha 2\nLinha 3")
    
    if result['success']:
        table.add_row("✅ Escrita de Arquivo", "PASSOU", f"Arquivo criado: {result['filepath']}")
    else:
        table.add_row("❌ Escrita de Arquivo", "FALHOU", result.get('error', 'Erro ao escrever'))
    
    # ========================================
    # TESTE 5: Leitura de Arquivo
    # ========================================
    console.print("[bold]Teste 5:[/bold] Ler arquivo do sandbox")
    result = sandbox.read_file("test.txt")
    
    if result['success'] and "Conteúdo de teste" in result['content']:
        table.add_row("✅ Leitura de Arquivo", "PASSOU", f"{len(result['content'])} caracteres lidos")
    else:
        table.add_row("❌ Leitura de Arquivo", "FALHOU", result.get('error', 'Erro ao ler'))
    
    # ========================================
    # TESTE 6: Path Traversal
    # ========================================
    console.print("[bold]Teste 6:[/bold] Prevenir path traversal")
    result = sandbox.read_file("../../etc/passwd")
    
    if not result['success'] and "fora do sandbox" in result.get('error', ''):
        table.add_row("✅ Path Traversal", "PASSOU", "Acesso fora do sandbox bloqueado")
    else:
        table.add_row("❌ Path Traversal", "FALHOU", "Path traversal não foi bloqueado!")
    
    # ========================================
    # TESTE 7: Listar Diretório
    # ========================================
    console.print("[bold]Teste 7:[/bold] Listar conteúdo do sandbox")
    result = sandbox.list_directory(".")
    
    if result['success'] and result['total'] > 0:
        table.add_row("✅ Listar Diretório", "PASSOU", f"{result['total']} itens encontrados")
    else:
        table.add_row("❌ Listar Diretório", "FALHOU", result.get('error', 'Erro ao listar'))
    
    # ========================================
    # TESTE 8: Timeout
    # ========================================
    console.print("[bold]Teste 8:[/bold] Timeout de comando")
    # Comando que demora (sleep não está na whitelist, então será bloqueado antes)
    result = sandbox.execute_shell("sleep 100")
    
    if not result['success']:
        table.add_row("✅ Timeout", "PASSOU", "Comando bloqueado ou timeout funcionou")
    else:
        table.add_row("⚠️ Timeout", "AVISO", "Comando não bloqueado (sleep não na whitelist)")
    
    # ========================================
    # TESTE 9: Arquivo Grande
    # ========================================
    console.print("[bold]Teste 9:[/bold] Bloquear arquivo muito grande")
    large_content = "A" * (6 * 1024 * 1024)  # 6MB (acima do limite de 5MB)
    result = sandbox.write_file("large.txt", large_content)
    
    if not result['success'] and "muito grande" in result.get('error', ''):
        table.add_row("✅ Arquivo Grande", "PASSOU", "Arquivo grande bloqueado")
    else:
        table.add_row("❌ Arquivo Grande", "FALHOU", "Arquivo grande não foi bloqueado!")
    
    # ========================================
    # TESTE 10: Sobrescrever Arquivo
    # ========================================
    console.print("[bold]Teste 10:[/bold] Sobrescrever arquivo existente")
    result = sandbox.write_file("test.txt", "Novo conteúdo", overwrite=True)
    
    if result['success']:
        # Verificar se foi sobrescrito
        read_result = sandbox.read_file("test.txt")
        if "Novo conteúdo" in read_result.get('content', ''):
            table.add_row("✅ Sobrescrever", "PASSOU", "Arquivo sobrescrito corretamente")
        else:
            table.add_row("❌ Sobrescrever", "FALHOU", "Conteúdo não foi atualizado")
    else:
        table.add_row("❌ Sobrescrever", "FALHOU", result.get('error', 'Erro ao sobrescrever'))
    
    # Exibir tabela de resultados
    console.print("\n")
    console.print(table)
    
    # Resumo
    console.print("\n")
    passed = str(table).count("✅")
    failed = str(table).count("❌")
    warnings = str(table).count("⚠️")
    
    if failed == 0:
        console.print(Panel(
            f"[bold green]🎉 TODOS OS TESTES PASSARAM![/bold green]\n\n"
            f"✅ Aprovados: {passed}\n"
            f"⚠️ Avisos: {warnings}\n"
            f"❌ Falhas: {failed}",
            title="Resultado Final",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[bold red]⚠️ ALGUNS TESTES FALHARAM[/bold red]\n\n"
            f"✅ Aprovados: {passed}\n"
            f"⚠️ Avisos: {warnings}\n"
            f"❌ Falhas: {failed}",
            title="Resultado Final",
            border_style="red"
        ))
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = test_sandbox()
        sys.exit(0 if success else 1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Erro fatal:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)
