import os
import logging
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except Exception as e:
    WHISPER_AVAILABLE = False
    logging.warning(f"Faster-Whisper desativado (Erro de importação ou DLL): {e}")

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def _load_model(self):
        if not WHISPER_AVAILABLE:
            logger.error("Faster-Whisper não está instalado.")
            return False
            
        if self.model is None:
            try:
                logger.info(f"Carregando modelo Whisper ({self.model_size})...")
                self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
                logger.info("Modelo Whisper carregado.")
                return True
            except Exception as e:
                logger.error(f"Erro ao carregar modelo Whisper: {e}")
                return False
        return True

    def transcribe(self, audio_path):
        """
        Transcreve um arquivo de áudio para texto.
        Suporta os formatos aceitos pelo ffmpeg.
        """
        if not self._load_model():
            return "[Erro: Whisper não disponível]"
            
        if not os.path.exists(audio_path):
            logger.error(f"Arquivo não encontrado: {audio_path}")
            return "[Erro: Arquivo não existe]"

        try:
            logger.info(f"Transcrevendo áudio: {audio_path}")
            segments, info = self.model.transcribe(audio_path, beam_size=5)
            
            text_segments = []
            for segment in segments:
                text_segments.append(segment.text)
                
            full_text = " ".join(text_segments).strip()
            logger.info(f"Transcrição concluída ({info.language}): {full_text[:50]}...")
            return full_text
        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            return f"[Erro na transcrição: {e}]"
