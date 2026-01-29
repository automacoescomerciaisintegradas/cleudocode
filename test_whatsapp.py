"""
Script para testar o gateway do WhatsApp
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from gateways.whatsapp_adapter import WhatsAppGateway

def testar_whatsapp():
    """Testa o gateway do WhatsApp"""
    
    print("Testando o gateway do WhatsApp...")
    
    # Criar instância do gateway do WhatsApp
    whatsapp_gateway = WhatsAppGateway()
    
    # Verificar se as credenciais estão configuradas
    if not whatsapp_gateway.id_instance or not whatsapp_gateway.api_token_instance:
        print("Credenciais do WhatsApp não configuradas. Usando modo simulação.")
        print(f"ID_INSTANCE: {whatsapp_gateway.id_instance}")
        print(f"API_TOKEN_INSTANCE: {whatsapp_gateway.api_token_instance}")
        
        # Vamos testar o modo simulação
        print("\n--- Testando modo simulação ---")
        
        # Testar envio de mensagem simulada
        mensagem_teste = "Teste de mensagem do sistema Cleudocodebot!"
        numero_teste = "5511999999999"  # Número de teste
        
        print(f"Enviando mensagem simulada para: {numero_teste}")
        whatsapp_gateway.send_message(numero_teste, mensagem_teste)
        
        # Simular recebimento de mensagem
        print(f"\nSimulando recebimento de mensagem de: {numero_teste}")
        whatsapp_gateway.simulate_incoming(numero_teste, "Olá, estou testando o sistema!")
        
        return
    
    # Se as credenciais estiverem configuradas, iniciar o gateway
    print("Credenciais do WhatsApp encontradas. Iniciando gateway...")
    whatsapp_gateway.start()
    
    # Mensagem de boas-vindas que será usada
    mensagem_boas_vindas = """Nome do cliente: Teste
Telefone do cliente: 5511999999999

[**Atendimento HUMANO**]https://wa.me/5588921567214

📞 Contato e Suporte
[**Saiba Mais!!!!**]
https://wa.me/558894227586
[**Atendimento HUMANO**]https://wa.me/5588921567214
💡 **Não perca tempo. A revolução do atendimento começa agora!**
https://www.whatsapp.com/channel/558894227586

Comece agora

Os links serão enviados no Grupo VIP - CONEXÃO CLIENTE no Whatsapp, clique no link abaixo para entrar no grupo.

Siga o canal "Grupo VIP" no WhatsApp: https://whatsapp.com/channel/558894227586

CLIQUE AQUI PARA ENTRAR NO GRUPO
Siga o canal "Grupo VIP" no WhatsApp: https://whatsapp.com/channel/558894227586"""
    
    # Testar envio de mensagem
    numero_teste = input("Digite o número de telefone para testar (formato internacional, ex: 5511999999999): ")
    
    if numero_teste:
        print(f"Enviando mensagem de boas-vindas para: {numero_teste}")
        try:
            whatsapp_gateway.send_message(numero_teste, mensagem_boas_vindas)
            print("Mensagem enviada com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
    
    print("\nGateway do WhatsApp testado com sucesso!")

if __name__ == "__main__":
    testar_whatsapp()