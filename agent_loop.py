import os
import sys
import json
import re
import requests
from dotenv import load_dotenv
import tool_box  # Nosso novo módulo

# Carregar ambiente
load_dotenv()

# Configurações
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:7b")

def parse_and_execute_tools(llm_response):
    """
    Busca por tags <tool code="...">...</tool> na resposta e executa.
    Retorna um log de execução para ser enviado de volta ao LLM se necessário.
    """
    execution_log = ""
    
    # Regex para capturar <tool code="comando">argumento</tool>
    # Suporta multiline e atributos
    pattern = r'<tool code="([^"]+)">\s*(.*?)\s*</tool>'
    matches = re.finditer(pattern, llm_response, re.DOTALL)
    
    found_tools = False
    for match in matches:
        found_tools = True
        tool_code = match.group(1)
        tool_arg = match.group(2).strip()
        
        print(f"\n[AGENT] Executando ferramenta: {tool_code}")
        
        if tool_code == "run_shell":
            res = tool_box.run_shell(tool_arg)
            out_msg = f"STDOUT:\n{res['stdout']}\nSTDERR:\n{res['stderr']}\nReturn Code: {res['returncode']}"
            execution_log += f"--- Resultado de {tool_code} ---\n{out_msg}\n"
            print(f"[SHELL] Retorno: {res['returncode']}")
            
        elif tool_code == "write_file":
            # Espera formato: PRIMEIRO LINHA = ARQUIVO, RESTO = CONTEUDO
            parts = tool_arg.split('\n', 1)
            if len(parts) >= 2:
                filename = parts[0].strip()
                content = parts[1]
                res = tool_box.write_file(filename, content)
                execution_log += f"--- Resultado de {tool_code} ({filename}) ---\n{res['message']}\n"
                print(f"[FILE] {res['message']}")
            else:
                execution_log += f"Erro: write_file requer filename na primeira linha e conteudo depois.\n"

        elif tool_code == "read_file":
            res = tool_box.read_file(tool_arg)
            if res['success']:
                execution_log += f"--- Conteúdo de {tool_arg} ---\n{res['content']}\n"
            else:
                execution_log += f"--- Erro ao ler {tool_arg} ---\n{res['message']}\n"
        
        elif tool_code == "fetch_url":
            res = tool_box.fetch_url(tool_arg)
            if res['success']:
                execution_log += f"--- Conteúdo Web de {tool_arg} ---\n{res['content']}\n"
            else:
                execution_log += f"--- Erro ao baixar URL ---\n{res['message']}\n"
                
    if not found_tools:
        return None
        
    return execution_log

def run_agent_iteration(iteration, max_iterations):
    print(f"\n=== Iteração {iteration} / {max_iterations} [Modelo: {MODEL}] ===")
    
    # Contexto Dinâmico
    prd_content = tool_box.read_file("docs/PRD.md").get("content", "[Erro]")
    # Tenta ler features, cria se não existe
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
            
            # --- PARTE NOVA: Execução de Ferramentas ---
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
