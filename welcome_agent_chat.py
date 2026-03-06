#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Community Welcome Agent - Camada 1
Assistente conversacional de acolhimento para comunidades de IA
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Carregar ambiente
load_dotenv()

# Configurações - Forçar localhost se IP externo falhar
OLLAMA_HOST_ENV = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')

# Fix automático: Se for IP externo, usa localhost
if "144.91.118.78" in OLLAMA_HOST_ENV:
    OLLAMA_HOST = "http://localhost:11434"
else:
    OLLAMA_HOST = OLLAMA_HOST_ENV

MODEL = os.getenv("WELCOME_MODEL", os.getenv("OLLAMA_MODEL", "llama3:8b"))

# Histórico da conversa
conversation_history = []
member_context = {
    "name": None,
    "knowledge_level": None,
    "need": None,
    "routed_to": None
}

def load_welcome_agent_persona():
    """Carrega a persona do Welcome Agent"""
    persona_file = Path("agents/welcome_agent.md")
    if persona_file.exists():
        return persona_file.read_text(encoding='utf-8')
    return "Você é um assistente de acolhimento para comunidades de IA."

def chat_with_llm(messages, timeout=10):
    """
    Envia mensagens para o LLM (Ollama)
    Com timeout configurável
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
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        return "Desculpe, não consegui processar sua mensagem."
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

def diagnose_knowledge_level(message):
    """
    Diagnostica nível de conhecimento do membro
    Com fallback para regras se Ollama falhar
    """
    # Tenta primeiro com Ollama
    try:
        diagnosis_prompt = f"""
Analise a mensagem abaixo e classifique o nível de conhecimento da pessoa em:
- BEGINNER (iniciante, nunca usou IA/automação)
- INTERMEDIATE (já conhece conceitos básicos, quer implementar)
- ADVANCED (já constrói sistemas complexos, otimização/arquitetura)

Mensagem: "{message}"

Responda APENAS com: BEGINNER, INTERMEDIATE ou ADVANCED
"""
        response = chat_with_llm([{"role": "user", "content": diagnosis_prompt}])
        
        if "BEGINNER" in response.upper():
            return "BEGINNER"
        elif "ADVANCED" in response.upper():
            return "ADVANCED"
        elif "INTERMEDIATE" in response.upper():
            return "INTERMEDIATE"
    except Exception as e:
        print(f"  ⚠️  Ollama indisponível, usando fallback...")
    
    # Fallback: regras baseadas em palavras-chave
    return diagnose_knowledge_level_rules(message)

def diagnose_knowledge_level_rules(message):
    """
    Diagnóstico por regras (fallback)
    """
    message_lower = message.lower()
    
    beginner_keywords = ['o que é', 'como começar', 'iniciante', 'nunca usei', 
                         'não sei', 'nao sei', 'do zero', 'básico', 'basico']
    advanced_keywords = ['arquitetura', 'escalar', 'otimizar', 'avançado', 
                         'complexo', 'produção', 'req/s', 'alta escala']
    
    beginner_score = sum(1 for kw in beginner_keywords if kw in message_lower)
    advanced_score = sum(1 for kw in advanced_keywords if kw in message_lower)
    
    if beginner_score > 0 and advanced_score == 0:
        return "BEGINNER"
    elif advanced_score > 0:
        return "ADVANCED"
    else:
        return "INTERMEDIATE"

def get_routing_resource(need, level):
    """
    Retorna o recurso ideal baseado na necessidade e nível
    """
    routing_matrix = {
        "BEGINNER": {
            "tutorial": "📚 Onboarding Guiado: https://docs.cleudocode.com/iniciante",
            "conceitos": "💡 Conceitos Básicos: https://docs.cleudocode.com/conceitos",
            "duvidas": "❓ FAQ Iniciantes: https://docs.cleudocode.com/faq",
            "default": "🎯 Comece aqui: https://docs.cleudocode.com/inicio"
        },
        "INTERMEDIATE": {
            "api": "🔌 Documentação API: https://docs.cleudocode.com/api",
            "automacao": "⚙️ Automações: https://docs.cleudocode.com/automacao",
            "integracao": "🔗 Integrações: https://docs.cleudocode.com/integracoes",
            "default": "📖 Docs Completas: https://docs.cleudocode.com"
        },
        "ADVANCED": {
            "arquitetura": "🏗️ Arquitetura: https://docs.cleudocode.com/arquitetura",
            "otimizacao": "⚡ Performance: https://docs.cleudocode.com/performance",
            "custom": "🛠️ Customização: https://docs.cleudocode.com/advanced",
            "default": "🚀 Advanced Docs: https://docs.cleudocode.com/advanced"
        }
    }
    
    level_resources = routing_matrix.get(level, routing_matrix["INTERMEDIATE"])
    
    # Detecta palavra-chave na necessidade
    need_lower = need.lower()
    if "tutorial" in need_lower or "começar" in need_lower or "iniciar" in need_lower:
        return level_resources.get("tutorial", level_resources["default"])
    elif "api" in need_lower or "integração" in need_lower or "integracao" in need_lower:
        return level_resources.get("api", level_resources["default"])
    elif "automa" in need_lower:
        return level_resources.get("automacao", level_resources["default"])
    elif "arquitet" in need_lower or "otimiz" in need_lower or "perform" in need_lower:
        return level_resources.get("arquitetura", level_resources["default"])
    else:
        return level_resources.get("default", "📖 Documentação: https://docs.cleudocode.com")

def print_help():
    print("\n--- Comandos Disponíveis ---")
    print(" /nome <nome>          : Define o nome do membro")
    print(" /level                : Mostra nível de conhecimento detectado")
    print(" /reset                : Reinicia conversa atual")
    print(" /history              : Mostra histórico da conversa")
    print(" /save                 : Salva contexto do membro")
    print(" /help                 : Mostra esta ajuda")
    print(" sair / exit           : Encerra o programa")
    print("---------------------------\n")

def welcome_member(name=None):
    """
    Gera mensagem de acolhimento inicial
    """
    persona = load_welcome_agent_persona()
    
    welcome_prompt = f"""
{persona}

