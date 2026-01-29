"""
Script para testar o envio da mensagem de boas-vindas do WhatsApp
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from gateways.whatsapp_adapter import WhatsAppGateway

def testar_mensagem_boas_vindas():
    """Testa o envio da mensagem de boas-vindas para um número"""
    
    print("Testando envio da mensagem de boas-vindas do WhatsApp...")
    
    # Criar instância do gateway do WhatsApp
    whatsapp_gateway = WhatsAppGateway()
    
    # Verificar se as credenciais estão configuradas
    if not whatsapp_gateway.id_instance or not whatsapp_gateway.authentication_key:
        print("Credenciais do WhatsApp não configuradas.")
        return
    
    print(f"ID da Instância: {whatsapp_gateway.id_instance}")
    print(f"Base URL: {whatsapp_gateway.base_url}")
    
    # Mensagem de boas-vindas
    mensagem_boas_vindas = """[**Atendimento HUMANO**]https://wa.me/5588921567214

📞 Contato e Suporte
[**Saiba Mais!!!!**]
https://wa.me/558894227586
[**Atendimento HUMANO**]https://wa.me/5588921567214
💡 **Não perca tempo. A revolução do atendimento começa agora!**
https://www.whatsapp.com/channel/558894227586"""
    
    # Solicitar número para teste
    numero_teste = input("Digite o número do WhatsApp para testar (formato internacional, ex: 5511999999999): ").strip()
    
    if not numero_teste:
        print("Nenhum número fornecido, encerrando teste.")
        return
    
    print(f"\nEnviando mensagem de boas-vindas para: {numero_teste}")
    print(f"Mensagem: {mensagem_boas_vindas}")
    
    try:
        # Enviar mensagem
        resultado = whatsapp_gateway.send_message(numero_teste, mensagem_boas_vindas)
        
        if resultado:
            print(f"\n✅ Mensagem enviada com sucesso!")
            print(f"Resultado: {resultado}")
        else:
            print(f"\n❌ Falha ao enviar mensagem")
            print("A mensagem pode ter sido enviada no modo simulação")
            
    except Exception as e:
        print(f"\n❌ Erro ao enviar mensagem: {e}")
        print("Verifique se o número está correto e se o WhatsApp está conectado")

def testar_resposta_automatica():
    """Testa a resposta automática quando uma mensagem é recebida"""
    
    print(f"\n{'='*60}")
    print("TESTANDO RESPOSTA AUTOMÁTICA")
    print("="*60)
    
    # Criar instância do gateway
    whatsapp_gateway = WhatsAppGateway()
    
    # Simular recebimento de mensagem
    numero_teste = input("Digite um número para simular recebimento de mensagem: ").strip()
    mensagem_teste = input("Digite uma mensagem para simular recebimento: ").strip()
    
    if not numero_teste or not mensagem_teste:
        print("Dados insuficientes para simular recebimento.")
        return
    
    print(f"\nSimulando recebimento de mensagem de {numero_teste}: {mensagem_teste}")
    
    try:
        # Simular recebimento de mensagem (isso deve disparar a resposta automática)
        whatsapp_gateway.simulate_incoming(numero_teste, mensagem_teste)
        print("✅ Simulação de recebimento realizada")
        print("A resposta automática deve ter sido disparada")
        
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")

if __name__ == "__main__":
    print("Teste de Mensagem de Boas-Vindas do WhatsApp")
    print("="*50)
    
    testar_mensagem_boas_vindas()
    testar_resposta_automatica()
    
    print(f"\n{'='*50}")
    print("TESTE CONCLUÍDO")
    print("="*50)
    print("\nLembre-se: Para que a mensagem de boas-vindas seja disparada automaticamente,")
    print("ela precisa estar configurada para responder a novas mensagens recebidas.")