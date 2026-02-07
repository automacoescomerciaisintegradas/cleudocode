import logging

try:
    from gateways.telegram_adapter import TelegramGateway
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    
try:
    from gateways.discord_adapter import DiscordGateway
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    
try:
    from gateways.whatsapp_adapter import EvolutionGateway
    from gateways.sentient_bridge import sentient_bridge
    WHATSAPP_AVAILABLE = True
    SENTIENT_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    SENTIENT_AVAILABLE = False

def register_telegram(daemon):
    if not TELEGRAM_AVAILABLE: return
    try:
        gw = TelegramGateway()
        # TelegramGateway usa self.tokens (lista) e não self.token
        if gw.tokens:
            daemon.add_gateway(gw)
            logging.info(f"Gateway Telegram registrado com {len(gw.tokens)} bots.")
    except Exception as e:
        logging.error(f"Erro ao registrar Telegram: {e}")

def register_discord(daemon):
    if not DISCORD_AVAILABLE: return
    try:
        gw = DiscordGateway()
        if gw.token:
            daemon.add_gateway(gw)
            logging.info("Gateway Discord registrado.")
    except Exception as e:
        logging.error(f"Erro ao registrar Discord: {e}")

def register_whatsapp(daemon):
    if not WHATSAPP_AVAILABLE: return
    try:
        gw = EvolutionGateway()
        if gw.token and gw.base_url:
            daemon.add_gateway(gw)
            logging.info("Gateway WhatsApp (Evolution) registrado.")
    except Exception as e:
        logging.error(f"Erro ao registrar WhatsApp: {e}")

def register_sentient(daemon):
    if not SENTIENT_AVAILABLE: return
    try:
        print(f"📡 Verificando integração Sentient Grid (Enabled: {sentient_bridge.enabled})...")
        if sentient_bridge.enabled:
            daemon.add_gateway(sentient_bridge)
            logging.info("Gateway Sentient Grid (OML) registrado.")
            print("✅ Gateway Sentient Grid (OML) registrado.")
    except Exception as e:
        logging.error(f"Erro ao registrar Sentient Grid: {e}")
