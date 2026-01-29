"""
Teste rápido do Whisper STT e Coqui TTS.
Valida integração de voz (transcrição e síntese).
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def test_whisper():
    """Testa Whisper STT."""
    
    console.print("\n[bold cyan]🎤 TESTE DO WHISPER (SPEECH-TO-TEXT)[/bold cyan]\n")
    
    try:
        console.print("[yellow]Importando Whisper...[/yellow]")
        from integrations.whisper import WhisperSTT
        
        console.print("[green]✅ Whisper importado com sucesso[/green]\n")
        
        # Inicializar Whisper
        console.print("[bold]Carregando modelo Whisper...[/bold]")
        console.print("[dim]Isso pode demorar na primeira vez (download do modelo)[/dim]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Carregando modelo 'base'...", total=None)
            
            whisper = WhisperSTT(model_size="base", device="cpu")
            
            progress.update(task, completed=True)
        
        console.print("[green]✅ Modelo Whisper carregado![/green]\n")
        
        # Informações do modelo
        console.print(Panel(
            f"[bold]Modelo:[/bold] {whisper.model_size}\n"
            f"[bold]Device:[/bold] {whisper.device}\n"
            f"[bold]Status:[/bold] Pronto para transcrição",
            title="Whisper STT",
            border_style="cyan"
        ))
        
        # Nota sobre teste de transcrição
        console.print("\n[yellow]ℹ️ Para testar transcrição:[/yellow]")
        console.print("   1. Grave um áudio curto (formato .ogg, .mp3, .wav)")
        console.print("   2. Salve como 'test_audio.ogg' no diretório do projeto")
        console.print("   3. Execute:")
        console.print("      [cyan]result = whisper.transcribe('test_audio.ogg', language='pt')[/cyan]")
        console.print("      [cyan]print(result['text'])[/cyan]\n")
        
        return True
        
    except ImportError as e:
        console.print(f"[red]❌ Erro ao importar Whisper:[/red] {e}")
        console.print("\n[yellow]Instale com:[/yellow] pip install openai-whisper")
        return False
    except Exception as e:
        console.print(f"[red]❌ Erro:[/red] {e}")
        import traceback
        console.print(traceback.format_exc())
        return False


def test_coqui_tts():
    """Testa Coqui TTS."""
    
    console.print("\n[bold cyan]🔊 TESTE DO COQUI TTS (TEXT-TO-SPEECH)[/bold cyan]\n")
    
    try:
        console.print("[yellow]Importando Coqui TTS...[/yellow]")
        from integrations.coqui_tts import CoquiTTS
        
        console.print("[green]✅ Coqui TTS importado com sucesso[/green]\n")
        
        # Inicializar TTS
        console.print("[bold]Carregando modelo TTS...[/bold]")
        console.print("[dim]Isso pode demorar na primeira vez (download do modelo)[/dim]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Carregando modelo português...", total=None)
            
            tts = CoquiTTS(model_name="tts_models/pt/cv/vits", gpu=False)
            
            progress.update(task, completed=True)
        
        console.print("[green]✅ Modelo TTS carregado![/green]\n")
        
        # Informações do modelo
        console.print(Panel(
            f"[bold]Modelo:[/bold] {tts.model_name}\n"
            f"[bold]GPU:[/bold] {'Sim' if tts.gpu else 'Não'}\n"
            f"[bold]Status:[/bold] Pronto para síntese",
            title="Coqui TTS",
            border_style="cyan"
        ))
        
        # Testar síntese
        console.print("\n[bold]Testando síntese de voz...[/bold]")
        
        test_text = "Olá! Este é um teste de síntese de voz usando Coqui TTS."
        output_file = "test_output.wav"
        
        console.print(f"[dim]Texto:[/dim] {test_text}")
        console.print(f"[dim]Arquivo:[/dim] {output_file}\n")
        
        result = tts.synthesize(test_text, output_file)
        
        if result['success']:
            console.print(Panel(
                f"[bold green]✅ Áudio gerado com sucesso![/bold green]\n\n"
                f"[bold]Arquivo:[/bold] {result['audio_path']}\n"
                f"[bold]Texto:[/bold] {result['text']}\n"
                f"[bold]Duração estimada:[/bold] {result['duration_estimate']:.1f}s",
                title="Síntese Concluída",
                border_style="green"
            ))
            
            console.print(f"\n[yellow]🔊 Reproduza o áudio:[/yellow] {output_file}")
            
            return True
        else:
            console.print(f"[red]❌ Erro na síntese:[/red] {result['error']}")
            return False
            
    except ImportError as e:
        console.print(f"[red]❌ Erro ao importar Coqui TTS:[/red] {e}")
        console.print("\n[yellow]Instale com:[/yellow] pip install TTS")
        return False
    except Exception as e:
        console.print(f"[red]❌ Erro:[/red] {e}")
        import traceback
        console.print(traceback.format_exc())
        return False


def test_voice_skill():
    """Testa Voice Skill completa."""
    
    console.print("\n[bold cyan]🎙️ TESTE DA VOICE SKILL[/bold cyan]\n")
    
    try:
        console.print("[yellow]Importando Voice Skill...[/yellow]")
        from skills.voice import VoiceSkill
        
        console.print("[green]✅ Voice Skill importada com sucesso[/green]\n")
        
        # Inicializar skill
        console.print("[bold]Inicializando Voice Skill...[/bold]\n")
        
        voice = VoiceSkill()
        
        console.print(Panel(
            f"[bold]Nome:[/bold] {voice.name}\n"
            f"[bold]Descrição:[/bold] {voice.description}\n"
            f"[bold]Status:[/bold] Pronto",
            title="Voice Skill",
            border_style="cyan"
        ))
        
        console.print("\n[green]✅ Voice Skill pronta para uso![/green]")
        
        # Exemplo de uso
        console.print("\n[bold]Exemplo de uso:[/bold]")
        console.print("""
