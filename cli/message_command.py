import os
import requests
import click
from rich.console import Console
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

console = Console()

@click.group()
def message():
    """Gerencia o envio de mensagens"""
    pass

@message.command()
@click.option('--channel', required=True, type=click.Choice(['telegram', 'whatsapp', 'discord', 'dashboard']), help='Canal de destino')
@click.option('--target', required=True, help='Destinatário (ID, JID ou @username)')
@click.option('--message', 'text', required=True, help='Conteúdo da mensagem')
@click.option('--token', help='Token do gateway para autenticação')
def send(channel, target, text, token):
    """Envia uma mensagem via gateway"""
    gateway_token = token or os.getenv("CLEUDOCODE_GATEWAY_TOKEN")
    if not gateway_token:
        console.print("[red]Erro: Token do gateway não fornecido e não encontrado no .env[/red]")
        return

    url = "http://localhost:18900/api/messages"
    headers = {
        "Authorization": f"Bearer {gateway_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "target": target,
        "message": text
    }

    try:
        console.print(f"[blue]Enviando mensagem para {target} no {channel}...[/blue]")
        # Nota: O endpoint /api/messages no web_server.py atual trata POST como comando pro orchestrator
        # mas aqui vamos simular a intenção de expandir o gateway
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            console.print("[green]✓ Mensagem processada pelo gateway.[/green]")
            data = resp.json()
            # Tentar 'response' ou 'reply' para compatibilidade
            ai_reply = data.get('response') or data.get('reply') or data.get('output') or "Sem resposta."
            console.print(f"\n[bold green]Resposta do Agente:[/bold green]\n{ai_reply}")
        else:
            console.print(f"[red]Erro ao enviar: {resp.status_code} - {resp.text}[/red]")
    except Exception as e:
        console.print(f"[red]Falha na comunicação com o gateway: {e}[/red]")

if __name__ == "__main__":
    message()
