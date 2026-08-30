#!/usr/bin/env python3
"""
Gerador de cards promocionais para o grupo Ofertas Shopee.

Pipeline:
  1. Sorteia um produto bombando
  2. Pede ao Grok 4.6 para montar o HTML do card promocional (em código)
  3. Renderiza o HTML → PNG via Chrome headless
  4. Envia a imagem para os grupos WhatsApp (Evolution) e Telegram

Uso:
    python3 gerador_ofertas_imagem.py              # gera + envia para todos os canais
    python3 gerador_ofertas_imagem.py --produto "X"  # fixa o produto
    python3 gerador_ofertas_imagem.py --envio-texto   # envia só texto (sem imagem)
"""
import os
import sys
import re
import base64
import random
import subprocess
import tempfile
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GeradorOfertas")

from gateways.whatsapp_adapter import EvolutionGateway

GROK_BIN = os.getenv("GROK_BIN", "/root/.grok/bin/grok")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-4.6")
CHROME_BIN = os.getenv("CHROME_BIN", "/usr/local/bin/google-chrome")

# Grupos de destino
WHATSAPP_GROUP = os.getenv("WHATSAPP_SHOPEE_GROUP", "120363411717166242@g.us")
TELEGRAM_GROUP = os.getenv("TELEGRAM_SHOPEE_GROUP", "-1001834086191")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Produto -> link de afiliado Shopee (link real/colocado aqui conforme coletado)
PRODUTOS = [
    ("Fone de Ouvido Bluetooth Lenovo XT88 TWS Original", "https://s.shopee.com.br/1gHF6AhoQc"),
    ("Fritadeira Air Fryer Mondial 4 Litros", "https://s.shopee.com.br/1gHF6AhoQc"),
    ("Relógio Smartwatch Pela Metade do Preço", "https://s.shopee.com.br/1gHF6AhoQc"),
    ("Robô Aspirador Inteligente Bivolt Multi Superfícies", "https://s.shopee.com.br/1gHF6AhoQc"),
    ("Kit Skincare Essencial", "https://s.shopee.com.br/1gHF6AhoQc"),
    ("SSD Kingston 480GB de alta velocidade", "https://s.shopee.com.br/1gHF6AhoQc"),
    ("Kit Pincéis de Maquiagem Profissionais", "https://s.shopee.com.br/1gHF6AhoQc"),
    ("Smart TV 32 Polliciosa HD", "https://s.shopee.com.br/1gHF6AhoQc"),
    ("Cafeteira Espresso Elétrica 3 em 1", "https://s.shopee.com.br/1gHF6AhoQc"),
    ("Ventilador de Coluna Turbo 40cm", "https://s.shopee.com.br/1gHF6AhoQc"),
]
# Se --produto vier sem link, usa este link padrão da loja
DEFAULT_SHOPEE_LINK = "https://s.shopee.com.br/1gHF6AhoQc"

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# Templates de card disponíveis (visuais + CTAs variados)
TEMPLATES = [
    {"arquivo": "card_imperdivel.html", "preco_antes": "R$ 1.899,90"},
    {"arquivo": "card_relampago.html", "preco_antes": "R$ 1.599,90"},
    {"arquivo": "card_profissional.html", "preco_antes": "R$ 1.799,90"},
    {"arquivo": "card_desconto.html", "preco_antes": "R$ 2.599,90"},
    {"arquivo": "card_hotdeal.html", "preco_antes": "R$ 1.999,90"},
    {"arquivo": "card_anuncio.html", "preco_antes": "R$ 1.699,90"},
]


def random_preco(produto):
    """Gera um preço 'garimpado' realista para o card."""
    if "Fone" in produto: return "R$ 89,90"
    if "Air Fryer" in produto: return "R$ 249,90"
    if "Smartwatch" in produto: return "R$ 119,90"
    if "Aspirador" in produto: return "R$ 399,90"
    if "Skincare" in produto: return "R$ 49,90"
    if "SSD" in produto: return "R$ 159,90"
    if "Pincéis" in produto: return "R$ 69,90"
    if "TV" in produto: return "R$ 899,90"
    if "Cafeteira" in produto: return "R$ 199,90"
    if "Ventilador" in produto: return "R$ 129,90"
    return f"R$ {random.randint(49, 899)},{random.randint(10, 99)}"


def gerar_qr_datauri(link):
    """Gera um QR code do link em base64 data URI para embutir no HTML."""
    try:
        import qrcode
        import io
        import base64 as b64
        qr = qrcode.QRCode(border=3, box_size=12, error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, "PNG")
        return "data:image/png;base64," + b64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        logger.warning(f"QR não gerado: {e}")
        return None


