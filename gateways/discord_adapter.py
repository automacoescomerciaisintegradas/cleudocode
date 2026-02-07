import logging
import discord
import asyncio
import threading
from gateways.base import BaseGateway
from core.config import settings

logger = logging.getLogger(__name__)

class DiscordGateway(BaseGateway):
    def __init__(self):
        super().__init__("Discord")
        self.token = settings.get("DISCORD_TOKEN")
        
        # Intents necessários
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True  # CRITICAL: Necessário para ler o conteúdo
        intents.dm_messages = True
        
        self.client = discord.Client(intents=intents)
        self.loop = None
        self.thread = None

        # Bind events
        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    def start(self):
        if not self.token:
            logger.warning("[Discord] Token não configurado (DISCORD_TOKEN). Ignorando gateway.")
            return

        self.running = True
        # Discord.py roda em asyncio event loop. Precisamos de uma thread separada se o main não for async.
        self.thread = threading.Thread(target=self._run_client, daemon=True)
        self.thread.start()

    def _run_client(self):
        # Cria um loop para essa thread
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.client.start(self.token))
        except Exception as e:
            logger.error(f"[Discord] Erro fatal no cliente: {e}")

    def stop(self):
        logger.info("[Discord] Parando gateway...")
        if self.loop and self.client:
            # Agenda o fechamento thread-safe
            asyncio.run_coroutine_threadsafe(self.client.close(), self.loop)
        self.running = False

    async def on_ready(self):
        logger.info(f"[Discord] Logado como {self.client.user} (ID: {self.client.user.id})")

    async def on_message(self, message):
        # Ignora mensagens do próprio bot
        if message.author == self.client.user:
            return

        # Ignora mensagens vazias ou de sistema (opcional)
        if not message.content:
            return

        logger.debug(f"[Discord] Msg de {message.author}: {message.content}")
        
        # Envia para o Router processar
        # sender_id é string combinando channel_id para podermos responder no mesmo lugar
        sender_ref = str(message.channel.id) 
        
        self.incoming_message(
            sender_id=sender_ref,
            content=message.content,
            metadata={
                "author": message.author.name,
                "author_id": message.author.id,
                "is_dm": isinstance(message.channel, discord.DMChannel)
            }
        )

    def send_message(self, recipient_id: str, message: str, **kwargs):
        """
        Envia mensagem de volta.
        recipient_id aqui é o channel_id que veio no sender_id.
        """
        if not self.loop:
            logger.error("[Discord] Loop não iniciado, impossível enviar mensagem.")
            return

        async def _send():
            try:
                channel = self.client.get_channel(int(recipient_id))
                if channel:
                    await channel.send(message)
                else:
                    # Se não achou cache, tenta fetch (mais lento, mas seguro)
                    try:
                        channel = await self.client.fetch_channel(int(recipient_id))
                        await channel.send(message)
                    except:
                        logger.error(f"[Discord] Canal {recipient_id} não encontrado.")
            except Exception as e:
                logger.error(f"[Discord] Erro ao enviar para {recipient_id}: {e}")

        # Agenda a coroutine no loop do Discord
        asyncio.run_coroutine_threadsafe(_send(), self.loop)
