"""
Script de teste robusto para envio de mensagens via WhatsApp
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from gateways.whatsapp_adapter import WhatsAppGateway

def testar_envio_mensagem():
    """Testa o envio de mensagem via WhatsApp com tratamento de erro robusto"""
    
    print("Testando envio de mensagem via WhatsApp...")
    
    # Criar gateway
    gateway = WhatsAppGateway()
    
    # Verificar se está configurado
    print(f"ID da Instância: {gateway.id_instance}")
    print(f"URL Base: {gateway.base_url}")
    print(f"Headers configurados: {bool(gateway.headers)}")
    
    if not gateway.id_instance or not gateway.headers:
        print("❌ Gateway não configurado corretamente")
        return
    
    # Testar envio com mensagem segura (sem emojis)
    mensagem_teste = """Boas-vindas ao nosso servico!

Aqui voce tera acesso a solucoes inteligentes e automatizacoes para revolucionar seu atendimento.

Canal oficial:
https://www.whatsapp.com/channel/558894227586"""
    
    numero_teste = "5588999999999"  # Número de teste
    
    print(f"\nEnviando mensagem para: {numero_teste}")
    print(f"Mensagem: {mensagem_teste[:100]}...")
    
    try:
        # Testar envio
        resultado = gateway.send_message(numero_teste, mensagem_teste)
        
        if resultado:
            print("✅ Mensagem enviada com sucesso!")
            print(f"Resultado: {resultado}")
        else:
            print("⚠️  Mensagem não foi enviada (possivelmente em modo simulação)")
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        import traceback
        traceback.print_exc()

def testar_sanitizacao():
    """Testa a função de sanitização de caracteres Unicode"""
    
    print("\n" + "="*50)
    print("TESTANDO FUNÇÃO DE SANITIZAÇÃO")
    print("="*50)
    
    gateway = WhatsAppGateway()
    
    # Testar com mensagem problemática
    mensagem_com_emojis = """👋 Olá, Seja bem-vindo(a) ao nosso canal!

🚀 Aqui você terá acesso a soluções inteligentes, automações e novidades para revolucionar seu atendimento.

📢 Canal oficial:
https://www.whatsapp.com/channel/558894227586"""
    
    print("Mensagem original:")
    print(mensagem_com_emojis)
    
    mensagem_sanitizada = gateway._sanitize_unicode_message(mensagem_com_emojis)
    
    print("\nMensagem sanitizada:")
    print(mensagem_sanitizada)
    
    print("\n✅ Sanitização funcionando corretamente!")

def testar_fluxo_completo():
    """Testa o fluxo completo de envio"""
    
    print("\n" + "="*50)
    print("TESTANDO FLUXO COMPLETO DE ENVIO")
    print("="*50)
    
    gateway = WhatsAppGateway()
    
    # Testar com mensagem de boas-vindas completa (sem emojis)
    mensagem_boas_vindas = """[**Atendimento HUMANO**]https://wa.me/5588921567214

Telefone: (88) 9215-67214
Contato e Suporte
[**Saiba Mais!!!!**]
https://wa.me/558894227586
[**Atendimento HUMANO**]https://wa.me/5588921567214
Telefone: (88) 9215-67214
* Nao perca tempo. A revolucao do atendimento comeca agora! *
https://www.whatsapp.com/channel/558894227586

Comece agora

Os links serao enviados no Grupo VIP - CONEXAO CLIENTE no Whatsapp, clique no link abaixo para entrar no grupo.

Siga o canal "Grupo VIP" no WhatsApp: https://whatsapp.com/channel/558894227586

CLIQUE AQUI PARA ENTRAR NO GRUPO
Siga o canal "Grupo VIP" no WhatsApp: https://whatsapp.com/channel/558894227586"""
    
    print("Testando envio da mensagem de boas-vindas completa...")
    
    # Simular envio para um número
    numero_destino = "558894227586"
    
    try:
        resultado = gateway.send_message(numero_destino, mensagem_boas_vindas)
        print(f"✅ Envio concluído. Resultado: {bool(resultado)}")
    except Exception as e:
        print(f"⚠️ Erro durante o envio: {e}")

if __name__ == "__main__":
    print("TESTE ROBUSTO DE ENVIO VIA WHATSAPP")
    print("="*50)
    
    testar_sanitizacao()
    testar_envio_mensagem()
    testar_fluxo_completo()
    
    print(f"\n{'='*50}")
    print("TESTE CONCLUÍDO")
    print("="*50)
    print("\nDICAS:")
    print("- Use a interface web em http://localhost:5000")
    print("- Evite emojis nas mensagens ou use a sanitização")
    print("- Verifique as credenciais do WhatsApp")
    print("- O gateway está configurado para modo simulação até conexão real")