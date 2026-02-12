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
    mensagem = """🎉 Bem-vindo(a) ao nosso canal! 💎✨🃏

🚀 Fique por dentro das últimas novidades
📧 Newsletter exclusiva para membros

🤝 Ajude a comunidade a crescer:
Convide amigos para fazer parte desta jornada!

🔔 Canal oficial: https://whatsapp.com/channel/0029Vb7MgPz5kg767iWItk42

✨ Obrigado por fazer essa comunidade evoluir!"""
    
    # IDs de chat para enviar a mensagem (substitua pelos IDs reais dos seus chats/grupos)
    # Para obter o ID real, siga as instruções no README
    chat_ids = [
        # "SEU_CHAT_ID_AQUI",  # Substitua este exemplo pelo ID real do seu chat
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
    
    mensagem = """🎉 Bem-vindo(a) ao nosso canal! 💎✨🃏

🚀 Fique por dentro das últimas novidades
📧 Newsletter exclusiva para membros

🤝 Ajude a comunidade a crescer:
Convide amigos para fazer parte desta jornada!

🔔 Canal oficial: https://whatsapp.com/channel/0029Vb7MgPz5kg767iWItk42

✨ Obrigado por fazer essa comunidade evoluir!"""
    
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
    print("🚀 Enviando mensagem de boas-vindas para o Telegram...")
    enviar_mensagem_boas_vindas()