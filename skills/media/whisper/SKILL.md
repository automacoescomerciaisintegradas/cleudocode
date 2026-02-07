---
name: whisper
description: Transcreve áudio para texto usando OpenAI Whisper (API ou local).
homepage: https://openai.com/research/whisper
metadata:
  cleudocode:
    emoji: "🎤"
    category: "media"
    requires:
      anyBins: ["curl", "ffmpeg"]
    install:
      - id: openai
        kind: pip
        package: openai
        label: "Instalar SDK OpenAI"
      - id: local
        kind: pip
        package: openai-whisper
        label: "Instalar Whisper local (GPU recomendado)"
---

# Whisper STT Skill

Transcrição de áudio para texto (Speech-to-Text) usando OpenAI Whisper.

## Modos de Operação

| Modo | Requisitos | Latência | Custo |
|------|------------|----------|-------|
| API | OPENAI_API_KEY | ~2s/min | $0.006/min |
| Local | GPU NVIDIA | ~10s/min | Gratuito |

## Configuração

```bash
# .env
OPENAI_API_KEY=sk-...
WHISPER_MODEL=base  # Para modo local: tiny, base, small, medium, large
```

## Uso

### Transcrever Áudio

```python
whisper action:transcribe file:/path/to/audio.mp3
```

### Com Idioma Específico

```python
whisper action:transcribe file:/path/to/audio.mp3 language:pt
```

### Transcrição com Timestamps

```python
whisper action:transcribe file:/path/to/audio.mp3 timestamps:true
```

### Traduzir para Inglês

```python
whisper action:translate file:/path/to/audio.mp3
```

## Formatos Suportados

- MP3, MP4, MPEG, MPGA
- M4A, WAV, WEBM
- OGG, FLAC

## Parâmetros

| Parâmetro | Descrição | Default |
|-----------|-----------|---------|
| `file` | Caminho do arquivo de áudio | Obrigatório |
| `mode` | api ou local | api |
| `language` | Código do idioma (pt, en, etc) | Auto-detectado |
| `timestamps` | Incluir timestamps | false |
| `model` | Modelo (whisper-1, base, large) | whisper-1 |
| `output` | Arquivo de saída (.txt, .srt, .vtt) | Retorna texto |

## Exemplos

### Transcrever Reunião

```python
whisper action:transcribe 
  file:/gravacoes/reuniao_2026-02-02.mp3
  language:pt
  output:/transcricoes/reuniao.txt
```

### Legendas para Vídeo

```python
whisper action:transcribe 
  file:/videos/apresentacao.mp4
  timestamps:true
  output:/legendas/apresentacao.srt
```

### Modo Local (GPU)

```python
whisper action:transcribe 
  file:/audio/podcast.mp3
  mode:local
  model:large
```

## Limitações

- API: Máximo 25MB por arquivo
- Local: Depende da VRAM
- Áudios longos: Processados em chunks

## Notas

- FFmpeg é necessário para conversão de formatos
- Modo local requer CUDA para performance
- Idiomas suportados: 97 (Whisper large)
