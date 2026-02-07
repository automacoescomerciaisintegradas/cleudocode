import sys
import os
from datetime import datetime
from core.config import settings
from gateways.whatsapp_adapter import EvolutionGateway

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 disparo_massa_whatsapp.py "<saudacao>" "<assinatura>"")
        sys.exit(1)

    saudacao_personalizada = sys.argv[1]
    assinatura_personalizada = sys.argv[2]

    whatsapp_gateway = EvolutionGateway()

    if not whatsapp_gateway.token or not whatsapp_gateway.base_url:
        print("Credenciais do WhatsApp (token ou base_url) não configuradas. Verifique core/config.py ou as variáveis de ambiente.")
        sys.exit(1)

    print(f"Base URL: {whatsapp_gateway.base_url}")

    mensagem_base = """💡 **Não perca tempo. A revolução do atendimento começa agora!**
{saudacao}
{assinatura}
📞 Contato e Suporte
[**Saiba Mais!!!!**]
https://wa.me/558894227586
"""
    
    mensagem_final = mensagem_base.format(saudacao=saudacao_personalizada, assinatura=assinatura_personalizada)

    print("\n--- PRÉVIA DA MENSAGEM ---")
    print(mensagem_final)
    print("--------------------------")

    numero_teste = input("Digite o número do WhatsApp para enviar (formato internacional, ex: 5511999999999): ").strip()

    if not numero_teste:
        print("Nenhum número fornecido, encerrando envio.")
        sys.exit(0)

    print(f"\nEnviando mensagem para: {numero_teste}")
    try:
        resultado = whatsapp_gateway.send_message(numero_teste, mensagem_final)
        if resultado:
            print(f"\n✅ Mensagem enviada com sucesso!")
            print(f"Resultado: {resultado}")
        else:
            print(f"\n❌ Falha ao enviar mensagem ou enviada em modo de simulação.")
    except Exception as e:
        print(f"\n❌ Erro ao enviar mensagem: {e}")
        print("Verifique se o número está correto e se o WhatsApp está conectado/autenticado.")

if __name__ == "__main__":
    main()