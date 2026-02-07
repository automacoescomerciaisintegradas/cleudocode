---
name: image-gen
description: Gera imagens usando APIs de IA como DALL-E, Stable Diffusion e Replicate.
homepage: https://platform.openai.com/docs/guides/images
metadata:
  cleudocode:
    emoji: "🎨"
    category: "media"
    requires:
      anyBins: ["curl"]
      env: []
    install:
      - id: openai
        kind: pip
        package: openai
        label: "Instalar SDK OpenAI (opcional)"
---

# Image Gen Skill

Geração de imagens usando APIs de IA.

## Provedores Suportados

| Provedor | Modelos | API Key |
|----------|---------|---------|
| OpenAI | DALL-E 3, DALL-E 2 | OPENAI_API_KEY |
| Replicate | Stable Diffusion, FLUX | REPLICATE_API_TOKEN |
| Stability AI | Stable Diffusion XL | STABILITY_API_KEY |
| Local | Automatic1111, ComfyUI | Nenhuma |

## Configuração

```bash
# .env
OPENAI_API_KEY=sk-...
REPLICATE_API_TOKEN=r8_...
STABILITY_API_KEY=sk-...
IMAGE_GEN_OUTPUT_DIR=./outputs/images
```

## Uso

### Gerar com DALL-E

```python
image-gen action:generate prompt:"Um gato astronauta" provider:openai model:dall-e-3
```

### Gerar com Stable Diffusion (Replicate)

```python
image-gen action:generate prompt:"Paisagem cyberpunk" provider:replicate model:sdxl
```

### Variações

```python
image-gen action:variation image:/path/to/image.png
```

### Edição (Inpainting)

```python
image-gen action:edit image:/path/to/image.png mask:/path/to/mask.png prompt:"Adicionar chapéu"
```

## Parâmetros Comuns

| Parâmetro | Descrição | Default |
|-----------|-----------|---------|
| `prompt` | Descrição da imagem | Obrigatório |
| `provider` | Provedor de IA | openai |
| `model` | Modelo específico | dall-e-3 |
| `size` | Tamanho (1024x1024, etc) | 1024x1024 |
| `quality` | Qualidade (standard, hd) | standard |
| `style` | Estilo (natural, vivid) | vivid |
| `output` | Caminho de saída | Auto-gerado |

## Exemplos

### Arte Digital

```python
image-gen action:generate 
  prompt:"Digital art of a mystical forest with bioluminescent plants"
  size:1792x1024
  quality:hd
  style:vivid
```

### Logo

```python
image-gen action:generate 
  prompt:"Minimal logo for a tech startup, clean lines, modern"
  size:1024x1024
  style:natural
```

## Notas

- DALL-E 3: Máximo 1 imagem por request
- Replicate: Suporta batch e modelos customizados
- Imagens são salvas em `./outputs/images/` por padrão
- Custo: ~$0.04-0.12 por imagem (DALL-E 3)
