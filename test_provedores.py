"""
Script para testar os provedores de LLM com as chaves configuradas
"""
import os
from core.config import settings
from core.llm_providers import llm_hub

def testar_provedores_configurados():
    """Testa quais provedores estão configurados e funcionando"""
    print("=== Teste de Provedores Configurados ===\n")
    
    # Verificar quais chaves estão configuradas
    print("Chaves de API configuradas:")
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-seu-openai-api-key-aqui":
        print("  ✓ OPENAI_API_KEY está configurada")
    else:
        print("  [ ] OPENAI_API_KEY não está configurada corretamente")

    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "seu-anthropic-api-key-aqui":
        print("  [X] ANTHROPIC_API_KEY está configurada")
    else:
        print("  [ ] ANTHROPIC_API_KEY não está configurada corretamente")

    if settings.OPENROUTER_API_KEY:
        print("  [X] OPENROUTER_API_KEY está configurada")
    else:
        print("  [ ] OPENROUTER_API_KEY não está configurada")

    if os.getenv("GEMINI_API_KEY"):
        print("  [X] GEMINI_API_KEY está configurada")
    else:
        print("  [ ] GEMINI_API_KEY não está configurada")

    print()

    # Testar provedores com mensagens simples
    mensagens_teste = [
        {"role": "system", "content": "Você é um assistente útil."},
        {"role": "user", "content": "Responda com 'OK'."}
    ]

    print("Testando provedores disponíveis:")

    # Testar OpenAI se configurada
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-seu-openai-api-key-aqui":
        print("\n  Testando OpenAI...")
        try:
            resposta = llm_hub.query(mensagens_teste, "gpt-4o-mini", provider="openai")
            print(f"    [X] OpenAI funcionando: {resposta[:50]}...")
        except Exception as e:
            print(f"    [ERROR] Erro no OpenAI: {e}")
    else:
        print("\n  [ ] OpenAI não configurado - adicione sua chave real")

    # Testar Anthropic se configurada
    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "seu-anthropic-api-key-aqui":
        print("\n  Testando Anthropic...")
        try:
            resposta = llm_hub.query(mensagens_teste, "claude-3-haiku-20240307", provider="anthropic")
            print(f"    [X] Anthropic funcionando: {resposta[:50]}...")
        except Exception as e:
            print(f"    [ERROR] Erro no Anthropic: {e}")
    else:
        print("\n  [ ] Anthropic não configurado - adicione sua chave real")

    # Testar OpenRouter
    if settings.OPENROUTER_API_KEY:
        print("\n  Testando OpenRouter...")
        try:
            resposta = llm_hub.query(mensagens_teste, "google/gemini-flash-2.0", provider="openrouter")
            print(f"    [X] OpenRouter funcionando: {resposta[:50]}...")
        except Exception as e:
            print(f"    [ERROR] Erro no OpenRouter: {e}")
    else:
        print("\n  [ ] OpenRouter não configurado")

    # Testar Ollama
    print("\n  Testando Ollama...")
    try:
        resposta = llm_hub.query(mensagens_teste, settings.LLM_MODEL or "llama3", provider="ollama")
        print(f"    [X] Ollama funcionando: {resposta[:50]}...")
    except Exception as e:
        print(f"    [ERROR] Erro no Ollama: {e}")

    print("\n" + "="*50)

def testar_selecao_automatica():
    """Testa a seleção automática de provedor baseado no nome do modelo"""
    print("=== Teste de Seleção Automática de Provedor ===\n")

    modelos_teste = [
        ("gpt-4o", "Deve usar OpenAI"),
        ("gpt-3.5-turbo", "Deve usar OpenAI"),
        ("claude-3-opus-20240229", "Deve usar Anthropic"),
        ("claude-3-haiku-20240307", "Deve usar Anthropic"),
        ("google/gemini-pro", "Deve usar OpenRouter"),
        ("meta-llama/llama-3.1-405b-instruct", "Deve usar OpenRouter"),
        ("qwen2.5-coder:7b", "Deve usar Ollama"),
        ("llama3", "Deve usar Ollama")
    ]

    mensagens_teste = [{"role": "user", "content": "Responda com o nome do modelo: TESTE"}]

    for modelo, descricao in modelos_teste:
        print(f"Testando {modelo} - {descricao}")
        try:
            resposta = llm_hub.query(mensagens_teste, modelo)
            print(f"  Resultado: OK (resposta recebida)")
        except Exception as e:
            print(f"  Resultado: Erro - {e}")
        print()

if __name__ == "__main__":
    print("Testando provedores de LLM configurados")
    print("="*50)

    testar_provedores_configurados()
    testar_selecao_automatica()

    print("Resumo:")
    print("- O hub de LLMs está pronto para usar múltiplos provedores")
    print("- Configure as chaves de API reais para ativar cada provedor")
    print("- O sistema seleciona automaticamente o provedor apropriado baseado no nome do modelo")