"""
Whisper STT Skill para Cleudocode
=================================

Transcrição de áudio para texto usando OpenAI Whisper.
Suporta API e modo local.

Autor: Cleudocode Team
Data: 02/02/2026
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import re
import logging

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.base import BaseSkill

logger = logging.getLogger(__name__)

# Tenta importar openai
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Tenta importar whisper local
try:
    import whisper as whisper_local
    HAS_LOCAL_WHISPER = True
except ImportError:
    HAS_LOCAL_WHISPER = False


class WhisperSkill(BaseSkill):
    """
    Skill de Speech-to-Text usando OpenAI Whisper.
    
    Modos:
    - api: Usa a API da OpenAI
    - local: Usa Whisper local (requer GPU)
    """
    
    SUPPORTED_FORMATS = ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm', 'ogg', 'flac']
    
    def __init__(self):
        super().__init__(
            name="whisper",
            description="Transcreve áudio para texto usando OpenAI Whisper (API ou local)."
        )
        self._local_model = None
    
    def execute(self, params: str) -> str:
        """
        Executa a skill.
        
        Formato: action:<action> file:<path> [mode:<api|local>] [outros params]
        
        Actions:
        - transcribe: Transcreve áudio para texto
        - translate: Transcreve e traduz para inglês
        - status: Verifica configuração
        """
        parsed = self._parse_params(params)
        action = parsed.get('action', 'transcribe')
        
        try:
            if action == 'status':
                return self._status()
            elif action == 'transcribe':
                return self._transcribe(parsed, translate=False)
            elif action == 'translate':
                return self._transcribe(parsed, translate=True)
            else:
                return f"Ação desconhecida: {action}"
        except Exception as e:
            logger.exception(f"Erro no WhisperSkill: {e}")
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
        lines = ["🎤 Whisper STT Status:\n"]
        
        # API OpenAI
        api_key = os.environ.get('OPENAI_API_KEY', '')
        lines.append(f"  API OpenAI: {'✅ Configurada' if api_key else '❌ Não configurada'}")
        
        # SDK OpenAI
        lines.append(f"  SDK openai: {'✅ Instalado' if HAS_OPENAI else '❌ Não instalado'}")
        
        # Whisper local
        lines.append(f"  Whisper local: {'✅ Instalado' if HAS_LOCAL_WHISPER else '❌ Não instalado'}")
        
        # FFmpeg
        import shutil
        lines.append(f"  FFmpeg: {'✅ Disponível' if shutil.which('ffmpeg') else '❌ Não encontrado'}")
        
        return "\n".join(lines)
    
    def _transcribe(self, params: Dict[str, str], translate: bool = False) -> str:
        """Transcreve áudio."""
        file_path = params.get('file', '')
        if not file_path:
            return "❌ file é obrigatório"
        
        file_path = Path(file_path)
        if not file_path.exists():
            return f"❌ Arquivo não encontrado: {file_path}"
        
        # Verifica formato
        ext = file_path.suffix.lower().lstrip('.')
        if ext not in self.SUPPORTED_FORMATS:
            return f"❌ Formato não suportado: {ext}. Use: {', '.join(self.SUPPORTED_FORMATS)}"
        
        # Verifica tamanho (máximo 25MB para API)
        file_size = file_path.stat().st_size / (1024 * 1024)
        
        mode = params.get('mode', 'api')
        language = params.get('language')
        timestamps = params.get('timestamps', 'false').lower() == 'true'
        model = params.get('model', 'whisper-1' if mode == 'api' else 'base')
        output = params.get('output', '')
        
        if mode == 'api':
            if file_size > 25:
                return f"❌ Arquivo muito grande ({file_size:.1f}MB). Máximo 25MB para API."
            result = self._transcribe_api(file_path, language, timestamps, translate)
        else:
            result = self._transcribe_local(file_path, model, language, timestamps, translate)
        
        # Salva output se especificado
        if output and result.get('text'):
            self._save_output(result, output)
            return f"✅ Transcrição salva em: {output}\n\nPreview:\n{result['text'][:500]}..."
        
        return self._format_result(result)
    
    def _transcribe_api(self, file_path: Path, language: str, 
                        timestamps: bool, translate: bool) -> dict:
        """Transcreve usando API OpenAI."""
        api_key = os.environ.get('OPENAI_API_KEY', '')
        if not api_key:
            raise ValueError("OPENAI_API_KEY não configurada")
        
        if HAS_OPENAI:
            # Usa SDK
            client = openai.OpenAI(api_key=api_key)
            
            with open(file_path, 'rb') as f:
                if translate:
                    response = client.audio.translations.create(
                        model='whisper-1',
                        file=f,
                        response_format='verbose_json' if timestamps else 'json'
                    )
                else:
                    kwargs = {
                        'model': 'whisper-1',
                        'file': f,
                        'response_format': 'verbose_json' if timestamps else 'json'
                    }
                    if language:
                        kwargs['language'] = language
                    response = client.audio.transcriptions.create(**kwargs)
            
            return {
                'text': response.text if hasattr(response, 'text') else str(response),
                'language': getattr(response, 'language', language or 'auto'),
                'segments': getattr(response, 'segments', []) if timestamps else []
            }
        else:
            # Usa curl como fallback
            return self._transcribe_api_curl(file_path, language, timestamps, translate, api_key)
    
    def _transcribe_api_curl(self, file_path: Path, language: str,
                             timestamps: bool, translate: bool, api_key: str) -> dict:
        """Transcreve usando curl."""
        endpoint = 'translations' if translate else 'transcriptions'
        url = f'https://api.openai.com/v1/audio/{endpoint}'
        
        cmd = [
            'curl', '-s', '-X', 'POST', url,
            '-H', f'Authorization: Bearer {api_key}',
            '-F', f'file=@{file_path}',
            '-F', 'model=whisper-1',
            '-F', f'response_format={"verbose_json" if timestamps else "json"}'
        ]
        
        if language and not translate:
            cmd.extend(['-F', f'language={language}'])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"curl falhou: {result.stderr}")
        
        data = json.loads(result.stdout)
        
        return {
            'text': data.get('text', ''),
            'language': data.get('language', language or 'auto'),
            'segments': data.get('segments', []) if timestamps else []
        }
    
    def _transcribe_local(self, file_path: Path, model: str, 
                          language: str, timestamps: bool, translate: bool) -> dict:
        """Transcreve usando Whisper local."""
        if not HAS_LOCAL_WHISPER:
            raise RuntimeError("Whisper local não instalado. Execute: pip install openai-whisper")
        
        # Carrega modelo (cache após primeira vez)
        if self._local_model is None or self._local_model.name != model:
            logger.info(f"Carregando modelo Whisper: {model}")
            self._local_model = whisper_local.load_model(model)
        
        # Transcreve
        task = 'translate' if translate else 'transcribe'
        result = self._local_model.transcribe(
            str(file_path),
            language=language,
            task=task,
            verbose=False
        )
        
        return {
            'text': result.get('text', ''),
            'language': result.get('language', language or 'auto'),
            'segments': result.get('segments', []) if timestamps else []
        }
    
    def _format_result(self, result: dict) -> str:
        """Formata resultado para exibição."""
        text = result.get('text', '')
        language = result.get('language', 'auto')
        segments = result.get('segments', [])
        
        lines = [f"🎤 Transcrição concluída!\n"]
        lines.append(f"📝 Idioma: {language}")
        lines.append(f"📊 Caracteres: {len(text)}")
        
        if segments:
            duration = segments[-1].get('end', 0) if segments else 0
            lines.append(f"⏱️ Duração: {duration:.1f}s")
        
        lines.append(f"\n--- Texto ---\n")
        lines.append(text)
        
        return "\n".join(lines)
    
    def _save_output(self, result: dict, output_path: str):
        """Salva transcrição em arquivo."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        ext = path.suffix.lower()
        
        if ext == '.srt':
            content = self._to_srt(result)
        elif ext == '.vtt':
            content = self._to_vtt(result)
        else:
            content = result.get('text', '')
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _to_srt(self, result: dict) -> str:
        """Converte para formato SRT."""
        lines = []
        for i, seg in enumerate(result.get('segments', []), 1):
            start = self._format_timestamp_srt(seg.get('start', 0))
            end = self._format_timestamp_srt(seg.get('end', 0))
            text = seg.get('text', '').strip()
            lines.append(f"{i}\n{start} --> {end}\n{text}\n")
        return "\n".join(lines)
    
    def _to_vtt(self, result: dict) -> str:
        """Converte para formato VTT."""
        lines = ["WEBVTT\n"]
        for seg in result.get('segments', []):
            start = self._format_timestamp_vtt(seg.get('start', 0))
            end = self._format_timestamp_vtt(seg.get('end', 0))
            text = seg.get('text', '').strip()
            lines.append(f"{start} --> {end}\n{text}\n")
        return "\n".join(lines)
    
    def _format_timestamp_srt(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_timestamp_vtt(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "whisper_transcribe",
                "description": "Transcreve áudio para texto",
                "parameters": {
                    "file": {"type": "string", "required": True},
                    "language": {"type": "string"},
                    "timestamps": {"type": "boolean"}
                }
            }
        ]


# Para testes
if __name__ == "__main__":
    skill = WhisperSkill()
    print(skill.get_definition())
    print("\n--- Status ---")
    print(skill.execute('action:status'))