def injetar_link_no_html(html, link, mostrar_qr=False):
    """Garante que o card (seja do Grok ou do template) mostre o link do produto
    APENAS no rodapé. Idempotente: se o HTML já tiver uma barra de link (class
    "linkbar") ou o próprio link presente num elemento dedicado de rodapé, não
    injeta de novo (evita link duplicado sobre a imagem). Também remove links
    soltos (âncoras <a>) que o Grok possa ter colado no corpo do card.

    Com mostrar_qr=True inclui o QR; caso contrário, só o link em destaque."""
    # Já tem barra de rodapé dedicada (rote própria / injetada antes) → não duplica
    if "linkbar" in html or 'role="linkbar"' in html:
        return html

    # Remove âncoras soltas do corpo (o Grok às vezes cola o link sobre a imagem),
    # aceitando aspas simples ou duplas no href.
    html = re.sub(r'<a\s[^>]*href=["\'][^"\']*["\'][^>]*>.*?</a>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove qualquer URL solta/como texto que tenha sobrado no corpo (ex.: colada sem <a>)
    html = re.sub(r'(https?://)?(s\.shopee\.com\.br|shopee\.com\.br|affiliate\.shopee\.com\.br)[\S]*', '', html)

    qr = gerar_qr_datauri(link) if mostrar_qr else None
    qr_img = ""
    if qr:
        qr_img = ('<img src="' + qr + '" '
                  'style="width:110px;height:110px;background:#fff;border-radius:12px;padding:6px;'
                  'box-shadow:0 4px 10px rgba(0,0,0,.25)"/>')
    height = "150px" if mostrar_qr else "96px"
    qr_style = "gap:18px" if mostrar_qr else "gap:6px;flex-direction:column;align-items:flex-start;justify-content:center"
    lbl_style = "font-weight:800;font-size:22px" if not mostrar_qr else "font-weight:800;font-size:22px"
    url_style = ("font-size:22px;font-weight:700;color:#ffe24d;word-break:break-all"
                 if mostrar_qr else "font-size:28px;font-weight:800;color:#ffe24d;word-break:break-all")
    block = ('<div role="linkbar" style="position:fixed;left:0;right:0;bottom:0;height:' + height + ';'
             'background:rgba(0,0,0,.68);display:flex;align-items:center;' + qr_style + ';padding:0 34px;">'
             + qr_img +
             '<div style="color:#fff;min-width:0">'
             '<div style="' + lbl_style + '">📲 Garanta seu desconto 👉</div>'
             '<div style="' + url_style + '">' + link + '</div></div></div>')
    if "</body>" in html:
        html = html.replace("</body>", block + "</body>").replace("</html>", "")
    else:
        html = html.replace("</html>", "").rstrip() + block
    html += "</html>"
    return html


def grok_gerar_html(produto, preco, link, saida_path):
    """Pede ao Grok 4.6 para montar o HTML do card promocional."""
    prompt = (
        f"Gere APENAS o código HTML completo de um card promocional quadrado 800x800px "
        f"para a oferta da Shopee do produto: '{produto}' por {preco} com FRETE GRÁTIS. "
        f"Use CSS inline apenas (sem arquivos externos, sem import, sem links), "
        f"background com degrade vibrante de vendas (verde/amarelo/laranja), "
        f"nome do produto grande em negrito, preço destacado em vermelho, "
        f"selo PROMOÇÃO, selo FRETE GRÁTIS, e hashtags pequenas no rodapé "
        f"(ex: #Shopee #Promoção #FreteGrátis). "
        f"Todo o texto deve estar em português. Deixe espaço livre (sem sobreposição) na parte inferior "
        f"do card para acomodar uma barra de link/QR. NÃO escreva texto explicativo fora do HTML. "
        f"Salve o arquivo completo em {saida_path}"
    )
    cmd = [
        GROK_BIN, "-m", GROK_MODEL,
        "--output-format", "plain",
        "--permission-mode", "bypassPermissions",
        "--cwd", os.path.dirname(saida_path),
        "-p", prompt,
    ]
    logger.info("🎨 Pedindo ao Grok para montar o card...")
    try:
        subprocess.run(cmd, timeout=150, check=False)
    except Exception as e:
        logger.error(f"❌ Falha ao chamar o Grok: {e}")
        return None
    if os.path.exists(saida_path) and os.path.getsize(saida_path) > 500:
        logger.info(f"✅ HTML do card gerado ({os.path.getsize(saida_path)} bytes)")
        return saida_path
    # fallback: extrai o bloco HTML da saída do Grok caso ele não tenha salvo
    logger.warning("Grok não salvou o arquivo; tentando extrair do stdout...")
    return None


def baixar_imagem_datauri(origem):
    """Baixa (URL) ou lê (caminho local) uma imagem e retorna como data URI base64.
    Retorna None se falhar."""
    if not origem:
        return None
    import base64 as b64
    try:
        if origem.startswith("http://") or origem.startswith("https://"):
            import requests
            r = requests.get(origem, timeout=30,
                             headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            r.raise_for_status()
            dados = r.content
            ct = r.headers.get("content-type", "").split(";")[0].strip().lower()
        else:
            with open(origem, "rb") as f:
                dados = f.read()
            ext = os.path.splitext(origem)[1].lower().lstrip(".")
            ct = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "gif": "image/gif"}.get(ext, "image/png")
        if not dados:
            return None
        return "data:" + ct + ";base64," + b64.b64encode(dados).decode()
    except Exception as e:
        logger.warning(f"Não foi possível carregar imagem ({origem[:60]}...): {e}")
        return None


# Foto real de cada produto: preencha manualmente {"palavra do produto": "URL da foto ou caminho"},
# OU use links de produto/afiliado em PRODUTOS (abaixo) para a foto ser baixada automaticamente.
PRODUTOS_IMAGEM = {}


def baixar_foto_e_dados_do_link(link):
    """Resolve um link de produto da Shopee (curto s.shopee... ou shopee.com.br/product/...) e
    extrai a foto real do produto (além de nome/preço quando disponíveis).

    Retorna dict {'imagem': bytes, 'imagem_tipo': str, 'nome': str|None, 'preco': str|None}
    ou None se não conseguir."""
    import re
    try:
        import requests
        ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}

        def _fetch(url: str) -> requests.Response:
            return requests.get(url, headers=ua, timeout=30, allow_redirects=True)

        r = _fetch(link)
        html = r.text
        conf = {"link_final": r.url}

        # Links curtos (s.shopee...) caem na versão MOBILE (opaanlp/<shopId>/<itemId>?__mobile__=1),
        # cujo HTML não traz og:title nem as imagens. Se sinal de mobile, reconstruímos a URL
        # desktop (/product/<shopId>/<itemId>) e refazemos o fetch — onde o HTML é completo.
        def _is_mobile(url: str) -> bool:
            return "__mobile__" in url or "/opaanlp/" in url

        if _is_mobile(r.url):
            m = re.search(r'/opaanlp/(\d+)/(\d+)', r.url)
            if m:
                desktop = f"https://shopee.com.br/product/{m.group(1)}/{m.group(2)}"
                try:
                    r2 = _fetch(desktop)
                    if r2.status_code == 200 and len(r2.text) > 20000:
                        html = r2.text
                        conf["link_final"] = desktop
                except Exception:
                    pass

        # --- foto do produto ---
        # CDN real: https://down-<reg>.img.susercontent.com/file/<hash>.webp
        # (logotipos/footer também usam esse CDN; filtramos pelo tamanho do hash)
        fotos = re.findall(r'usercontent\.com/file/([a-zA-Z0-9_-]{24,})(?:@resize_w\d+_nl)?\.webp', html)
        if fotos:
            h = fotos[0]
            conf["imagem"] = f"https://down-br.img.susercontent.com/file/{h}@resize_w900_nl.webp"
            conf["imagem_tipo"] = "image/webp"

        # --- nome do produto ---
        m = re.search(r'property="og:title" content="([^"]+)"', html)
        if m:
            conf["nome"] = m.group(1).replace(" | Shopee Brasil", "").strip()

        # --- preço (JSON embutido) ---
        # padrão típico "price":123 ou "price_min":123 em centavos
        pm = re.search(r'"price(?:_min)?"\s*:\s*(\d+)', html)
        if pm:
            cent = int(pm.group(1))
            conf["preco"] = f"R$ {cent//100},{cent%100:02d}"

        return conf
    except Exception as e:
        logger.warning(f"não foi possível obter dados do link {link}: {e}")
        return None


