"""
Script para testar o envio direto da mensagem de boas-vindas do WhatsApp
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from gateways.whatsapp_adapter import WhatsAppGateway

def enviar_mensagem_boas_vindas_direto():
    """Envia a mensagem de boas-vindas diretamente para um número"""
    
    print("Enviando mensagem de boas-vindas do WhatsApp...")
    
    # Criar instância do gateway do WhatsApp
    whatsapp_gateway = WhatsAppGateway()
    
    # Verificar se as credenciais estão configuradas
    if not whatsapp_gateway.id_instance or not whatsapp_gateway.authentication_key:
        print("Credenciais do WhatsApp não configuradas.")
        return
    
    print(f"ID da Instância: {whatsapp_gateway.id_instance}")
    print(f"Base URL: {whatsapp_gateway.base_url}")
    
    # Número de teste (substitua pelo número real que deseja testar)
    # Por segurança, estou usando um número de exemplo
    numero_destino = "558894227586"  # Este é um dos números que aparecem na sua mensagem
    
    # Mensagem de boas-vindas exata que você solicitou
    mensagem_boas_vindas = """[**Atendimento HUMANO**]https://wa.me/5588921567214

Telefone: (88) 9215-67214
Contato e Suporte
[**Saiba Mais!!!!**]
https://wa.me/558894227586
[**Atendimento HUMANO**]https://wa.me/5588921567214
Telefone: (88) 9215-67214
* Nao perca tempo. A revolucao do atendimento comeca agora! *
https://www.whatsapp.com/channel/558894227586"""
    
    print(f"\nEnviando mensagem de boas-vindas para: {numero_destino}")
    print(f"Mensagem: {mensagem_boas_vindas}")
    
    try:
        # Enviar mensagem
        resultado = whatsapp_gateway.send_message(numero_destino, mensagem_boas_vindas)
        
        if resultado:
            print(f"\n[OK] Mensagem enviada com sucesso!")
            print(f"Resultado: {resultado}")
        else:
            print(f"\n[ERRO] Falha ao enviar mensagem")
            print("A mensagem pode ter sido enviada no modo simulação")

    except Exception as e:
        print(f"\n[ERRO] Erro ao enviar mensagem: {e}")
        print("Verifique se o número está correto e se o WhatsApp está conectado")

def enviar_para_multiplos_numeros():
    """Envia a mensagem para múltiplos números"""
    
    print(f"\n{'='*60}")
    print("ENVIANDO PARA MÚLTIPLOS NÚMEROS")
    print("="*60)
    
    # Criar instância do gateway do WhatsApp
    whatsapp_gateway = WhatsAppGateway()
    
    # Números de destino
    numeros_destino = [
        "558894227586",  # Canal mencionado
        "5588921567214"  # Link de atendimento humano
    ]
    
    # Mensagem de boas-vindas
    mensagem_boas_vindas = """[**Atendimento HUMANO**]https://wa.me/5588921567214

📞 Contato e Suporte
[**Saiba Mais!!!!**]
https://wa.me/558894227586
[**Atendimento HUMANO**]https://wa.me/5588921567214
💡 **Não perca tempo. A revolução do atendimento começa agora!**
https://www.whatsapp.com/channel/558894227586"""
    
    for numero in numeros_destino:
        print(f"\nEnviando para: {numero}")
        try:
            resultado = whatsapp_gateway.send_message(numero, mensagem_boas_vindas)
            if resultado:
                print(f"✅ Enviado com sucesso para {numero}")
            else:
                print(f"❌ Falha ao enviar para {numero}")
        except Exception as e:
            print(f"❌ Erro ao enviar para {numero}: {e}")

if __name__ == "__main__":
    print("Teste de Envio Direto da Mensagem de Boas-Vindas do WhatsApp")
    print("="*60)
    
    enviar_mensagem_boas_vindas_direto()
    enviar_para_multiplos_numeros()
    
    print(f"\n{'='*60}")
    print("TESTE CONCLUÍDO")
    print("="*60)
    print("\nA mensagem de boas-vindas está configurada e pronta para ser usada!")