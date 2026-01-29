"""
Demonstração do Hub de LLMs - Como usar diferentes modelos para diferentes casos de uso
"""

from core.llm_providers import llm_hub

def demo_hub_uso():
    """Demonstra como usar diferentes provedores e modelos"""
    
    print("=== Demonstração do Hub de LLMs ===\n")
    
    # 1. Listar modelos disponíveis
    print("1. Modelos disponíveis por provedor:")
    modelos = llm_hub.list_models()
    for provedor, lista_modelos in modelos.items():
        print(f"   {provedor}: {lista_modelos}")
    print()
    
    # 2. Exemplo de consulta com diferentes modelos
    mensagens_exemplo = [
        {"role": "system", "content": "Você é um assistente útil."},
        {"role": "user", "content": "Qual é a capital do Brasil?"}
    ]
    
    print("2. Exemplos de consultas:")
    
    # Usando modelo padrão (Ollama)
    try:
        resposta = llm_hub.query(mensagens_exemplo, "qwen2.5-coder:7b")
        print(f"   Ollama (qwen2.5-coder:7b): {resposta[:100]}...")
    except Exception as e:
        print(f"   Ollama indisponível: {e}")
    
    # Se tivermos OpenAI configurado
    try:
        resposta = llm_hub.query(mensagens_exemplo, "gpt-4o", provider="openai")
        print(f"   OpenAI (gpt-4o): {resposta[:100]}...")
    except Exception as e:
        print(f"   OpenAI indisponível: {e}")
    
    # Se tivermos Anthropic configurado
    try:
        resposta = llm_hub.query(mensagens_exemplo, "claude-3-haiku-20240307", provider="anthropic")
        print(f"   Anthropic (claude-3-haiku): {resposta[:100]}...")
    except Exception as e:
        print(f"   Anthropic indisponível: {e}")
    
    # Se tivermos OpenRouter configurado
    try:
        resposta = llm_hub.query(mensagens_exemplo, "google/gemini-flash-2.0", provider="openrouter")
        print(f"   OpenRouter (gemini-flash-2.0): {resposta[:100]}...")
    except Exception as e:
        print(f"   OpenRouter indisponível: {e}")
    
    print()
    
    # 3. Demonstração de seleção automática de provedor
    print("3. Demonstração de seleção automática de provedor:")
    
    modelos_para_testar = [
        "gpt-4o",           # Deve ir para OpenAI
        "claude-3-opus-20240229",  # Deve ir para Anthropic
        "meta-llama/llama-3.1-405b-instruct",  # Deve ir para OpenRouter
        "qwen2.5-coder:7b"  # Deve ir para Ollama
    ]
    
    for modelo in modelos_para_testar:
        try:
            resposta = llm_hub.query(mensagens_exemplo, modelo)
            print(f"   {modelo}: [resposta obtida]")
        except Exception as e:
            print(f"   {modelo}: indisponível ({e})")
    
    print("\n=== Fim da Demonstração ===")


def exemplo_selecao_modelo(caso_de_uso: str, requisitos: dict = None):
    """
    Função de exemplo que seleciona automaticamente o melhor modelo com base no caso de uso
    """
    if caso_de_uso == "codigo":
        # Para geração de código, prioriza Claude Opus ou modelos especializados
        if requisitos and requisitos.get("prioridade") == "alta":
            return llm_hub.query(
                [{"role": "user", "content": requisitos.get("prompt", "")}],
                "claude-3-opus-20240229",
                provider="anthropic"
            )
        else:
            return llm_hub.query(
                [{"role": "user", "content": requisitos.get("prompt", "")}],
                "gpt-4o",
                provider="openai"
            )
    
    elif caso_de_uso == "conversa":
        # Para conversas normais, pode usar modelos mais rápidos e baratos
        return llm_hub.query(
            [{"role": "user", "content": requisitos.get("prompt", "")}],
            "claude-3-haiku-20240307",
            provider="anthropic"
        )
    
    elif caso_de_uso == "subagente":
        # Para tarefas secundárias, pode usar modelos grátis
        return llm_hub.query(
            [{"role": "user", "content": requisitos.get("prompt", "")}],
            "google/gemini-flash-2.0",
            provider="openrouter"
        )
    
    else:
        # Caso padrão, usa o modelo configurado
        from core.config import settings
        return llm_hub.query(
            [{"role": "user", "content": requisitos.get("prompt", "")}],
            settings.LLM_MODEL
        )


if __name__ == "__main__":
    demo_hub_uso()
    
    print("\n" + "="*50)
    print("EXEMPLO: Seleção de modelo por caso de uso")
    print("="*50)
    
    # Exemplo de uso baseado em caso de uso
    requisito_codigo = {
        "prompt": "Escreva uma função Python para calcular o fatorial de um número",
        "prioridade": "alta"
    }
    
    resultado = exemplo_selecao_modelo("codigo", requisito_codigo)
    print(f"Geração de código: {resultado[:100]}...")