"""
Script para testar o envio da mensagem de boas-vindas do WhatsApp
Adaptado para o ecossistema Cleudocode pelo Orquestrador Pro Max
"""
import sys
import os
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Adiciona diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from core.config import settings
from gateways.whatsapp_adapter import EvolutionGateway
from core.daemon import CleudoDaemon

def testar_mensagem_boas_vindas():
    """Testa o envio da mensagem de boas-vindas para um número"""
    
    print("\n[🚀] Testando envio da mensagem de boas-vindas do WhatsApp...")
    
    # Criar instância do gateway do WhatsApp
    whatsapp_gateway = EvolutionGateway()
    
    # Verificar se as credenciais estão configuradas
    if not whatsapp_gateway.token or not whatsapp_gateway.base_url:
        print("❌ Erro: Credenciais do WhatsApp não configuradas no .env")
        return
    
    print(f"✅ Instância: {whatsapp_gateway.instance_name}")
    print(f"🌐 Base URL: {whatsapp_gateway.base_url}")
    
    # Mensagem de boas-vindas (Conforme solicitado)
    mensagem_boas_vindas = """[**Atendimento HUMANO**]https://wa.me/5588921567214

📞 Contato e Suporte
[**Saiba Mais!!!!**]
https://wa.me/558894227586
[**Atendimento HUMANO**]https://wa.me/5588921567214
💡 **Não perca tempo. A revolução do atendimento começa agora!**
https://www.whatsapp.com/channel/558894227586"""
    
    # Solicitar número para teste
    numero_teste = input("\n👉 Digite o número do WhatsApp para testar (ex: 5588999999999): ").strip()
    
    if not numero_teste:
        print("⚠️ Nenhum número fornecido, encerrando teste.")
        return
    
    print(f"\n[📡] Enviando para: {numero_teste}...")
    
    try:
        # Enviar mensagem
        success = whatsapp_gateway.send_message(numero_teste, mensagem_boas_vindas)
        
        if success:
            print(f"\n✅ Mensagem enviada com sucesso!")
        else:
            print(f"\n❌ Falha ao enviar mensagem. Verifique se a instância está conectada.")
            
    except Exception as e:
        print(f"\n❌ Erro crítico no envio: {e}")

def testar_resposta_automatica():
    """Testa a lógica do Daemon ao receber uma mensagem simulada"""
    
    print(f"\n{'='*60}")
    print("      🧪 TESTANDO LOGICA DE RESPOSTA (DAEMON)")
    print("="*60)
    
    # Criar Daemon e Gateway
    daemon = CleudoDaemon()
    whatsapp_gateway = EvolutionGateway()
    
    # Adicionar gateway ao daemon (isso configura o callback)
    daemon.add_gateway(whatsapp_gateway)
    
    # Simular recebimento de mensagem
    numero_teste = input("\n👉 Digite um número para simular recebimento: ").strip()
    mensagem_teste = input("👉 Digite uma mensagem para simular recebimento: ").strip()
    
    if not numero_teste or not mensagem_teste:
        print("⚠️ Dados insuficientes para simular.")
        return
    
    print(f"\n[📥] Simulando mensagem de {numero_teste}: '{mensagem_teste}'")
    
    try:
        # Simular recebimento (Vai disparar o daemon.handle_message)
        whatsapp_gateway.simulate_incoming(numero_teste, mensagem_teste)
        print("\n✅ Simulação processada pelo Daemon.")
        print("ℹ️ Aguardando resposta da IA (10s)...")
        import time
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")

if __name__ == "__main__":
    print("============================================================")
    print("        CLEUDOCODE - WHATSAPP WELCOME & LOGIC TESTER 💎")
    print("============================================================")
    
    testar_mensagem_boas_vindas()
    testar_resposta_automatica()
    
    print(f"\n{'='*60}")
    print("🏁 TESTE CONCLUÍDO")
    print("="*60)
