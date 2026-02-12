"""
Script para enviar mensagens proativas para os bots do Telegram
Finalizado pelo Orquestrador Pro Max
"""
import os
import logging
from dotenv import load_dotenv
from core.config import settings
from gateways.telegram_adapter import TelegramGateway

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ProactiveSender")

def enviar_mensagem_boas_vindas():
    """Envia mensagem de boas-vindas para os bots do Telegram"""
    
    # Garantir que o .env está carregado
    load_dotenv()
    
    # Criar uma instância do gateway do Telegram
    telegram_gateway = TelegramGateway()
    
    # Iniciar manualmente os bots para ter acesso às instâncias
    print("\n[🌌] Iniciando bots do Telegram...")
    telegram_gateway.start()
    
    # Mensagem de boas-vindas (Conforme solicitado pelo usuário)
    mensagem = """Até Breve 💎✨🃏
Ajude a 🚀📰Newsletter a crescer convidando mais pessoas, mais pessoas mais motivação para trazer mais conteúdo.

link canal https://whatsapp.com/channel/0029Vb7MgPz5kg767iWItk42"""
    
    # IDs de chat para enviar a mensagem
    chat_ids = [
        # "SEU_CHAT_ID_AQUI",  # Substitua pelo ID real do seu chat
    ]
    
    print(f"[📡] Preparando envio proativo para {len(chat_ids)} chats...")
    
    # Pequena espera para garantir que a conexão foi estabelecida
    import time
    time.sleep(3)
    
    # Enviar mensagem para cada bot configurado
    if not telegram_gateway.bots:
        print("❌ Nenhum bot ativo encontrado. Verifique seu TELEGRAM_BOT_TOKEN no .env")
        return

    for bot_config in telegram_gateway.bots:
        print(f"   - Usando bot: {bot_config['name']}")
        
        # Enviar para os chats especificados
        for chat_id in chat_ids:
            try:
                # Usar o método send_message do gateway
                telegram_gateway.send_message(chat_id, mensagem, bot_name=bot_config['name'])
                print(f"   ✅ Mensagem enviada com sucesso para {chat_id}")
            except Exception as e:
                print(f"   ❌ Erro ao enviar para {chat_id}: {e}")
    
    print("\n[🏁] Operação concluída. Aguardando finalização do gateway...")
    time.sleep(2)
    telegram_gateway.stop()

def enviar_mensagem_para_canal():
    """Função para enviar mensagem para um canal do Telegram"""
    load_dotenv()
    telegram_gateway = TelegramGateway()
    telegram_gateway.start()
    
    mensagem = """Até Breve 💎✨🃏
Ajude a 🚀📰Newsletter a crescer convidando mais pessoas, mais pessoas mais motivação para trazer mais conteúdo.

link canal https://whatsapp.com/channel/0029Vb7MgPz5kg767iWItk42"""
    
    # ID do canal (IDs de canais são negativos e começam com -100)
    canal_id = "-1002345678901" # Substituir pelo ID real
    
    print(f"[📢] Enviando para o canal {canal_id}...")
    
    import time
    time.sleep(3)

    for bot_config in telegram_gateway.bots:
        try:
            telegram_gateway.send_message(canal_id, mensagem, bot_name=bot_config['name'])
            print(f"   ✅ Enviado para canal via {bot_config['name']}")
        except Exception as e:
            print(f"   ❌ Erro no canal: {e}")
    
    time.sleep(2)
    telegram_gateway.stop()

if __name__ == "__main__":
    print("============================================================")
    print("          CLEUDOCODE - PROACTIVE TELEGRAM SENDER 🚀")
    print("============================================================")
    print("1. Enviar mensagem de boas-vindas para chats (adicione o ID real do chat)")
    print("2. Enviar mensagem para canal (ID manual)")
    print("Q. Sair")
    
    escolha = input("\nEscolha uma opção: ").strip().lower()
    
    if escolha == "1":
        enviar_mensagem_boas_vindas()
    elif escolha == "2":
        enviar_mensagem_para_canal()
    elif escolha == "q":
        print("Saindo...")
    else:
        print("Opção inválida.")
