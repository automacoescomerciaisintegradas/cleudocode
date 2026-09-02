#!/usr/bin/env python3
import os
import sys
import time
import random
import logging
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from gateways.whatsapp_adapter import EvolutionGateway
from orchestrator import orchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ShopeePromoter")

GROUP_JID = "120363411717166242@g.us"
INTERVALO_HORAS = 4 # Intervalo em horas entre envios

PRODUTOS_BOMBANDO = [
    "Fone de Ouvido Bluetooth Lenovo XT88 TWS Original",
    "Fritadeira Air Fryer Mondial 4 Litros",
    "Relógio Smartwatch Pela Metade do Preço",
    "Robô Aspirador Inteligente Bivolt Multi Superfícies",
    "Kit Skincare Essencial",
    "SSD Kingston 480GB de alta velocidade",
    "Kit Pincéis de Maquiagem Profissionais"
]

def gerar_e_enviar_oferta():
    gw = EvolutionGateway()
    
    if not gw.token or not gw.base_url:
        logger.error("Gateway WhatsApp (Evolution) não está configurado no .env")
        return
        
    produto_sorteado = random.choice(PRODUTOS_BOMBANDO)
    
    logger.info(f"🛍️ Gerando nova copy de oferta para: {produto_sorteado}")
    
    prompt_pedido = (
        f"Gere AGORA uma postagem promocional bombástica, persuasiva mas realista (sem promessas falsas), "
        f"especial para o grupo de ofertas, vendendo o produto: {produto_sorteado}. "
        f"Finja que você acabou de garimpar essa promoção. Use hashtags e crie um link fictício curto da shopee "
        f"para os membros clicarem, lembrando de frete grátis."
    )
    
    try:
        # Usa o orquestrador mirando na persona shopee_agent configurada recentemente
        result = orchestrator.receive_message({
            "text": prompt_pedido, 
            "from": "sistema_interno", 
            "targeted_agent": "shopee_agent"
        })
        
        texto_oferta = result.get("result", {}).get("output", "")
        
        if texto_oferta:
            logger.info("📝 Copy gerada com sucesso. Enviando para Evolution API...")
            sucesso = gw.send_message(GROUP_JID, texto_oferta)
            if sucesso:
                logger.info(f"✅ Postagem divulgada no grupo com sucesso!")
            else:
                logger.error("❌ Falha na confirmação de entrega via Evolution API.")
        else:
            logger.error("❌ O orquestrador IA não retornou o texto sugerido.")
            
    except Exception as e:
        logger.error(f"❌ Exceção gravíssima rodando o promotor: {e}")

if __name__ == "__main__":
    logger.info(f"🚀 Shopee Promoter Daemon ativado! Alvo: Grupo {GROUP_JID} a cada {INTERVALO_HORAS} horas.")
    
    # Gatilho imediato para atestar o funcionamento na hora que lançar o script
    gerar_e_enviar_oferta()
    
    while True:
        segundos = INTERVALO_HORAS * 3600
        logger.info(f"🕒 Aguardando {INTERVALO_HORAS} horas para a próxima caçada de ofertas...")
        time.sleep(segundos)
        gerar_e_enviar_oferta()
