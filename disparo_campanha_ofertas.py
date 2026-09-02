#!/usr/bin/env python3
"""Disparo em Massa via WhatsApp (Evolution API).

Lê os contatos reais de `telefones_contatos.csv` (colunas `nome`,`telefone`) e
envia a oferta promocional. Filtra apenas números válidos do Brasil (55 + DDD +
número), deduplica e respeita a flag do bot (`bot_gate.sh on/off`).

Configuração recomendada: delay de 8s entre envios e limite por execução
(`MAX_DISPATCH`, padrão 50) para evitar bloqueio da conta.
"""

import os
import sys
import csv
import re
import time
import logging
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from gateways.whatsapp_adapter import EvolutionGateway
from orchestrator import orchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MassBroadcast")

DELAY_SEGUNDOS = int(os.getenv("DELAY_SEGUNDOS", "8"))
MAX_DISPATCH = int(os.getenv("MAX_DISPATCH", "50"))  # limite de envios por execução
ARQUIVO_CONTATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telefones_contatos.csv")
PRODUTO_OFERTA = os.getenv("PRODUTO_OFERTA", "Smartwatch lançamento com GPS e NFC")


def carregar_contatos():
    """Lê o CSV e devolve lista de (nome, telefone_br_normalizado) válidos."""
    if not os.path.exists(ARQUIVO_CONTATOS):
        logger.error(f"CSV de contatos não encontrado: {ARQUIVO_CONTATOS}")
        return []
    contatos = []
    vistos = set()
    with open(ARQUIVO_CONTATOS, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            t = re.sub(r"\D", "", row.get("telefone") or "")
            # só número válido do Brasil: 55 + DDD(2) + 8/9 dígitos
            if not re.fullmatch(r"55\d{10,11}", t):
                continue
            if t in vistos:
                continue
            vistos.add(t)
            contatos.append(((row.get("nome") or "Cliente").strip(), t))
    return contatos


def gerar_copy_oferta():
    """Gera a mensagem da oferta usando o agente shopee (com fallback)."""
    try:
        prompt = (f"Gere uma mensagem direta e curta vendendo: {PRODUTO_OFERTA}. "
                  f"Lembre que é uma mensagem privada no WhatsApp. Traga escassez. "
                  f"Responda apenas o texto da mensagem, em português, sem aspas.")
        result = orchestrator.receive_message({"text": prompt, "from": "cron", "targeted_agent": "shopee_agent"})
        texto = result.get("result", {}).get("output", "").strip()
        if texto and not texto.lower().startswith("desculpe"):
            return texto
    except Exception as e:
        logger.error(f"Erro ao gerar copy: {e}")
    return "🚨 Mega oferta liberada hoje!!! Corre no nosso canal!"


def mass_broadcast():
    gw = EvolutionGateway()
    if not gw.token or not gw.base_url:
        logger.error("Gateway WhatsApp (Evolution) não configurado no .env")
        return

    # ===== REGRA ANTI-BAN =====
    # SÓ envia para grupos/comunidades autorizados (WHATSAPP_TARGET_NUMBER @g.us/@newsletter/@lid).
    # NUNCA envia para números privados (@s.whatsapp.net).
    alvos = [a.strip() for a in os.getenv("WHATSAPP_TARGET_NUMBER", "").split(",") if a.strip()]
    alvos = [a for a in alvos if a.endswith(("@g.us", "@newsletter", "@lid"))]
    if not alvos:
        logger.error("Bloqueado: nenhum destino de grupo autorizado em WHATSAPP_TARGET_NUMBER. "
                     "Disparo em massa para números privados está DESATIVADO.")
        return
    logger.info(f"📢 Destinos autorizados ({len(alvos)} grupos/comunidades): {len(alvos)} grupos.")

    contatos = carregar_contatos()
    if not contatos:
        logger.warning("Nenhum contato válido (telefones do Brasil) encontrado no CSV.")
        return

    # respeita o limite e o agendamento do bot
    lote = contatos[:MAX_DISPATCH]
    logger.info(f"🚀 Iniciando Disparo em Massa. Total de contatos válidos no CSV: {len(contatos)} — "
                f"enviando {len(lote)} nesta execução (MAX_DISPATCH={MAX_DISPATCH}).")

    texto_oferta = gerar_copy_oferta()

    sucessos = 0
    for idx, (nome, telefone) in enumerate(lote, start=1):
        jid = f"{telefone}@s.whatsapp.net"
        mensagem = f"Oi {nome}! 🎉\n\n{texto_oferta}"
        try:
            ok = gw.send_message(jid, mensagem)
        except Exception as e:
            logger.error(f"Erro/Exceção para {nome} ({telefone}): {e}")
            ok = False
        if ok:
            sucessos += 1
            logger.info(f"✅ [{idx}/{len(lote)}] {nome} ({telefone})")
        else:
            logger.warning(f"❌ [{idx}/{len(lote)}] {nome} ({telefone})")
        if idx < len(lote):
            time.sleep(DELAY_SEGUNDOS)

    logger.info(f"✅ Disparo Concluído! Entregou para {sucessos} de {len(lote)} contatos.")


if __name__ == "__main__":
    # Respeita a flag do bot (bot_gate.sh on/off): só dispara com o bot ligado.
    if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".bot_on")):
        logger.warning("Bot OFF (sem flag .bot_on). Disparo em massa bloqueado.")
        sys.exit(0)
    mass_broadcast()