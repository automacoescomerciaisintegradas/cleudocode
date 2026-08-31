#!/usr/bin/env python3
"""
Disparo em Massa (Volume Baixo a Médio)
Agente Shopee -> Contatos CRM
Configuração recomendada: Delay de 8 segundos entre disparos.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from gateways.whatsapp_adapter import EvolutionGateway
from orchestrator import orchestrator
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MassBroadcast")

DELAY_SEGUNDOS = 8
PRODUTO_OFERTA = "Smartwatch lançamento com GPS e NFC" # Pode ser passado como argumento

def obter_leads_via_mcp():
    URL = "http://127.0.0.1:65000/mcp"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "listar_leads",
            "arguments": {}
        }
    }
    import json
    try:
        resp = requests.post(URL, json=payload, timeout=10)
        data = resp.json()
        leads_str = data["result"]["content"][0]["text"]
        leads_json = json.loads(leads_str)
        return leads_json.get("leads", [])
    except Exception as e:
        logger.error(f"Erro ao pescar leads do CRM MCP: {e}")
        return []

def mass_broadcast():
    gw = EvolutionGateway()
    if not gw.token:
        logger.error("Gateway WhatsApp ausente.")
        return

    leads = obter_leads_via_mcp()
    if not leads:
        logger.warning("Nenhum lead encontrado no CRM/MCP. Encerrando rotina de disparo.")
        return

    logger.info(f"🚀 Iniciando Disparo em Massa. Total de Leads: {len(leads)}")
    logger.info(f"⏱️ Delay configurado entre disparos: {DELAY_SEGUNDOS} segundos.")
    
    # 1. Gerar a copy da oferta usando a inteligência do agente shopee
    prompt = f"Gere uma mensagem direta e curta vendendo: {PRODUTO_OFERTA}. Lembre que é uma mensagem privada no WhatsApp. Traga escassez."
    result = orchestrator.receive_message({"text": prompt, "from": "cron", "targeted_agent": "shopee_agent"})
    texto_oferta = result.get("result", {}).get("output", "🚨 Mega oferta liberada hoje!!! Corre no nosso canal!")
    
    sucessos = 0
    
    # 2. Executar o Loop de Disparo com os delays calculados para anti-ban
    for idx, lead in enumerate(leads):
        nome = lead.get("name", "Cliente")
        telefone = lead.get("phone")
        if not telefone:
            continue
            
        jid = f"{telefone}@s.whatsapp.net" if "@" not in telefone else telefone
        
        # Personaliza a mensagem
        mensagem_final = f"Oi {nome}! 🎉\n\n{texto_oferta}"
        
        logger.info(f"Enviando para {nome} ({telefone})... [Lead {idx+1}/{len(leads)}]")
        ok = gw.send_message(jid, mensagem_final)
        
        if ok:
            sucessos += 1
            
        # Delay de Anti-Spam (8s recomendado para low volume)
        if idx < len(leads) - 1:
            logger.info(f"⏳ Aguardando {DELAY_SEGUNDOS}s por segurança (política Anti-Ban)...")
            time.sleep(DELAY_SEGUNDOS)

    logger.info(f"✅ Disparo Concluído! Entregue para {sucessos} de {len(leads)} leads.")

if __name__ == "__main__":
    # Respeita a flag do bot (bot_gate.sh on/off): só dispara com o bot ligado.
    if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".bot_on")):
        logger.warning("Bot OFF (sem flag .bot_on). Disparo em massa bloqueado.")
        sys.exit(0)
    mass_broadcast()
