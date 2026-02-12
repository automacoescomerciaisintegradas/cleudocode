"""
Script para enviar mensagem de boas-vindas proativa para os bots do Telegram
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Bot
from core.config import settings

async def enviar_mensagem_boas_vindas():
    """Envia mensagem de boas-vindas proativa para os bots do Telegram"""
    
    mensagem = """Até Breve 💎✨🃏
Ajude a 🚀📰Newsletter a crescer convidando mais pessoas, mais pessoas mais motivação para trazer mais conteúdo.

link canal https://whatsapp.com/channel/0029Vb7MgPz5kg767iWItk42"""
    
    # Obter tokens dos bots
    tokens = []
    
    # Adicionando os tokens conhecidos
    token1 = settings.get("TELEGRAM_TOKEN")
    token2 = settings.get("TELEGRAM_BOT_TOKEN")
    
    if token1:
        tokens.append(("Bot 1", token1))
    if token2:
        tokens.append(("Bot 2", token2))
    
    # Adicionando tokens numerados
    for i in range(2, 10):
        token_var = f"TELEGRAM_TOKEN_{i}"
        alt_token_var = f"TELEGRAM_BOT_TOKEN_{i}"
        
        token = settings.get(token_var)
        if not token:
            token = settings.get(alt_token_var)
        
        if token:
            tokens.append((f"Bot {i}", token))
        else:
            break
    
    if not tokens:
        print("Nenhum token de bot do Telegram encontrado nas configurações.")
        return
    
    print(f"Encontrados {len(tokens)} bots do Telegram.")
    
    # IDs de chat para enviar a mensagem
    # ATENÇÃO: Você precisa substituir este ID pelo ID real do chat ou grupo
    # Para obter o ID real, você pode verificar os logs anteriores ou usar métodos especiais
    chat_ids = []  # Adicione os IDs reais dos chats aqui quando obtidos
    
    # Se quiser enviar para outros chats, adicione-os aqui
    # chat_ids.extend(["outro_id1", "outro_id2"])
    
    for bot_nome, token in tokens:
        print(f"\nEnviando mensagem via {bot_nome}...")
        
        try:
            # Criar instância do bot
            bot = Bot(token=token)
            
            for chat_id in chat_ids:
                try:
                    await bot.send_message(chat_id=chat_id, text=mensagem)
                    print(f"✓ Mensagem enviada com sucesso para {chat_id} via {bot_nome}")
                except Exception as e:
                    print(f"✗ Erro ao enviar para {chat_id} via {bot_nome}: {e}")
                    
        except Exception as e:
            print(f"✗ Erro ao inicializar {bot_nome}: {e}")

def main():
    import asyncio
    
    print("Enviando mensagem de boas-vindas proativa para os bots do Telegram...")
    print("ATENÇÃO: Esta funcionalidade requer que você tenha os IDs de chat válidos.")
    print("Os IDs de chat precisam ser de chats onde o bot já está presente ou")
    print("que já iniciaram uma conversa com o bot.")
    
    confirmacao = input("\nDeseja continuar? (s/n): ")
    if confirmacao.lower() != 's':
        print("Operação cancelada.")
        return
    
    try:
        asyncio.run(enviar_mensagem_boas_vindas())
    except Exception as e:
        print(f"Erro ao executar a função assíncrona: {e}")

if __name__ == "__main__":
    main()