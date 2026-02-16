# WhatsApp Skill

Integração com a Evolution API v2 para automação de mensagens e divulgação de ofertas.

## Funcionalidades
- Envio de mensagens de texto com prévia de link.
- Envio de mídia (imagens e vídeos) com legenda.
- Verificação de status da instância.

## Configuração Necessária (.env)
- `WHATSAPP_API_URL`: URL do servidor Evolution API.
- `WHATSAPP_API_KEY`: Chave global de API.
- `WHATSAPP_API_INSTANCE`: Nome da instância conectada.
- `WHATSAPP_API_TOKEN_INSTANCE`: Token específico da instância (opcional dependendo da config).

## Exemplo de Uso
```python
# Enviar oferta com imagem
action:send_media number:"5511999999999" media_url:"http://link.com/foto.jpg" caption:"Confira esta oferta!" media_type:"image"
```

## Ferramentas para LLM
- `whatsapp_send`: Enviar texto ou mídia.
