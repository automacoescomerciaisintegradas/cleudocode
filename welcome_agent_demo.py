#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Community Welcome Agent (Sem dependência do Ollama)
Demonstração da lógica de acolhimento e roteamento
"""

import json
from datetime import datetime

# =============================================================================
# LÓGICA DE DIAGNÓSTICO (Regras baseadas em palavras-chave)
# =============================================================================

def diagnose_knowledge_level_rulebased(message):
    """
    Diagnostica nível de conhecimento usando regras (sem LLM)
    """
    message_lower = message.lower()
    
    # Palavras-chave por nível
    beginner_keywords = [
        'o que é', 'o que eh', 'como começar', 'como comecar',
        'iniciante', 'nunca usei', 'não sei nada', 'nao sei nada',
        'primeiro', 'básico', 'basico', 'do zero', 'aprender agora'
    ]
    
    advanced_keywords = [
        'arquitetura', 'escalar', 'otimizar', 'performance',
        'avançado', 'avançado', 'complexo', 'produção',
        'milhões', 'milhares', 'req/s', 'alta escala',
        'cluster', 'distributed', 'microserviços'
    ]
    
    # Conta ocorrências
    beginner_score = sum(1 for kw in beginner_keywords if kw in message_lower)
    advanced_score = sum(1 for kw in advanced_keywords if kw in message_lower)
    
    # Classifica
    if beginner_score > 0 and advanced_score == 0:
        return "BEGINNER"
    elif advanced_score > 0 and beginner_score == 0:
        return "ADVANCED"
    elif beginner_score == 0 and advanced_score == 0:
        return "INTERMEDIATE"  # Padrão
    else:
        # Misto - decide pelo maior
        return "ADVANCED" if advanced_score > beginner_score else "BEGINNER"

def get_routing_resource(need, level):
    """
    Retorna recurso ideal baseado na necessidade e nível
    """
    routing_matrix = {
        "BEGINNER": {
            "tutorial": {
                "title": "📚 Onboarding Guiado",
                "url": "https://docs.cleudocode.com/iniciante",
                "time": "15 min",
                "description": "Tutorial passo a passo com exemplos práticos"
            },
            "conceitos": {
                "title": "💡 Conceitos Básicos",
                "url": "https://docs.cleudocode.com/conceitos",
                "time": "10 min",
                "description": "Entenda os fundamentos de IA e automação"
            },
            "default": {
                "title": "🎯 Comece Aqui",
                "url": "https://docs.cleudocode.com/inicio",
                "time": "5 min",
                "description": "Ponto de partida ideal para iniciantes"
            }
        },
        "INTERMEDIATE": {
            "api": {
                "title": "🔌 Documentação API",
                "url": "https://docs.cleudocode.com/api",
                "time": "20 min",
                "description": "Referência completa da API com exemplos"
            },
            "automacao": {
                "title": "⚙️ Automações",
                "url": "https://docs.cleudocode.com/automacao",
                "time": "25 min",
                "description": "Templates e receitas prontas"
            },
            "integracao": {
                "title": "🔗 Integrações",
                "url": "https://docs.cleudocode.com/integracoes",
                "time": "15 min",
                "description": "Conecte com WhatsApp, Telegram, etc"
            },
            "default": {
                "title": "📖 Documentação Completa",
                "url": "https://docs.cleudocode.com",
                "time": "-",
                "description": "Tudo que você precisa"
            }
        },
        "ADVANCED": {
            "arquitetura": {
                "title": "🏗️ Arquitetura",
                "url": "https://docs.cleudocode.com/arquitetura",
                "time": "30 min",
                "description": "Padrões avançados e best practices"
            },
            "otimizacao": {
                "title": "⚡ Performance",
                "url": "https://docs.cleudocode.com/performance",
                "time": "25 min",
                "description": "Otimização e escalabilidade"
            },
            "custom": {
                "title": "🛠️ Customização Avançada",
                "url": "https://docs.cleudocode.com/advanced",
                "time": "40 min",
                "description": "Extensões e modificações complexas"
            },
            "default": {
                "title": "🚀 Advanced Docs",
                "url": "https://docs.cleudocode.com/advanced",
                "time": "-",
                "description": "Recursos para usuários avançados"
            }
        }
    }
    
    level_resources = routing_matrix.get(level, routing_matrix["INTERMEDIATE"])
    
    # Detecta palavra-chave na necessidade
    need_lower = need.lower()
    
    if any(kw in need_lower for kw in ['tutorial', 'começar', 'comecar', 'iniciar', 'aprender']):
        return level_resources.get("tutorial", level_resources["default"])
    elif any(kw in need_lower for kw in ['api', 'integração', 'integracao', 'conectar']):
        return level_resources.get("api", level_resources["default"])
    elif any(kw in need_lower for kw in ['automa', 'bot', 'telegram', 'whatsapp']):
        return level_resources.get("automacao", level_resources["default"])
    elif any(kw in need_lower for kw in ['arquitet', 'otimiz', 'perform', 'escal']):
        return level_resources.get("arquitetura", level_resources["default"])
    else:
        return level_resources["default"]

def generate_welcome_response(name, message, level, resource):
    """
    Gera resposta de acolhimento baseada no nível
    """
    templates = {
        "BEGINNER": f"""
