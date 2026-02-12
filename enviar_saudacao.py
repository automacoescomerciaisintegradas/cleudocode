#!/usr/bin/env python3
"""
📢 Script de Saudação do Cleudocode
Envia mensagem de ativação para todos os canais configurados (Telegram e WhatsApp)
"""
import os
import sys
import asyncio
import requests
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 MENSAGEM DE SAUDAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

MENSAGEM_SAUDACAO = """
🚀 *Cleudocode está ATIVO!* 🚀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ *Status:* Sistema Operacional
🕐 *Ativado em:* {timestamp}
🤖 *Modo:* Inteligência Artificial

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 *Bem-vindo ao Cleudocode!*

Este wizard irá configurar seu ambiente 
seguindo os padrões Cleudocode!

💡 Estou pronto para ajudar você com:
• Automações comerciais
• Integração com sistemas
• Respostas inteligentes via IA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 contato@automacoescomerciais.com.br
© Automações Comerciais Integradas 2026 ⚙️
"""

# ═══════════════════════════════════════════════════════════════════════════════
# 📱 TELEGRAM
# ═══════════════════════════════════════════════════════════════════════════════

async def enviar_telegram(chat_id_override=None):
    """Envia mensagem para os bots do Telegram configurados"""
    from telegram import Bot
    
    # Chat IDs conhecidos (do histórico de mensagens)
    CHAT_IDS_CONHECIDOS = []  # IDs reais serão adicionados após descoberta
    
    # Coleta todos os tokens disponíveis
    tokens = []
    token_vars = [
        ("TELEGRAM_TOKEN", "Bot 1"),
        ("TELEGRAM_BOT_TOKEN", "Bot 2"),
        ("TELEGRAM_TOKEN_2", "Bot 3"),
        ("TELEGRAM_BOT_TOKEN_2", "Bot 4"),
    ]
    
    for var, nome in token_vars:
        token = os.getenv(var)
        if token:
            tokens.append((nome, token))
    
    if not tokens:
        print("⚠️  Nenhum token Telegram encontrado")
        return []
    
    resultados = []
    
    for nome, token in tokens:
        try:
            bot = Bot(token=token)
            
            # Obtém informações do bot
            me = await bot.get_me()
            print(f"🤖 {nome}: @{me.username}")
            
            # Usa chat_id fornecido ou tenta descobrir
            chat_ids = set()
            
            if chat_id_override:
                chat_ids.add(chat_id_override)
            else:
                # Tenta obter de atualizações recentes
                try:
                    updates = await bot.get_updates(limit=10)
                    for update in updates:
                        if update.message:
                            chat_ids.add(str(update.message.chat_id))
                        elif update.channel_post:
                            chat_ids.add(str(update.channel_post.chat_id))
                except Exception:
                    pass
                
                # Adiciona IDs conhecidos do histórico
                for cid in CHAT_IDS_CONHECIDOS:
                    chat_ids.add(cid)
            
            if not chat_ids:
                print(f"   ⚠️  Nenhum chat encontrado para {nome}")
                continue
            
            # Envia para todos os chats encontrados
            timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")
            mensagem = MENSAGEM_SAUDACAO.format(timestamp=timestamp)
            
            for chat_id in chat_ids:
                try:
                    await bot.send_message(
                        chat_id=int(chat_id), 
                        text=mensagem,
                        parse_mode='Markdown'
                    )
                    print(f"   ✅ Enviado para chat {chat_id}")
                    resultados.append({"canal": "Telegram", "chat_id": chat_id, "status": "✅"})
                except Exception as e:
                    print(f"   ❌ Erro no chat {chat_id}: {e}")
                    resultados.append({"canal": "Telegram", "chat_id": chat_id, "status": "❌", "erro": str(e)})
                    
        except Exception as e:
            print(f"❌ Erro com {nome}: {e}")
    
    return resultados

