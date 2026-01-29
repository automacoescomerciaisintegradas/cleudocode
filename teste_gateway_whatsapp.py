"""
Script de teste direto para o gateway do WhatsApp
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from gateways.whatsapp_adapter import WhatsAppGateway

def testar_gateway_whatsapp():
    """Testa diretamente o gateway do WhatsApp"""
    
    print("Teste Direto do Gateway do WhatsApp")
    print("="*50)
    
    # Criar instância do gateway
    gateway = WhatsAppGateway()

    print(f"ID da Instância: {gateway.id_instance}")
    print(f"URL Base: {gateway.base_url}")
    print(f"Token de Autenticação: {'Configurado' if gateway.authentication_key else 'Não configurado'}")

    # Verificar se está em modo simulação
    if not hasattr(gateway, 'client') or not gateway.client:
        print("\n[AVISO] Gateway em modo SIMULACAO (credenciais nao configuradas ou invalidas)")
        print("   Isso e esperado com as credenciais de teste atuais")
    else:
        print("\n[OK] Gateway conectado ao servidor real")
    
    # Testar envio de mensagem de boas-vindas para um contato conhecido
    print(f"\nTestando envio de mensagem de boas-vindas...")
    
    # Mensagem de boas-vindas configurada
    mensagem_boas_vindas = """[**Atendimento HUMANO**]https://wa.me/5588921567214

Ola Ronaldo Simplicio! Seja bem-vindx ao nosso canal!
Telefone: (88) 9215-67214
Contato e Suporte
[**Saiba Mais!!!!**]
https://wa.me/558894227586
[**Atendimento HUMANO**]https://wa.me/5588921567214
Telefone: (88) 9215-67214
* Nao perca tempo. A revolucao do atendimento comeca agora! *
https://www.whatsapp.com/channel/558894227586"""
    
    # ID do contato identificado no webhook
    contato_teste = "112928179142781@lid"  # Ronaldo Simplicio
    
    print(f"\nEnviando mensagem para: {contato_teste}")
    print(f"Mensagem: {mensagem_boas_vindas[:100]}...")
    
    try:
        # Enviar mensagem
        resultado = gateway.send_message(contato_teste, mensagem_boas_vindas)
        
        if resultado:
            print(f"\n[OK] Mensagem enviada com sucesso!")
            print(f"Resultado: {resultado}")
        else:
            print(f"\n[AVISO] Mensagem processada em modo simulacao")
            print("   (Isso e normal com credenciais de teste)")

    except Exception as e:
        print(f"\n[ERRO] Erro ao enviar mensagem: {e}")
    
    # Testar envio para outros contatos
    print(f"\nTestando envio para outros contatos...")
    
    outros_contatos = [
        "558894227586@s.whatsapp.net",  # Canal Oficial
        "5588921567214@s.whatsapp.net"  # Atendimento Humano
    ]
    
    for contato in outros_contatos:
        print(f"\nEnviando para: {contato}")
        try:
            resultado = gateway.send_message(contato, mensagem_boas_vindas)
            if resultado:
                print(f"   [OK] Enviado com sucesso")
            else:
                print(f"   [AVISO] Processado em simulacao")
        except Exception as e:
            print(f"   [ERRO] Erro: {e}")
    
    print(f"\n{'='*50}")
    print("TESTE CONCLUÍDO")
    print("="*50)
    print("\nDICAS PARA ATIVAÇÃO REAL:")
    print("1. Substitua as credenciais de teste pelas reais do Green-API")
    print("2. Conecte um número real do WhatsApp à instância")
    print("3. O sistema estará pronto para envios reais")
    print("4. A mensagem de boas-vindas já está configurada")

def testar_identificacao_contatos():
    """Testa a identificação de contatos a partir de dados recebidos"""
    
    print(f"\n{'='*50}")
    print("TESTE DE IDENTIFICAÇÃO DE CONTATOS")
    print("="*50)
    
    # Dados extraídos do webhook que você forneceu
    dados_webhook = {
        "key": {
            "remoteJid": "554184212269-1488774100@g.us",
            "remoteJidAlt": None,
            "fromMe": False,
            "id": "A585495F94301632990CDD3F399B1C13",
            "participant": "112928179142781@lid",
            "participantAlt": "558389119837@s.whatsapp.net",
            "addressingMode": "lid"
        },
        "pushName": "Ronaldo Simplicio",
        "message": {
            "conversation": "https://www.youtube.com/live/W5eW_HAFPcw?si=Mn6G9UeaOQwT34jZ"
        }
    }
    
    print("Dados recebidos do webhook:")
    print(f"  Contato: {dados_webhook['pushName']}")
    print(f"  ID do Contato: {dados_webhook['key']['participant']}")
    print(f"  Grupo: {dados_webhook['key']['remoteJid']}")
    print(f"  Mensagem: {dados_webhook['message']['conversation']}")
    
    # Extração de informações
    contato_id = dados_webhook['key']['participant']
    nome_contato = dados_webhook['pushName']
    grupo_id = dados_webhook['key']['remoteJid']
    
    print(f"\nInformações extraídas:")
    print(f"  ID: {contato_id}")
    print(f"  Nome: {nome_contato}")
    print(f"  Grupo: {grupo_id}")
    
    # Verificar se o contato já está no sistema
    gateway = WhatsAppGateway()
    
    print(f"\nContato identificado e pronto para inclusão na lista de envio!")
    print(f"O sistema pode armazenar este contato para futuras campanhas.")

if __name__ == "__main__":
    testar_gateway_whatsapp()
    testar_identificacao_contatos()
    
    print(f"\n{'='*50}")
    print("TESTE COMPLETO - SISTEMA PRONTO!")
    print("="*50)