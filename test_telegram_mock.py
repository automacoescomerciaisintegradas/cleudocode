"""
test_telegram_mock.py — Teste simulado do bot do Telegram sem API real.

Simula:
  - Recebimento de mensagem do Telegram
  - Chamada ao orchestrator
  - Geração de resposta

Útil para validar lógica antes de ter um token real.

Autor: Cleudo Code Team
Data: 06/02/2026 (Atualizado pelo Orquestrador Pro Max)
"""

from orchestrator import orchestrator

def simulate_telegram_message(text: str, user_id: str = "123456789", chat_id: str = "987654321"):
    """Simula uma mensagem recebida pelo bot do Telegram."""
    msg = {
        "from": chat_id,
        "text": text,
        "timestamp": "2026-02-06T15:00:00Z"
    }
    print(f"[SIM] Mensagem recebida de {user_id} (chat {chat_id}): '{text}'")
    
    result = orchestrator.receive_message(msg)
    
    # Formata resposta como o bot faria
    steps = result.get("result", {}).get("steps", [])
    overall = result.get("result", {}).get("overall_status", "unknown")
    
    print("\n[RESPONSE] Resposta ao usuário:")
    if overall == "success":
        print("✅ Tarefa concluída!")
        for i, s in enumerate(steps, 1):
            print(f"  {i}. {s.get('action')}: {s.get('output', '')[:80]}...")
    else:
        print("⚠️ Falha na tarefa.")
        for i, s in enumerate(steps, 1):
            print(f"  {i}. [{s.get('status')}] {s.get('error', s.get('stderr', ''))[:80]}...")
    
    return result

if __name__ == "__main__":
    print("="*60)
    print("🤖 Teste Mock do Bot do Telegram")
    print("="*60)
    
    # Teste 1: Deploy
    simulate_telegram_message("Deploy v2.1 e avise no WhatsApp")
    
    print("\n" + "-"*60)
    
    # Teste 2: Campanha
    simulate_telegram_message("Envie campanha com 'Teste OpenClaw!' para +5511999999999")
    
    print("\n✅ Teste concluído. Seu orchestrator está pronto para o bot real.")