Olá, {name}! 👋 Seja muito bem-vindo(a) à nossa comunidade de IA!

Fico muito feliz em saber que você quer {message[:50]}...

📍 **Seu perfil:** Iniciante em IA/automação

**Não se preocupe!** Todo mundo começa por aqui. 😊

📍 **Seu próximo passo:**

→ **{resource['title']}:** {resource['url']}
   - Tempo estimado: {resource['time']}
   - {resource['description']}

💡 **Dica:** Vá com calma, faça no seu ritmo e não hesite em perguntar!

Quer que eu te acompanhe em algum ponto específico? Estou aqui! 😊
""",
        "INTERMEDIATE": f"""
Olá, {name}! 🚀 Que bom te ver por aqui!

Vi que você quer {message[:50]}...

📍 **Seu perfil:** Já tem familiaridade com IA/automação

📍 **Recurso ideal para você:**

→ **{resource['title']}:** {resource['url']}
   - Tempo estimado: {resource['time']}
   - {resource['description']}

🔧 **Atalho:** Aproveite os exemplos práticos que já estão prontos!

Precisa de ajuda com algum detalhe da implementação? Só chamar! 💪
""",
        "ADVANCED": f"""
Excelente, {name}! 🎯

Sua questão sobre "{message[:50]}..." mostra que você já está em nível avançado!

📍 **Recursos especializados:**

→ **{resource['title']}:** {resource['url']}
   - Tempo estimado: {resource['time']}
   - {resource['description']}

🎯 **Sugestão:** Dada a complexidade, se precisar de uma discussão mais técnica, posso te conectar com nosso time de engenharia!

À disposição para detalhes! 💪
""",
    }
    
    return templates.get(level, templates["INTERMEDIATE"])

# =============================================================================
# DEMONSTRAÇÃO
# =============================================================================

def demo():
    print("=" * 70)
    print("  🤗 DEMO: Community Welcome Agent - Camada 1")
    print("  Acolhimento Inteligente para Comunidades de IA")
    print("=" * 70)
    print()
    
    # Cenários de teste
    test_cases = [
        {
            "name": "Maria Silva",
            "message": "Quero criar automações com IA mas não sei por onde começar, nunca usei nada disso",
            "expected_level": "BEGINNER"
        },
        {
            "name": "João Santos",
            "message": "Preciso integrar WhatsApp com meu sistema de vendas",
            "expected_level": "INTERMEDIATE"
        },
        {
            "name": "Ana Costa",
            "message": "Qual a melhor arquitetura para escalar webhooks com 10k requisições por segundo?",
            "expected_level": "ADVANCED"
        },
        {
            "name": "Pedro Oliveira",
            "message": "Como crio um bot simples para Telegram?",
            "expected_level": "INTERMEDIATE"
        },
        {
            "name": "Carla Mendes",
            "message": "O que é IA? Quero entender o básico antes de começar",
            "expected_level": "BEGINNER"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"  CENÁRIO {i}: {case['name']}")
        print(f"{'='*70}")
        
        # Diagnóstico
        level = diagnose_knowledge_level_rulebased(case['message'])
        status = "✅" if level == case['expected_level'] else "❌"
        
        print(f"\n📊 Diagnóstico: {level} {status}")
        print(f"   Esperado: {case['expected_level']}")
        
        # Roteamento
        resource = get_routing_resource(case['message'], level)
        
        print(f"\n📍 Recurso recomendado:")
        print(f"   {resource['title']}")
        print(f"   {resource['url']}")
        print(f"   {resource['description']}")
        
        # Resposta completa
        response = generate_welcome_response(case['name'], case['message'], level, resource)
        
        print(f"\n🤖 Resposta do Welcome Agent:")
        print("-" * 70)
        print(response)
        print("-" * 70)
    
    print(f"\n{'='*70}")
    print("  DEMONSTRAÇÃO CONCLUÍDA!")
    print(f"{'='*70}")
    print()
    print("💡 Para usar com LLM real (Ollama), execute:")
    print("   python3 welcome_agent_chat.py")
    print()
    print("📱 Para Telegram bot:")
    print("   python3 telegram_welcome_bot.py")
    print()

if __name__ == "__main__":
    demo()
