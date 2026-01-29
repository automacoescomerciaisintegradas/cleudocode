import os
import sys
import json
import re
from dotenv import load_dotenv
from core.tool_parser import parse_and_execute_tools

# Carregar ambiente
load_dotenv()

# Configurações
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:7b")

def run_agent_iteration(iteration, max_iterations):
    print(f"\n=== Iteração {iteration} / {max_iterations} [Modelo: {MODEL}] ===")
    
    # Contexto Dinâmico
    # O tool_box é usado aqui para ler os arquivos de contexto
    prd_content = tool_box.read_file("docs/PRD.md").get("content", "[Erro]")
    if not os.path.exists("features.json"):
        tool_box.write_file("features.json", "[]")
    features_content = tool_box.read_file("features.json").get("content", "[]")
    
    prompt = f"""
Você é um Engenheiro de Software Autônomo Sênior.
Estamos trabalhando no projeto LLM P2P Chat.

=== CONTEXTO DO PROJETO ===
PRD (Requisitos):
{prd_content[:2000]}... (truncado se muito longo)

FEATURES JÁ IMPLEMENTADAS:
{features_content}

=== SUAS FERRAMENTAS ===
Você pode e DEVE executar ações reais usando tags XML:

1. Executar comandos de terminal:
<tool code="run_shell">
npm run test
</tool>

2. Criar/Editar arquivos (Primeira linha é o nome, depois o conteúdo):
<tool code="write_file">
src/teste.py
print("Ola mundo")
</tool>

3. Ler arquivos:
<tool code="read_file">
src/app.py
</tool>

4. Ler páginas Web (URL):
<tool code="fetch_url">
https://exemplo.com/docs
</tool>

=== MISSÃO DA ITERAÇÃO ===
1. Analise o status atual.
2. Use ferramentas para explorar ou testar se necessário.
3. Implemente a próxima feature ou correção.
4. Se terminou tudo, responda apenas: <promise>COMPLETE</promise>

Pense passo a passo. Se for escrever código, use a ferramenta write_file.
"""

    # Envio para API
    url = f"{OLLAMA_HOST}/v1/chat/completions"
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2, # Mais determinístico para código
        "stream": False
    }
    
    try:
        print(f"Pensando...")
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        
        content = ""
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]
            print("\n--- RESPOSTA DO AGENTE ---")
            print(content)
            print("--------------------------")
            
            # --- Execução de Ferramentas via core.tool_parser ---
            exec_log = parse_and_execute_tools(content)
            if exec_log:
                print("\n--- RESULTADO DAS EXECUÇÕES ---")
                print(exec_log)
                
                # Opcional: Poderíamos enviar o resultado de volta para o LLM num loop interno ("ReAct Loop")
                # Mas por enquanto, vamos apenas logar e ir para a próxima iteração do loop principal.
                
        return content

    except Exception as e:
        print(f"Erro no loop: {e}")
        return ""

def main():
    if len(sys.argv) < 2:
        print("Uso: python agent_loop.py <numero_de_iteracoes>")
        sys.exit(1)
        
    try:
        iterations = int(sys.argv[1])
        for i in range(1, iterations + 1):
            result = run_agent_iteration(i, iterations)
            if result and "<promise>COMPLETE</promise>" in result:
                print(f"🎉 Trabalho concluído!")
                sys.exit(0)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")

if __name__ == "__main__":
    main()
