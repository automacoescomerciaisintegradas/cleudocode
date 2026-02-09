import os
import subprocess
import click
from rich.console import Console

console = Console()

@click.group()
def browser():
    """Gerencia o navegador dedicado (Playwright)"""
    pass

@browser.command()
def install():
    """Instala dependências do Playwright e Chromium"""
    console.print("[blue]Instalando navegadores Playwright...[/blue]")
    try:
        subprocess.run(["python3", "-m", "playwright", "install", "chromium"], check=True)
        console.print("[green]✓ Chromium instalado.[/green]")
        
        console.print("[blue]Instalando dependências de sistema...[/blue]")
        subprocess.run(["python3", "-m", "playwright", "install-deps"], check=True)
        console.print("[green]✓ Dependências instaladas.[/green]")
    except Exception as e:
        console.print(f"[red]Erro na instalação: {e}[/red]")

@browser.command()
@click.argument('url')
def open(url):
    """Abre uma URL no navegador (headless por padrão)"""
    console.print(f"[blue]Abrindo {url} via Playwright...[/blue]")
    script = f"""
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('{url}')
        print(f"Página carregada: {{await page.title()}}")
        # Mantém aberto por um tempo para demonstração
        await asyncio.sleep(10)
        await browser.close()

asyncio.run(run())
"""
    try:
        with open("temp_browser.py", "w") as f:
            f.write(script)
        subprocess.run(["python3", "temp_browser.py"])
        os.remove("temp_browser.py")
    except Exception as e:
        console.print(f"[red]Erro ao abrir página: {e}[/red]")

if __name__ == "__main__":
    browser()