Gere uma mensagem de boas-vindas calorosa e acolhedora para um novo membro da comunidade de IA.
Nome do membro: {name or 'visitante'}

Siga a estrutura:
1. Saudação calorosa
2. Expressão de interesse em ajudar
3. Convite para compartilhar sua necessidade

Mantenha a mensagem curta (máx 100 palavras), use emojis de forma natural e seja genuinamente acolhedor.
"""
    
    messages = [
        {"role": "system", "content": "Você é um assistente de acolhimento caloroso e humano."},
        {"role": "user", "content": welcome_prompt}
    ]
    
    return chat_with_llm(messages)

def main():
    global conversation_history, member_context
    
    print("=" * 60)
    print("  🤗 Community Welcome Agent - Camada 1")
    print("  Acolhimento Inteligente para Comunidades de IA")
    print("=" * 60)
    print(f"  Modelo: {MODEL}")
    print(f"  Servidor: {OLLAMA_HOST}")
    print("=" * 60)
    print("\n💡 Dica: Use /help para ver comandos\n")
    
    # Mensagem de boas-vindas inicial
    print("🤗 " + welcome_member())
    print("\n" + "-" * 60 + "\n")
    
    while True:
        try:
            user_input = input("\n📨 Membro: ").strip()
            
            if not user_input:
                continue
            
            # Comandos do Sistema
            if user_input.lower() in ['sair', 'exit', 'quit', '/stop']:
                print("\n👋 Encerrando atendimento...")
                if member_context["name"]:
                    print(f"📝 Contexto de {member_context['name']} salvo.")
                break
            
            elif user_input.lower() == '/help':
                print_help()
                continue
            
            elif user_input.lower() == '/reset':
                conversation_history = []
                member_context = {"name": None, "knowledge_level": None, "need": None, "routed_to": None}
                print("🔄 Conversa reiniciada!")
                print("\n🤗 " + welcome_member())
                continue
            
            elif user_input.lower() == '/history':
                print(json.dumps(conversation_history, indent=2, ensure_ascii=False))
                continue
            
            elif user_input.lower() == '/save':
                if member_context["name"]:
                    filename = f"member_{member_context['name'].lower().replace(' ', '_')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(member_context, f, indent=2, ensure_ascii=False)
                    print(f"✅ Contexto salvo em: {filename}")
                else:
                    print("⚠️ Use /nome <nome> primeiro!")
                continue
            
            elif user_input.lower() == '/level':
                if member_context["knowledge_level"]:
                    print(f"📊 Nível detectado: {member_context['knowledge_level']}")
                else:
                    print("⚠️ Nenhuma análise ainda. Envie uma mensagem do membro.")
                continue
            
            elif user_input.lower().startswith('/nome '):
                member_context["name"] = user_input[6:].strip()
                print(f"✅ Nome definido: {member_context['name']}")
                print("\n🤗 " + welcome_member(member_context["name"]))
                continue
            
            # Fluxo Normal de Acolhimento
            print("\n⏳ Processando...")
            
            # Diagnóstico de nível (se ainda não feito)
            if not member_context["knowledge_level"]:
                level = diagnose_knowledge_level(user_input)
                if level in ["BEGINNER", "INTERMEDIATE", "ADVANCED"]:
                    member_context["knowledge_level"] = level
                    print(f"📊 Nível detectado: {level}")
            
            # Monta contexto para o LLM
            persona = load_welcome_agent_persona()
            
            context_msg = f"""
Contexto do membro:
- Nome: {member_context['name'] or 'Não informado'}
- Nível: {member_context['knowledge_level'] or 'Não diagnosticado'}
- Necessidade anterior: {member_context['need'] or 'Primeira interação'}

Mensagem do membro: {user_input}

Aplique o protocolo de acolhimento (Camada 1):
1. Valide a mensagem de forma empática
2. Se necessário, faça 1-3 perguntas de diagnóstico
3. Se já tiver clareza, direcione para o recurso exato

Seja caloroso, use emojis naturalmente, e mantenha a resposta concisa.
"""
            
            messages = [
                {"role": "system", "content": persona},
                {"role": "user", "content": context_msg}
            ]
            
            response = chat_with_llm(messages)
            
            print(f"\n🤖 Welcome Agent: {response}")
            
            # Atualiza histórico
            conversation_history.append({
                "member": user_input,
                "agent": response,
                "level": member_context["knowledge_level"]
            })
            
            # Atualiza necessidade
            if not member_context["need"]:
                member_context["need"] = user_input[:100]
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrompido pelo usuário.")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()