def render_template_card(produto, preco, link, saida_path, preco_antes=None, arquivo=None, mostrar_qr=False, imagem=None):
    """Renderiza um dos templates de card (visual + CTA variados), embutindo QR/link.

    Se arquivo=None, sorteia um template da lista TEMPLATES. Retorna o caminho do
    HTML gerado. Com mostrar_qr=False, o QR é escondido e o link ganha destaque.
    """
    # escolhe template
    if arquivo:
        templ_def = {"arquivo": arquivo, "preco_antes": preco_antes or "R$ 1.799,90"}
    else:
        templ_def = random.choice(TEMPLATES)
        if preco_antes:
            templ_def = dict(templ_def, preco_antes=preco_antes)
    templ = os.path.join(TEMPLATE_DIR, templ_def["arquivo"])
    try:
        with open(templ, encoding="utf-8") as f:
            html = f.read()
    except Exception as e:
        logger.error(f"Template não encontrado ({templ}): {e}")
        return None
    p_ant = templ_def.get("preco_antes") or "R$ 1.799,90"
    qr = gerar_qr_datauri(link) or ""
    # Se não mostrar QR, esconde o bloco do QR e dá destaque total ao link
    if mostrar_qr:
        qr_html = qr
        css = ""
    else:
        qr_html = ""
        css = (".linkqr{display:none!important} "
               ".linkbar{flex-direction:column;align-items:flex-start!important;gap:6px!important} "
               ".linktxt{width:100%} "
               ".linktxt .url{font-size:26px!important;display:block}")
        # remove o <img> do QR caso o template o deixe com src vazio
        html = html.replace("<img class=\"linkqr\" src=\"{{QR_IMG}}\" alt=\"QR\"/>", "")
    # Imagem do produto: prioriza o parâmetro imagem; senão, vê se há foto mapeada p/ o produto
    if imagem is None:
        for k, v in PRODUTOS_IMAGEM.items():
            if k.lower() in produto.lower():
                imagem = v
                break
    img_uri = baixar_imagem_datauri(imagem) or ""
    # logo da marca no header (data URI p/ funcionar no render headless)
    logo_aci = baixar_imagem_datauri(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "assets", "logo_achadinhos_aci_transparente.png")) or ""
    html = (html.replace("{{PRODUTO}}", produto)
               .replace("{{PRECO}}", preco)
               .replace("{{PRECO_ANTES}}", p_ant)
               .replace("{{QR_IMG}}", qr)
               .replace("{{LINK}}", link)
               .replace("{{PRODUTO_IMG}}", img_uri)
               .replace("{{LOGO_ACI}}", logo_aci))
    if css:
        html = html.replace("<head>", "<head><style>" + css + "</style>")
    with open(saida_path, "w", encoding="utf-8") as f:
        f.write(html)
    return saida_path


