---
name: wordpress
description: Integração profunda com WordPress REST API para gestão de conteúdo, mídia e automação de afiliados.
homepage: https://github.com/automacoescomerciaisintegradas/cleudocode
metadata:
  cleudocode:
    emoji: "🌐"
    category: automation
    requires:
      env:
        - WP_URL
        - WP_USERNAME
        - WP_APPLICATION_PASSWORD
      packages:
        - requests
    install:
      - method: pip
        command: pip install requests
---

# WordPress Skill

Esta skill permite ao Cleudocode interagir com sites WordPress de forma autônoma.

## Funcionalidades

- **Publicação de Posts**: Criar, atualizar e deletar posts.
- **Gestão de Mídia**: Upload de imagens e vídeos.
- **Integração REST**: Acesso a qualquer endpoint da WP REST API.
- **Suporte a Afiliados**: Formatação automática para links Shopee, Amazon e ML.

## Configuração

Certifique-se de definir as seguintes variáveis no seu `.env`:

```env
WP_URL=https://seu-site.com
WP_USERNAME=seu-usuario
WP_APPLICATION_PASSWORD=xxxx xxxx xxxx xxxx
```

## Uso

### Criar um Post

```xml
<tool code="wordpress">
action:create_post title:"Minha Oferta" content:"Confira este produto!" status:"publish"
</tool>
```

### Upload de Imagem

```xml
<tool code="wordpress">
action:upload_media file_path:"./imagem.png" alt_text:"Produto em oferta"
</tool>
```
