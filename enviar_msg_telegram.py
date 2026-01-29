"""
Script para enviar mensagens proativas para os bots do Telegram
"""
import asyncio
from core.config import settings
from gateways.telegram_adapter import TelegramGateway

def enviar_mensagem_boas_vindas():
    """Envia mensagem de boas-vindas para os bots do Telegram"""
    
    # Criar uma instância do gateway do Telegram
    telegram_gateway = TelegramGateway()
    
    # Iniciar manualmente os bots para ter acesso às instâncias
    print("Iniciando bots do Telegram...")
    telegram_gateway.start()
    
    # Mensagem de boas-vindas
    mensagem = """Até Breve 💎✨🃏
Ajude a 🚀📰Newsletter a crescer convidando mais pessoas, mais pessoas mais motivação para trazer mais conteúdo.

link canal https://whatsapp.com/channel/0029Vb7MgPz5kg767iWItk42"""
    
    # IDs de chat para enviar a mensagem (você precisará substituir pelos IDs reais dos chats)
    # Estes são exemplos - você precisará obter os IDs reais dos chats
    chat_ids = [
        "5667792894",  # ID do chat que apareceu nos logs anteriores
        # Adicione outros IDs de chat conforme necessário
    ]
    
    print(f"Tentando enviar mensagem de boas-vindas...")
    
    # Enviar mensagem para cada bot
    for bot_config in telegram_gateway.bots:
        print(f"Enviando mensagem via {bot_config['name']}...")
        
        # Enviar para os chats especificados
        for chat_id in chat_ids:
            try:
                # Usar o método send_message do gateway
                telegram_gateway.send_message(chat_id, mensagem, bot_name=bot_config['name'])
                print(f"Mensagem enviada com sucesso para {chat_id} via {bot_config['name']}")
            except Exception as e:
                print(f"Erro ao enviar mensagem para {chat_id} via {bot_config['name']}: {e}")
    
    print("Operação concluída.")

def enviar_mensagem_para_canal():
    """Função para enviar mensagem para um canal do Telegram"""
    telegram_gateway = TelegramGateway()
    telegram_gateway.start()
    
    mensagem = """Até Breve 💎✨🃏
Ajude a 🚀📰Newsletter a crescer convidando mais pessoas, mais pessoas mais motivação para trazer mais conteúdo.

link canal https://whatsapp.com/channel/0029Vb7MgPz5kg767iWItk42"""
    
    # ID do canal (precisa ser um ID de canal válido)
    # Exemplo: -1001234567890 (canais têm IDs negativos)
    canal_id = "-1001234567890"  # Substitua pelo ID real do canal
    
    for bot_config in telegram_gateway.bots:
        try:
            telegram_gateway.send_message(canal_id, mensagem, bot_name=bot_config['name'])
            print(f"Mensagem enviada para o canal {canal_id} via {bot_config['name']}")
        except Exception as e:
            print(f"Erro ao enviar para o canal: {e}")

if __name__ == "__main__":
    print("Opções disponíveis:")
    print("1. Enviar mensagem de boas-vindas para chats")
    print("2. Enviar mensagem para canal")
    
    escolha = input("Escolha uma opção (1 ou 2): ")
    
    if escolha == "1":
        enviar_mensagem_boas_vindas()
    elif escolha == "2":
        enviar_mensagem_para_canal()
    else:
        print("Opção inválida")