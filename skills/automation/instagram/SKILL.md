---
name: instagram
description: Integração com Instagram Graph API para publicação de mídia e gestão de perfil.
homepage: https://github.com/automacoescomerciaisintegradas/cleudocode
metadata:
  cleudocode:
    emoji: "📸"
    category: automation
    requires:
      env:
        - INSTAGRAM_CLIENT_ID
        - INSTAGRAM_CLIENT_SECRET
        - INSTAGRAM_REDIRECT_URI
      packages:
        - requests
    install:
      - method: pip
        command: pip install requests
---

# Instagram Skill

Esta skill permite ao Cleudocode interagir com a API do Instagram para automatizar posts de ofertas.

## Funcionalidades

- **Publicação de Mídia**: Postar fotos e vídeos (Reels).
- **OAuth2 Flow**: Gerenciar troca de códigos por tokens de acesso.
- **Leitura de Perfil**: Obter mídia recente e informações do usuário.

## Configuração

Defina suas credenciais no `.env`:

```env
INSTAGRAM_CLIENT_ID=seu-id
INSTAGRAM_CLIENT_SECRET=seu-secret
INSTAGRAM_REDIRECT_URI=https://seu-backend.com/oauth/callback
```

## Uso

### Publicar Imagem

```xml
<tool code="instagram">
action:publish_photo url:"https://url-da-imagem.jpg" caption:"Confira esta oferta!"
</tool>
```
