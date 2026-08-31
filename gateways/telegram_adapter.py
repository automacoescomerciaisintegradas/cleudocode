import logging
import asyncio
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from gateways.base import BaseGateway
from core.config import settings
from core.audio_processor import AudioProcessor
import os
import tempfile

logger = logging.getLogger(__name__)

class TelegramGateway(BaseGateway):
    def __init__(self):
        super().__init__("Telegram")
        self.audio_processor = AudioProcessor()
        # Obtém múltiplos tokens do Telegram
        self.tokens = []

        # Verifica todos os possíveis tokens do Telegram
        token_pairs = [
            ("TELEGRAM_TOKEN", "Telegram_1"),
            ("TELEGRAM_BOT_TOKEN", "Telegram_2"),
            ("TELEGRAM_TOKEN_2", "Telegram_3"),
            ("TELEGRAM_BOT_TOKEN_2", "Telegram_4"),
            ("TELEGRAM_TOKEN_3", "Telegram_5"),
            ("TELEGRAM_BOT_TOKEN_3", "Telegram_6"),
            ("TELEGRAM_TOKEN_4", "Telegram_7"),
            ("TELEGRAM_BOT_TOKEN_4", "Telegram_8"),
            ("TELEGRAM_TOKEN_5", "Telegram_9"),
            ("TELEGRAM_BOT_TOKEN_5", "Telegram_10"),
        ]

        for token_key, bot_name in token_pairs:
            token = settings.get(token_key)
            if token:
                self.tokens.append({
                    'token': token,
                    'name': bot_name,
                    'application': None,
                    'loop': None,
                    'thread': None
                })

        self.bots = []  # Lista de bots ativos
        logger.info(f"[Telegram] Encontrados {len(self.tokens)} tokens de bot(s)")

    def start(self):
        if not self.tokens:
            logger.warning("[Telegram] Nenhum token configurado (TELEGRAM_TOKEN, TELEGRAM_BOT_TOKEN, etc). Ignorando gateway.")
            return

        self.running = True

        for bot_config in self.tokens:
            try:
                self._start_bot(bot_config)
            except Exception as e:
                logger.error(f"[Telegram] Erro ao iniciar bot {bot_config['name']}: {e}")

    def _start_bot(self, bot_config):
        """Inicia um único bot do Telegram"""
        # Build app
        application = ApplicationBuilder().token(bot_config['token']).build()

        # Add Handlers
        # Filtra mensagens de texto e voz
        message_handler = MessageHandler(
            (filters.TEXT | filters.VOICE) & (~filters.COMMAND),
            lambda update, context: self._telegram_callback(update, context, bot_config['name'])
        )
        application.add_handler(message_handler)

        # Armazena referências
        bot_config['application'] = application

        # Thread separada pois python-telegram-bot v20+ usa asyncio
        thread = threading.Thread(
            target=self._run_client,
            args=(bot_config,),
            daemon=True
        )
        bot_config['thread'] = thread
        thread.start()

        # Adiciona à lista de bots ativos
        self.bots.append(bot_config)

        logger.info(f"[{bot_config['name']}] Bot iniciado com sucesso.")

    async def _telegram_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, bot_name: str):
        if not update.message:
            return

        # Evita loop: ignora mensagens enviadas por BOTS (incluindo as nossas próprias
        # e de outros bots que estejam no mesmo grupo). Sem isso, um bot responde à
        # postagem do outro indefinidamente (spam a mesma mensagem/template).
        if getattr(update.message.from_user, "is_bot", False):
            return

        user = update.message.from_user
        chat_id = update.effective_chat.id
        text = ""

        # Verifica se é voz
        if update.message.voice:
            logger.info(f"[{bot_name}] Recebido áudio de {user.first_name}. Transcrevendo...")
            try:
                # Download do arquivo
                voice_file = await context.bot.get_file(update.message.voice.file_id)
                
                with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
                    await voice_file.download_to_drive(tmp.name)
                    tmp_path = tmp.name
                
                # Transcrição
                text = self.audio_processor.transcribe(tmp_path)
                
                # Cleanup
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
                if text.startswith("[Erro"):
                    await update.message.reply_text("Desculpe, tive um problema ao processar seu áudio.")
                    return
                
                logger.info(f"[{bot_name}] Transcrição: {text}")
                # Opcional: Avisar o usuário que transcreveu
                # await update.message.reply_text(f"🎤 Transcrição: {text}")
                
            except Exception as e:
                logger.error(f"Erro ao processar voz: {e}")
                await update.message.reply_text("Erro ao processar áudio.")
                return
        elif update.message.text:
            text = update.message.text
        else:
            return

        logger.debug(f"[{bot_name}] Msg de {user.first_name}: {text}")

        # Envia para Router com identificação do bot
        # Usamos o nome do gateway padrão ("Telegram") mas incluímos o nome do bot nos metadados
        self.incoming_message(
            sender_id=str(chat_id),  # Apenas o chat_id como sender_id
            content=text,
            metadata={
                "username": user.username,
                "first_name": user.first_name,
                "user_id": user.id,
                "bot_name": bot_name,
                "chat_id": chat_id
            }
        )

    async def _setup_polling(self, bot_config):
        application = bot_config['application']
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        logger.info(f"[{bot_config['name']}] Polling iniciado.")

        # Mantém vivo na thread
        while self.running:
            await asyncio.sleep(1)

        await application.updater.stop()
        await application.stop()
        await application.shutdown()

    def _run_client(self, bot_config):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot_config['loop'] = loop
        loop.run_until_complete(self._setup_polling(bot_config))

    def stop(self):
        logger.info("[Telegram] Parando gateway...")
        self.running = False
        logger.info("[Telegram] Gateway parado.")

    def send_message(self, recipient_id: str, message: str, **kwargs):
        # Extrai informações do destinatário
        # Verifica se há informações do bot nos metadados
        metadata = kwargs.get('metadata', {})
        bot_name_from_metadata = metadata.get('bot_name', None)

        # Se tivermos o nome do bot nos metadados, usamos esse
        if bot_name_from_metadata:
            bot_name = bot_name_from_metadata
        else:
            # Caso contrário, tenta extrair do próprio recipient_id
            bot_name = kwargs.get('bot_name', 'Telegram_1')

        # Encontra o bot apropriado
        target_bot = None
        chat_id = recipient_id  # Por padrão, assume que o recipient_id é o chat_id

        for bot_config in self.bots:
            if bot_config['name'] == bot_name:
                target_bot = bot_config
                break

        # Se ainda não encontrou, tenta encontrar qualquer bot
        if not target_bot:
            if self.bots:
                target_bot = self.bots[0]  # Usa o primeiro bot como fallback

        if not target_bot or not target_bot.get('loop') or not self.running:
            logger.error(f"[{bot_name}] Gateway não está rodando ou não encontrado.")
            return

        async def _send():
            try:
                await target_bot['application'].bot.send_message(chat_id=int(chat_id), text=message)
                logger.info(f"[{bot_name}] Mensagem enviada para {chat_id}")
            except Exception as e:
                logger.error(f"[{bot_name}] Erro envio: {e}")

        asyncio.run_coroutine_threadsafe(_send(), target_bot['loop'])

    def send_image(self, chat_id: str, image_path_or_bytes, caption: str = "", bot_name: str = None):
        """Envia uma imagem para o chat via telegram.

        AdaptiveResolution não muda nada aqui; python-telegram-bot faz o upload.
        Aceita caminho de arquivo, bytes ou objeto de arquivo.
        """
        target_bot = None
        for bc in self.bots:
            if bot_name and bc['name'] == bot_name:
                target_bot = bc
                break
        if not target_bot and self.bots:
            target_bot = self.bots[0]
        if not target_bot or not target_bot.get('loop') or not self.running:
            logger.error("[Telegram] Gateway não está rodando p/ envio de imagem.")
            return False

        async def _send_img():
            try:
                await target_bot['application'].bot.send_photo(chat_id=int(chat_id), photo=image_path_or_bytes, caption=caption)
                logger.info(f"[{target_bot['name']}] Imagem enviada para {chat_id}")
            except Exception as e:
                logger.error(f"[{target_bot['name']}] Erro envio imagem: {e}")

        asyncio.run_coroutine_threadsafe(_send_img(), target_bot['loop'])
        return True
