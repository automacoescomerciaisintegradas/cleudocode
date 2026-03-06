#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot - Community Welcome Agent
Bot de acolhimento para comunidades de IA no Telegram
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Carregar ambiente
load_dotenv()

# Configurações
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("WELCOME_MODEL", "llama3:8b")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Contexto por usuário
user_contexts = {}

def load_welcome_agent_persona():
    """Carrega a persona do Welcome Agent"""
    persona_file = Path("agents/welcome_agent.md")
    if persona_file.exists():
        return persona_file.read_text(encoding='utf-8')
    return "Você é um assistente de acolhimento para comunidades de IA."

def chat_with_llm(messages):
    """
    Envia mensagens para o LLM (Ollama)
    """
    import requests
    
    url = f"{OLLAMA_HOST}/v1/chat/completions"
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        return "Desculpe, não consegui processar sua mensagem."
    except Exception as e:
        logger.error(f"Erro LLM: {e}")
        return "⚠️ Estou com dificuldade de processar no momento. Tente novamente em instantes."

def diagnose_knowledge_level(message):
    """Diagnostica nível de conhecimento"""
    diagnosis_prompt = f"""
Analise a mensagem e classifique o nível:
- BEGINNER (iniciante)
- INTERMEDIATE (já conhece básico)
- ADVANCED (avançado)

Mensagem: "{message}"

Responda APENAS: BEGINNER, INTERMEDIATE ou ADVANCED
"""
    response = chat_with_llm([{"role": "user", "content": diagnosis_prompt}])
    return response.strip().upper()

def get_routing_resource(need, level):
    """Retorna recurso ideal"""
    routing_matrix = {
        "BEGINNER": {
            "default": "🎯 Comece aqui: https://docs.cleudocode.com/inicio"
        },
        "INTERMEDIATE": {
            "default": "📖 Docs: https://docs.cleudocode.com"
        },
        "ADVANCED": {
            "default": "🚀 Advanced: https://docs.cleudocode.com/advanced"
        }
    }
    
    level_resources = routing_matrix.get(level, routing_matrix["INTERMEDIATE"])
    return level_resources.get("default", "📖 Documentação: https://docs.cleudocode.com")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Inicializa contexto
    user_contexts[user_id] = {
        "name": user.first_name,
        "knowledge_level": None,
        "history": []
    }
    
    persona = load_welcome_agent_persona()
    
    welcome_message = f"""
{persona}

Gere uma mensagem de boas-vindas calorosa para:
Nome: {user.first_name}

Siga a estrutura:
1. Saudação calorosa (use o nome)
2. Expressão de interesse em ajudar
3. Convite para compartilhar necessidade

Mantenha curto (máx 100 palavras), use emojis naturalmente.
"""
    
    messages = [
        {"role": "system", "content": "Você é um assistente de acolhimento caloroso."},
        {"role": "user", "content": welcome_message}
    ]
    
    response = chat_with_llm(messages)
    
    await update.message.reply_text(response)
    logger.info(f"Welcome enviado para {user.first_name} (ID: {user_id})")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    help_text = """
🤗 **Comandos Disponíveis:**

/start - Reinicia o acolhimento
/help - Mostra esta ajuda
/status - Mostra seu nível detectado
/reset - Reinicia sua conversa

💡 **Como funciona:**
1. Me conte sua dúvida ou necessidade
2. Eu diagnostico seu nível
3. Te direciono para o recurso exato

Tudo em até 3 mensagens! 🚀
"""
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    user_id = str(update.effective_user.id)
    ctx = user_contexts.get(user_id)
    
    if ctx:
        level = ctx.get("knowledge_level", "Não diagnosticado")
        name = ctx.get("name", "Usuário")
        msgs = len(ctx.get("history", []))
        
        status = f"""
📊 **Status do Membro**

👤 Nome: {name}
📈 Nível: {level or 'Não diagnosticado'}
💬 Mensagens: {msgs}

Precisa de algo mais? É só me contar! 😊
"""
    else:
        status = "⚠️ Nenhum contexto encontrado. Use /start para começar."
    
    await update.message.reply_text(status)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /reset"""
    user_id = str(update.effective_user.id)
    user_contexts[user_id] = {
        "name": update.effective_user.first_name,
        "knowledge_level": None,
        "history": []
    }
    
    await update.message.reply_text(
        "🔄 Conversa reiniciada!\n\n" +
        "Agora me conte: como posso te ajudar hoje? 😊"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto"""
    user = update.effective_user
    user_id = str(user.id)
    message_text = update.message.text
    
    # Inicializa contexto se necessário
    if user_id not in user_contexts:
        user_contexts[user_id] = {
            "name": user.first_name,
            "knowledge_level": None,
            "history": []
        }
    
    ctx = user_contexts[user_id]
    
    # Diagnóstico de nível (se ainda não feito)
    if not ctx["knowledge_level"]:
        level = diagnose_knowledge_level(message_text)
        if level in ["BEGINNER", "INTERMEDIATE", "ADVANCED"]:
            ctx["knowledge_level"] = level
            logger.info(f"Nível detectado para {user.first_name}: {level}")
    
    # Monta prompt com contexto
    persona = load_welcome_agent_persona()
    
    context_msg = f"""
Contexto do membro:
- Nome: {ctx['name']}
- Nível: {ctx['knowledge_level'] or 'Não diagnosticado'}
- Histórico: {len(ctx['history'])} mensagens

Mensagem: {message_text}

Aplique o protocolo de acolhimento (Camada 1):
1. Valide de forma empática
2. Se necessário, faça 1-3 perguntas de diagnóstico
3. Se já tiver clareza, direcione para o recurso exato

Seja caloroso, use emojis naturalmente, resposta concisa.
"""
    
    messages = [
        {"role": "system", "content": persona},
        {"role": "user", "content": context_msg}
    ]
    
    response = chat_with_llm(messages)
    
    # Envia resposta (pode ser dividida se longa)
    await update.message.reply_text(response)
    
    # Atualiza histórico
    ctx["history"].append({
        "member": message_text,
        "agent": response
    })
    
    logger.info(f"Mensagem de {user.first_name} processada")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Erro: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Ocorreu um erro. Tente novamente ou use /reset."
        )

def main():
    """Inicia o bot"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN não configurado!")
        print("\n❌ Erro: TELEGRAM_BOT_TOKEN não encontrado no .env")
        print("\nPara configurar:")
        print("1. Crie um bot no Telegram via @BotFather")
        print("2. Copie o token")
        print("3. Adicione no .env: TELEGRAM_BOT_TOKEN=seu_token_aqui")
        sys.exit(1)
    
    print("=" * 60)
    print("  🤗 Telegram Bot - Community Welcome Agent")
    print("  Acolhimento Inteligente para Comunidades de IA")
    print("=" * 60)
    print(f"  Token: {'Configurado ✓' if TELEGRAM_TOKEN else 'Não configurado ✗'}")
    print(f"  Modelo: {MODEL}")
    print(f"  Ollama: {OLLAMA_HOST}")
    print("=" * 60)
    print("\n🤖 Bot iniciado! Aguardando mensagens...\n")
    
    # Cria aplicação
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)
    
    # Inicia polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
