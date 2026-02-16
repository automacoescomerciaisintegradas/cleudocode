---
name: affiliate
description: Conversão de links e extração de mídia para programas de afiliados (Shopee, Amazon, Mercado Livre).
homepage: https://github.com/automacoescomerciaisintegradas/cleudocode
metadata:
  cleudocode:
    emoji: "🛍️"
    category: automation
    requires:
      env:
        - SHOPEE_AFFILIATE_ID
      packages:
        - beautifulsoup4
        - requests
    install:
      - method: pip
        command: pip install beautifulsoup4 requests
---

# Affiliate Skill

Esta skill permite ao Cleudocode processar links de produtos de grandes plataformas e convertê-los em links de afiliado, extraindo também imagens e vídeos.

## Funcionalidades

- **Resolução de Links**: Converte links curtos e diretos em links de afiliado.
- **Extração de Mídia**: Captura as melhores imagens e vídeos do produto.
- **Detecção de Plataforma**: Identifica automaticamente se o link é Shopee, Amazon ou ML.

## Configuração

Defina seus IDs no `.env`:

```env
SHOPEE_AFFILIATE_ID=18372150411
AMAZON_AFFILIATE_TAG=seu-tag
ML_AFFILIATE_ID=seu-id
```

## Uso

### Resolver Link Shopee

```xml
<tool code="affiliate">
action:resolve url:"https://shopee.com.br/produto-exemplo"
</tool>
```
