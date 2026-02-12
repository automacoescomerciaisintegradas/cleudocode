#!/usr/bin/env python3
"""
Script de Demonstração do Agente de Vendas Shopee
Este script demonstra a funcionalidade do agente respondendo a algumas mensagens de exemplo
"""
from shopee_telegram_agent import ShopeeSalesAgent

def testar_agente():
    """Testa o agente com algumas mensagens de exemplo"""
    agent = ShopeeSalesAgent()
    
    print("🤖 Demonstração do Agente de Vendas Shopee")
    print("="*50)
    
    # Mensagens de teste
    mensagens_teste = [
        "Oi",
        "Olá, gostaria de saber sobre frete",
        "Tem produto X em estoque?",
        "Como faço para pagar?",
        "Obrigado pelas informações",
        "O que é flywheel?",
        "Me fale sobre estudos de caso",
        "Como funciona a roda de crescimento?",
        "O que é o DANNET MASTER?",
        "Como gerar link de afiliado?",
        "Como criar mensagem com IA?",
        "Quero gerar um link de afiliado",
        "Preciso de uma mensagem promocional"
    ]
    
    for i, mensagem in enumerate(mensagens_teste, 1):
        print(f"\n{i}. Mensagem recebida: {mensagem}")
        resposta = agent.responder_mensagem(mensagem, "123456789")  # ID de chat fictício
        print(f"   Resposta do agente: {resposta[:100]}..." if len(resposta) > 100 else f"   Resposta do agente: {resposta}")
        print("-" * 50)

if __name__ == "__main__":
    testar_agente()