def render_html_to_png(html_path, png_path, largura=800, altura=800):
    """Renderiza o HTML → PNG via Chrome headless."""
    cmd = [
        CHROME_BIN, "--headless", "--no-sandbox", "--disable-gpu",
        "--hide-scrollbars", "--force-device-scale-factor=2",
        f"--window-size={largura},{altura}",
        f"--screenshot={png_path}",
        html_path,
    ]
    try:
        subprocess.run(cmd, timeout=60, check=True, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"❌ Falha na renderização Chrome: {e}")
        return None
    if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
        logger.info(f"✅ Card renderizado: {png_path} ({os.path.getsize(png_path)} bytes)")
        return png_path
    logger.error("❌ Renderização não produziu imagem.")
    return None


def enviar_whatsapp(png_path, caption):
    gw = EvolutionGateway()
    if not gw.token or not gw.base_url:
        logger.error("WhatsApp (Evolution) não configurado.")
        return False
    ok = gw.send_image(WHATSAPP_GROUP, png_path, caption=caption)
    logger.info(f"🟢 WhatsApp: {'enviado' if ok else 'FALHOU'}")
    return ok


def enviar_telegram(png_path, caption):
    """Envia a imagem para o grupo Telegram via API HTTP do bot (sem depender do gateway)."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN não configurado; pulando Telegram.")
        return False
    import requests
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open(png_path, "rb") as f:
            resp = requests.post(
                url,
                data={"chat_id": TELEGRAM_GROUP, "caption": caption},
                files={"photo": (os.path.basename(png_path), f, "image/png")},
                timeout=60,
            )
        if resp.status_code == 200 and resp.json().get("ok"):
            logger.info("🔵 Telegram: imagem enviada ao grupo.")
            return True
        logger.error(f"Telegram: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        logger.error(f"❌ Falha envio Telegram: {e}")
    return False


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--produto", default=None)
    ap.add_argument("--link", default=None)
    ap.add_argument("--preco", default=None)
    ap.add_argument("--template", default=None,
                    help="arquivo do template (ex: card_relampago.html). Sem ele, sorteia se usar fallback.")
    ap.add_argument("--skip-grok", action="store_true",
                    help="pula o Grok e usa direto o template (mais rápido; ideal para a rotina cron)")
    ap.add_argument("--com-qr", action="store_true",
                    help="mostra o QR code no card (por padrão o link aparece como texto grande, sem QR)")
    ap.add_argument("--imagem", default=None,
                    help="URL ou caminho local da foto do produto a ser exibida no card")
    ap.add_argument("--solo-html", action="store_true", help="só gera o PNG, não envia")
    ap.add_argument("--sem-telegram", action="store_true")
    ap.add_argument("--sem-whatsapp", action="store_true")
    args = ap.parse_args()

    if args.produto:
        produto = args.produto
        link = args.link or DEFAULT_SHOPEE_LINK
    else:
        produto, _link = random.choice(PRODUTOS)
        link = args.link or _link
    preco = args.preco or random_preco(produto)

    # Tenta extrair a foto real (e nome/preço) do produto a partir do link,
    # para o card sempre sair com a imagem — mesmo que o produto seja novo.
    imagem = args.imagem
    dados_link = None
    if link:
        try:
            dados_link = baixar_foto_e_dados_do_link(link)
        except Exception as e:
            logger.warning(f"não foi possível extrair dados do link: {e}")
    if dados_link:
        if not imagem and dados_link.get("imagem"):
            imagem = dados_link["imagem"]
        # se o usuário não especificou nome/preço, aproveita o que veio do link
        if not args.produto and dados_link.get("nome"):
            produto = dados_link["nome"]
        if not args.preco and dados_link.get("preco"):
            preco = dados_link["preco"]

    # escolhe o template (fixo via --template, ou sorteia um para o fallback)
    if args.template:
        template_def = {"arquivo": args.template, "preco_antes": "R$ 1.899,90"}
    else:
        template_def = random.choice(TEMPLATES)
    logger.info(f"🛍️ Oferta sorteada: {produto} — {preco}\n🔗 link: {link}\n🎨 template: {template_def['arquivo']}")

    tmp = tempfile.mkdtemp(prefix="oferta_shopee_")
    html_path = os.path.join(tmp, "card.html")
    png_path = os.path.join(tmp, "card.png")

    skip_grok = args.skip_grok or os.getenv("USE_GROK", "1").lower() in ("0", "false", "no")

    gerado = None
    if not skip_grok:
        gerado = grok_gerar_html(produto, preco, link, html_path)
    if not gerado or not os.path.exists(html_path) or os.path.getsize(html_path) < 500:
        if skip_grok:
            logger.info("⚡ Modo rápido: usando template diretamente.")
        else:
            logger.warning("⚠️ Grok não gerou o HTML; usando template de fallback.")
        render_template_card(produto, preco, link, html_path,
                             preco_antes=template_def.get("preco_antes"),
                             arquivo=template_def["arquivo"],
                             mostrar_qr=args.com_qr,
                             imagem=imagem)
        template_usado = template_def["arquivo"]
    else:
        template_usado = "grok (geração própria)"
        # Garante que o link/QR esteja no card mesmo quando o Grok gera
        try:
            with open(html_path, encoding="utf-8") as f:
                html = f.read()
            html = injetar_link_no_html(html, link, mostrar_qr=args.com_qr)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            logger.warning(f"Não foi possível injetar link no HTML do Grok: {e}")

    png = render_html_to_png(html_path, png_path)
    if not png:
        return 1

    if args.solo_html:
        print(f"\n✅ Card gerado: {png}\n   Produto: {produto} — {preco}")
        return 0

    caption = (f"🔥 {produto} por {preco} — FRETE GRÁTIS! 👉 {link}\n"
               f"\n🪧 Aviso Importante: Comprando pelo nosso link, você ajuda o canal sem pagar nada a mais por isso!\n"
               f"⚠️ Preço e estoque dos produtos estão sujeitos a alteração.\n"
               f"#OfertasShopee #Promoção")
    resp_wa = resp_tg = None
    if not args.sem_whatsapp:
        resp_wa = enviar_whatsapp(png, caption)
    if not args.sem_telegram:
        resp_tg = enviar_telegram(png, caption)

    print(f"\n📊 Resultado:\n  Produto: {produto} ({preco})\n"
          f"  Template: {template_usado}\n"
          f"  WhatsApp: {'✅' if resp_wa else '❌'}\n"
          f"  Telegram: {'✅' if resp_tg else '❌'}\n"
          f"  Card salvo em: {png}")
    return 0 if (resp_wa or resp_tg) else 1


if __name__ == "__main__":
    sys.exit(main())