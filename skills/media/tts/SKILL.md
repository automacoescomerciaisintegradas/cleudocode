---
name: tts
description: Converte texto para áudio usando APIs de síntese de voz (OpenAI, ElevenLabs, gTTS).
homepage: https://platform.openai.com/docs/guides/text-to-speech
metadata:
  cleudocode:
    emoji: "🔊"
    category: "media"
    requires:
      anyBins: ["curl"]
    install:
      - id: openai
        kind: pip
        package: openai
        label: "Instalar SDK OpenAI"
      - id: gtts
        kind: pip
        package: gTTS
        label: "Instalar Google TTS (gratuito)"
---

# TTS Skill

Text-to-Speech: Converte texto para áudio de alta qualidade.

## Provedores Suportados

| Provedor | Qualidade | Latência | Custo |
|----------|-----------|----------|-------|
| OpenAI | Alta | Rápido | $0.015/1K chars |
| ElevenLabs | Excelente | Médio | $0.30/1K chars |
| gTTS | Básica | Rápido | Gratuito |
| Edge TTS | Boa | Rápido | Gratuito |

## Configuração

```bash
# .env
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
TTS_OUTPUT_DIR=./outputs/audio
```

## Uso

### OpenAI TTS

```python
tts action:speak text:"Olá, eu sou o Cleudocode!" voice:alloy
```

### ElevenLabs

```python
tts action:speak text:"Texto para falar" provider:elevenlabs voice:Rachel
```

### Google TTS (Gratuito)

```python
tts action:speak text:"Texto em português" provider:gtts language:pt
```

## Vozes Disponíveis

### OpenAI

| Voz | Características |
|-----|-----------------|
| alloy | Neutra, versátil |
| echo | Grave, masculina |
| fable | Expressiva, narração |
| onyx | Profunda, autoritária |
| nova | Amigável, feminina |
| shimmer | Suave, clara |

### ElevenLabs

Vozes customizadas e realistas (ver dashboard).

## Parâmetros

| Parâmetro | Descrição | Default |
|-----------|-----------|---------|
| `text` | Texto para sintetizar | Obrigatório |
| `provider` | Provedor (openai, elevenlabs, gtts) | openai |
| `voice` | Voz a usar | alloy |
| `speed` | Velocidade (0.25-4.0) | 1.0 |
| `output` | Arquivo de saída | Auto-gerado |
| `format` | Formato (mp3, opus, aac) | mp3 |

## Exemplos

### Narração de Artigo

```python
tts action:speak 
  text:"Bem-vindos ao nosso podcast sobre tecnologia..."
  voice:fable
  speed:0.9
  output:/audio/podcast_intro.mp3
```

### Notificação Rápida

```python
tts action:speak 
  text:"Tarefa concluída com sucesso!"
  voice:nova
```

### Multi-idioma

```python
tts action:speak 
  text:"Hello world"
  provider:gtts
  language:en

tts action:speak 
  text:"Olá mundo"
  provider:gtts
  language:pt
```

## Limitações

- OpenAI: 4096 caracteres por request
- ElevenLabs: Depende do plano
- gTTS: Requer internet

## Notas

- Arquivos são salvos em `./outputs/audio/` por padrão
- Use speed > 1 para áudio rápido, < 1 para lento
- gTTS é gratuito mas qualidade inferior
