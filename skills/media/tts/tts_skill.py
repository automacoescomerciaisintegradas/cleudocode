"""
TTS Skill para Cleudocode
=========================

Text-to-Speech usando múltiplos provedores.
Suporta OpenAI, ElevenLabs, Google TTS e Edge TTS.

Autor: Cleudocode Team
Data: 02/02/2026
"""

import os
import json
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import logging

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.base import BaseSkill

logger = logging.getLogger(__name__)

# Tenta importar dependências
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False


class TTSSkill(BaseSkill):
    """
    Skill de Text-to-Speech.
    
    Provedores:
    - openai: Alta qualidade, várias vozes
    - elevenlabs: Qualidade premium
    - gtts: Gratuito, básico
    - edge: Edge TTS (gratuito)
    """
    
    # Vozes disponíveis por provedor
    VOICES = {
        'openai': ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
        'elevenlabs': ['Rachel', 'Domi', 'Bella', 'Antoni', 'Elli', 'Josh', 'Adam', 'Sam'],
        'gtts': [],  # Usa language codes
        'edge': ['pt-BR-FranciscaNeural', 'pt-BR-AntonioNeural', 'en-US-JennyNeural', 'en-US-GuyNeural']
    }
    
    def __init__(self):
        super().__init__(
            name="tts",
            description="Converte texto para áudio usando APIs de síntese de voz (OpenAI, ElevenLabs, gTTS)."
        )
        self.output_dir = Path(os.environ.get('TTS_OUTPUT_DIR', './outputs/audio'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, params: str) -> str:
        """
        Executa a skill.
        
        Formato: action:<action> text:<text> [provider:<provider>] [voice:<voice>]
        
        Actions:
        - speak: Gera áudio a partir do texto
        - voices: Lista vozes disponíveis
        - status: Verifica configuração
        """
        parsed = self._parse_params(params)
        action = parsed.get('action', 'speak')
        
        try:
            if action == 'status':
                return self._status()
            elif action == 'voices':
                return self._list_voices(parsed.get('provider', 'openai'))
            elif action == 'speak':
                return self._speak(parsed)
            else:
                return f"Ação desconhecida: {action}"
        except Exception as e:
            logger.exception(f"Erro no TTSSkill: {e}")
            return f"❌ Erro: {str(e)}"
    
    def _parse_params(self, params: str) -> Dict[str, str]:
        result = {}
        pattern = r'(\w+):(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))'
        matches = re.findall(pattern, params)
        for key, q1, q2, simple in matches:
            result[key] = q1 or q2 or simple
        return result
    
    def _status(self) -> str:
        """Verifica configuração."""
        lines = ["🔊 TTS Status:\n"]
        
        # OpenAI
        api_key = os.environ.get('OPENAI_API_KEY', '')
        lines.append(f"  OpenAI: {'✅ Configurado' if api_key else '❌ Não configurado'}")
        lines.append(f"    SDK: {'✅' if HAS_OPENAI else '❌'}")
        
        # ElevenLabs
        eleven_key = os.environ.get('ELEVENLABS_API_KEY', '')
        lines.append(f"  ElevenLabs: {'✅ Configurado' if eleven_key else '❌ Não configurado'}")
        
        # gTTS
        lines.append(f"  gTTS: {'✅ Instalado' if HAS_GTTS else '❌ Não instalado'}")
        
        # Edge TTS
        import shutil
        edge_available = shutil.which('edge-tts') is not None
        lines.append(f"  Edge TTS: {'✅ Disponível' if edge_available else '❌ Não instalado'}")
        
        return "\n".join(lines)
    
    def _list_voices(self, provider: str) -> str:
        """Lista vozes disponíveis."""
        voices = self.VOICES.get(provider, [])
        
        if provider == 'gtts':
            return """🔊 gTTS usa códigos de idioma:
  - pt (português)
  - en (inglês)
  - es (espanhol)
  - fr (francês)
  - de (alemão)
  
Use: language:pt"""
        
        if not voices:
            return f"❌ Provedor desconhecido: {provider}"
        
        lines = [f"🔊 Vozes {provider}:\n"]
        for voice in voices:
            lines.append(f"  • {voice}")
        
        return "\n".join(lines)
    
    def _speak(self, params: Dict[str, str]) -> str:
        """Gera áudio a partir do texto."""
        text = params.get('text', '')
        if not text:
            return "❌ text é obrigatório"
        
        provider = params.get('provider', 'openai')
        voice = params.get('voice', 'alloy')
        speed = float(params.get('speed', '1.0'))
        output = params.get('output', '')
        format_type = params.get('format', 'mp3')
        language = params.get('language', 'pt')
        
        # Gera nome de arquivo se não especificado
        if not output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output = self.output_dir / f"tts_{provider}_{timestamp}.{format_type}"
        else:
            output = Path(output)
        
        output.parent.mkdir(parents=True, exist_ok=True)
        
        # Gera baseado no provedor
        if provider == 'openai':
            return self._speak_openai(text, voice, speed, output)
        elif provider == 'elevenlabs':
            return self._speak_elevenlabs(text, voice, output)
        elif provider == 'gtts':
            return self._speak_gtts(text, language, output)
        elif provider == 'edge':
            return self._speak_edge(text, voice, output)
        else:
            return f"❌ Provedor não suportado: {provider}"
    
    def _speak_openai(self, text: str, voice: str, speed: float, output: Path) -> str:
        """Gera áudio via OpenAI."""
        api_key = os.environ.get('OPENAI_API_KEY', '')
        if not api_key:
            return "❌ OPENAI_API_KEY não configurada"
        
        if HAS_OPENAI:
            client = openai.OpenAI(api_key=api_key)
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed
            )
            
            response.stream_to_file(str(output))
        else:
            # Fallback com curl
            import urllib.request
            
            url = 'https://api.openai.com/v1/audio/speech'
            payload = {
                'model': 'tts-1',
                'voice': voice,
                'input': text,
                'speed': speed
            }
            
            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                with open(output, 'wb') as f:
                    f.write(response.read())
        
        return f"""🔊 Áudio gerado com sucesso!

📁 Arquivo: {output}
🎙️ Voz: {voice}
📝 Caracteres: {len(text)}
⚡ Velocidade: {speed}x"""
    
    def _speak_elevenlabs(self, text: str, voice: str, output: Path) -> str:
        """Gera áudio via ElevenLabs."""
        api_key = os.environ.get('ELEVENLABS_API_KEY', '')
        if not api_key:
            return "❌ ELEVENLABS_API_KEY não configurada"
        
        import urllib.request
        
        # Primeiro, obtém voice_id
        voices_url = 'https://api.elevenlabs.io/v1/voices'
        req = urllib.request.Request(
            voices_url,
            headers={'xi-api-key': api_key}
        )
        
        try:
            with urllib.request.urlopen(req) as resp:
                voices_data = json.loads(resp.read().decode())
        except Exception as e:
            return f"❌ Erro ao obter vozes: {e}"
        
        # Encontra voice_id
        voice_id = None
        for v in voices_data.get('voices', []):
            if v.get('name', '').lower() == voice.lower():
                voice_id = v.get('voice_id')
                break
        
        if not voice_id:
            # Usa primeiro disponível
            voice_id = voices_data.get('voices', [{}])[0].get('voice_id')
        
        if not voice_id:
            return "❌ Nenhuma voz disponível"
        
        # Gera áudio
        tts_url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
        payload = {
            'text': text,
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.5
            }
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            tts_url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'xi-api-key': api_key
            }
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(output, 'wb') as f:
                f.write(response.read())
        
        return f"""🔊 Áudio gerado com sucesso!

📁 Arquivo: {output}
🎙️ Voz: {voice}
📝 Caracteres: {len(text)}"""
    
    def _speak_gtts(self, text: str, language: str, output: Path) -> str:
        """Gera áudio via Google TTS."""
        if not HAS_GTTS:
            return "❌ gTTS não instalado. Execute: pip install gTTS"
        
        tts = gTTS(text=text, lang=language)
        tts.save(str(output))
        
        return f"""🔊 Áudio gerado com sucesso!

📁 Arquivo: {output}
🌐 Idioma: {language}
📝 Caracteres: {len(text)}"""
    
    def _speak_edge(self, text: str, voice: str, output: Path) -> str:
        """Gera áudio via Edge TTS."""
        import shutil
        
        if not shutil.which('edge-tts'):
            return "❌ edge-tts não instalado. Execute: pip install edge-tts"
        
        cmd = [
            'edge-tts',
            '--voice', voice,
            '--text', text,
            '--write-media', str(output)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return f"❌ Erro edge-tts: {result.stderr}"
        
        return f"""🔊 Áudio gerado com sucesso!

📁 Arquivo: {output}
🎙️ Voz: {voice}
📝 Caracteres: {len(text)}"""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "tts_speak",
                "description": "Converte texto para áudio",
                "parameters": {
                    "text": {"type": "string", "required": True},
                    "provider": {"type": "string", "enum": ["openai", "elevenlabs", "gtts", "edge"]},
                    "voice": {"type": "string"}
                }
            }
        ]


# Para testes
if __name__ == "__main__":
    skill = TTSSkill()
    print(skill.get_definition())
    print("\n--- Status ---")
    print(skill.execute('action:status'))
    print("\n--- Vozes OpenAI ---")
    print(skill.execute('action:voices provider:openai'))