# ═══════════════════════════════════════════════════════════════════════════════
# 📲 WHATSAPP (Evolution API)
# ═══════════════════════════════════════════════════════════════════════════════

def enviar_whatsapp(numero_destino=None):
    """Envia mensagem via WhatsApp Evolution API"""
    base_url = os.getenv("WHATSAPP_BASE_URL", "").rstrip('/')
    token = os.getenv("WHATSAPP_API_TOKEN_INSTANCE")
    instance = os.getenv("WHATSAPP_INSTANCE_NAME", "cleudocode")
    
    if not base_url or not token:
        print("⚠️  WhatsApp não configurado (WHATSAPP_BASE_URL ou TOKEN ausente)")
        return []
    
    resultados = []
    
    # Primeiro, verifica o status da conexão
    try:
        status_url = f"{base_url}/instance/connectionState/{instance}"
        headers = {"apikey": token, "Content-Type": "application/json"}
        
        resp = requests.get(status_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            state = data.get('instance', {}).get('state', 'unknown')
            print(f"📲 WhatsApp ({instance}): {state}")
            
            if state != 'open':
                print("   ⚠️  WhatsApp não está conectado!")
                return resultados
        else:
            print(f"   ❌ Erro ao verificar status: {resp.status_code}")
            return resultados
            
    except Exception as e:
        print(f"❌ Erro ao conectar na Evolution API: {e}")
        return resultados
    
    # Se tiver número de destino, envia a mensagem
    if numero_destino:
        timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")
        mensagem = MENSAGEM_SAUDACAO.format(timestamp=timestamp)
        # Remove markdown para WhatsApp (usa formatação diferente)
        mensagem = mensagem.replace('*', '_')
        
        url = f"{base_url}/message/sendText/{instance}"
        payload = {
            "number": numero_destino,
            "text": mensagem,
            "options": {
                "delay": 1200,
                "presence": "composing"
            }
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code in [200, 201]:
                print(f"   ✅ Enviado para {numero_destino}")
                resultados.append({"canal": "WhatsApp", "numero": numero_destino, "status": "✅"})
            else:
                print(f"   ❌ Erro: {resp.status_code} - {resp.text}")
                resultados.append({"canal": "WhatsApp", "numero": numero_destino, "status": "❌"})
        except Exception as e:
            print(f"   ❌ Erro ao enviar: {e}")
    else:
        print("   ℹ️  WhatsApp ativo! Use --whatsapp <numero> para enviar.")
    
    return resultados

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 EXECUÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("""
╭────────────────────────────────────╮
│  📢 Cleudocode - Saudação Inicial  │
╰────────────────────────────────────╯
""")
    
    timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")
    print(f"🕐 {timestamp}\n")
    
    todos_resultados = []
    
    # 1. Envia para Telegram
    print("━━━ TELEGRAM ━━━")
    try:
        telegram_results = asyncio.run(enviar_telegram())
        todos_resultados.extend(telegram_results)
    except Exception as e:
        print(f"❌ Erro no Telegram: {e}")
    
    print()
    
    # 2. Verifica/Envia WhatsApp
    print("━━━ WHATSAPP ━━━")
    numero_whatsapp = None
    if len(sys.argv) > 2 and sys.argv[1] == "--whatsapp":
        numero_whatsapp = sys.argv[2]
    
    whatsapp_results = enviar_whatsapp(numero_whatsapp)
    todos_resultados.extend(whatsapp_results)
    
    # Resumo
    print("\n" + "═" * 40)
    print("📊 RESUMO")
    print("═" * 40)
    
    if todos_resultados:
        for r in todos_resultados:
            canal = r.get('canal', '?')
            status = r.get('status', '?')
            destino = r.get('chat_id') or r.get('numero', '?')
            print(f"  {status} {canal}: {destino}")
    else:
        print("  Nenhuma mensagem enviada")
    
    print("\n© Automações Comerciais Integradas 2026 ⚙️")
    print("contato@automacoescomerciais.com.br")

if __name__ == "__main__":
    main()