[cyan]# Transcrever áudio[/cyan]
result = voice.transcribe('audio.ogg', language='pt')
print(result['text'])

[cyan]# Sintetizar texto[/cyan]
result = voice.synthesize('Olá!', 'output.wav')
print(result['audio_path'])

[cyan]# Transcrever e responder[/cyan]
result = voice.transcribe_and_respond(
    'user_audio.ogg',
    'Entendi sua pergunta!',
    'response.wav'
)
""")
        
        return True
        
    except ImportError as e:
        console.print(f"[red]❌ Erro ao importar Voice Skill:[/red] {e}")
        return False
    except Exception as e:
        console.print(f"[red]❌ Erro:[/red] {e}")
        import traceback
        console.print(traceback.format_exc())
        return False


def main():
    """Executa todos os testes de voz."""
    
    console.print(Panel(
        "[bold cyan]🎙️ TESTE DE INTEGRAÇÃO DE VOZ[/bold cyan]\n\n"
        "Este teste valida:\n"
        "• Whisper STT (Speech-to-Text)\n"
        "• Coqui TTS (Text-to-Speech)\n"
        "• Voice Skill (Integração)",
        title="Cleudocodebot - Voice Testing",
        border_style="cyan"
    ))
    
    results = {
        "Whisper STT": False,
        "Coqui TTS": False,
        "Voice Skill": False
    }
    
    # Teste 1: Whisper
    results["Whisper STT"] = test_whisper()
    
    # Teste 2: Coqui TTS
    results["Coqui TTS"] = test_coqui_tts()
    
    # Teste 3: Voice Skill
    results["Voice Skill"] = test_voice_skill()
    
    # Resumo final
    console.print("\n" + "="*60 + "\n")
    console.print("[bold cyan]📊 RESUMO DOS TESTES[/bold cyan]\n")
    
    for test_name, passed in results.items():
        icon = "✅" if passed else "❌"
        color = "green" if passed else "red"
        console.print(f"{icon} [{color}]{test_name}[/{color}]")
    
    all_passed = all(results.values())
    
    console.print("\n")
    if all_passed:
        console.print(Panel(
            "[bold green]🎉 TODOS OS TESTES PASSARAM![/bold green]\n\n"
            "O sistema de voz está pronto para uso!",
            title="Resultado Final",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "[bold yellow]⚠️ ALGUNS TESTES FALHARAM[/bold yellow]\n\n"
            "Verifique as dependências:\n"
            "• pip install openai-whisper\n"
            "• pip install TTS\n"
            "• Instale FFmpeg no sistema",
            title="Resultado Final",
            border_style="yellow"
        ))
    
    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️ Teste interrompido pelo usuário[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Erro fatal:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)
