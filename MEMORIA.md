# MEMÓRIA — Gerador de Cards de Ofertas (cleudocode)

> Documento de memória para retomar o trabalho em qualquer sessão futura.
> Atualizado em: 2026-08-30

## 📌 O que o sistema faz

Gera cards promocionais de ofertas da Shopee (HTML → PNG via Chrome headless) e
envia automaticamente para **grupo do WhatsApp (Evolution API)** e **grupo do Telegram**.

- Script principal: `gerador_ofertas_imagem.py`
- Templates: `templates/card_*.html`
- Logo da marca: `assets/logo_achadinhos_aci_transparente.png` (fundo removido)
- Rotina automática: `rotina_ofertas.sh` (cron)

## 🧩 Arquitetura do fluxo

1. `main()` recebe `--link` (curto `s.shopee...` ou completo `shopee.com.br/product/<shop>/<item>`)
2. `baixar_foto_e_dados_do_link(link)` → extrai **foto, nome e preço** do produto
   (fetch no HTML; CDN real = `down-br.img.susercontent.com/file/<hash>.webp`)
3. Template HTML renderizado com placeholders: `{{PRODUTO}} {{PRECO}} {{PRECO_ANTES}}
   {{LINK}} {{PRODUTO_IMG}} {{QR_IMG}} {{LOGO_ACI}}` (imagens embutidas como **data URI**)
4. `render_html_to_png()` → Chrome headless 800×800
5. Envio: `enviar_whatsapp()` (Evolution) + `enviar_telegram()` (bot)
6. Legenda: oferta + link + aviso legal + hashtags

## ✅ Correções aplicadas (2026-08-30)

1. **Link duplicado (sobre a imagem + rodapé)** → `injetar_link_no_html()` agora é
   **idempotente**: remove âncoras `<a>` do corpo (aspas simples e duplas), remove
   URLs soltas de shopee.com.br e deixa **1 link só no rodapé** (linkbar).
2. **Card sem foto do produto** → `main()` NÃO chamava a extração do link. Agora
   chama `baixar_foto_e_dados_do_link(link)` e usa a foto (nome/preço também se não
   informados). `PRODUTOS_IMAGEM` está vazia — não é mais necessária.
3. **Sobreposição (preço sobre a foto, CTA colidindo)** → reescrevi os 5 templates
   com **zonas fixas** que não colidem (card 800×800):
   - Header 0–96 · Foto 108–492 · Nome 500 (máx 2 linhas, clamp) · Preço/CTA
     acima do rodapé (bottom 78) · Linkbar 70px na base.
4. **Marca** → header "SHOPEE" substituído pelo **logo achadinhos ACI** (imagem
   embutida via `{{LOGO_ACI}}`, transparente).
5. **Aviso legal** adicionado à legenda de envio:
   "🪧 Comprando pelo nosso link, você ajuda o canal sem pagar nada a mais!
   ⚠️ Preço e estoque sujeitos a alteração."

## 🎨 Templates (6)

| Arquivo | Visual |
|---|---|
| `card_imperdivel.html` | Verde, OFERTA IMPERDÍVEL, logo + preço com "de X" |
| `card_relampago.html` | Vermelho/amarelo, OFERTA RELÂMPAGO, logo no canto do zig |
| `card_profissional.html` | Azul escuro, OFERTA CONFIRMADA |
| `card_desconto.html` | Roxo, badge -50% |
| `card_hotdeal.html` | Preto, HOT DEAL 🔥 |
| `card_anuncio.html` | **NOVO** — estilo anúncio Shopee (fundo claro, tagline, chips, CTA "Compre agora") |

Todos: foto do produto + nome (2 linhas) + preço + CTA + link no rodapé + logo ACI.

## 🖥️ Comandos úteis

```bash
cd /root/cleudocode
# gerar + enviar (WhatsApp + Telegram) usando o link (foto automática)
./venv/bin/python3 gerador_ofertas_imagem.py --link "<link>" --template "card_anuncio.html" --skip-grok

# só gerar PNG, sem enviar
./venv/bin/python3 gerador_ofertas_imagem.py --link "<link>" --template "card_relampago.html" --solo-html --sem-telegram --sem-whatsapp --skip-grok

# produto fixo + preço fixo + imagem local
./venv/bin/python3 gerador_ofertas_imagem.py --produto "X" --link "<link>" --preco "R$ 69,90" --imagem "/tmp/foto.webp" --template "card_anuncio.html" --skip-grok
```

`--skip-grok` = usa template direto (rápido, recomendado). Sem ele, tenta Grok 4.6 gerar o HTML.

## 📁 Arquivos de referência

- Cards gerados: `card_*_final.png`, `card_anuncio.png`, `card_com_logo.png` (na raiz)
- Logo original: `assets/logo_achadinhos_aci.png` (500×500, fundo preto)
- Logo transparente: `assets/logo_achadinhos_aci_transparente.png` (usado nos cards)
- Banner ACI: `assets/logo_aci_banner.png` (1024×558, do site aci.automacoescomerciais.com.br)
- Facebook da marca: "Achadinhos aci" (id 61592454388414) — **sem foto de perfil**
- Links de afiliado da marca: blog `https://aci.automacoescomerciais.com.br/`

## ⚠️ Pendências / pontos de atenção

1. **Preço extraído do link varia entre execuções** (Shopee serve valores diferentes:
   ex. R$ 69,90 → R$ 899,90). Sugerido: **travar preços fixos por produto**.
2. **Anti-bot da Shopee**: a extração do link às vezes falha (1 falha observada) →
   card cai em produto aleatório do sorteio sem foto. Sugerido: **retry (até 3x)** na
   extração antes de desistir.
3. **QR code**: desativado por padrão (`--com-qr` para ativar) — antes atrapalhava a imagem.
4. Pipeline de "imagem profissional" (rembg, fundo branco, 1:1, sombra) estava em
   andamento — `rembg` já instalado no venv; não integrado ao fluxo principal.
5. Gemini: chave direta **inválida** ("API key not valid"); proxy local omniroute
   (porta 20128) não retornou JSON utilizável. Fallback de imagem via Gemini **não funcional**.

## 🔌 Integrações

- **WhatsApp**: Evolution API via `gateways/whatsapp_adapter.py` → grupo `120363411717166242@g.us`
- **Telegram**: bot token no `.env` → envia imagem ao grupo via API
- **Grok 4.6**: `grok_gerar_html()` gera o HTML do card (fallback para templates)
