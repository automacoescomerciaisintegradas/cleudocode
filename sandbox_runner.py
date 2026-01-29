import sys
import json
import os
from core.tool_parser import parse_and_execute_tools

def main():
    """
    Ponto de entrada para o executor do sandbox.
    Lê um arquivo de tarefa, executa as ferramentas e escreve um arquivo de resultado.
    """
    if len(sys.argv) < 2:
        print("[SandboxRunner] Erro: Caminho para o arquivo de tarefa não fornecido.", file=sys.stderr)
        sys.exit(1)

    task_file_path = sys.argv[1]

    if not os.path.exists(task_file_path):
        print(f"[SandboxRunner] Erro: Arquivo de tarefa '{task_file_path}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    # 1. Ler a tarefa
    try:
        with open(task_file_path, 'r', encoding='utf-8') as f:
            task_data = json.load(f)
    except Exception as e:
        print(f"[SandboxRunner] Erro ao ler o arquivo de tarefa JSON: {e}", file=sys.stderr)
        sys.exit(1)

    task_id = task_data.get("task_id")
    tool_code_string = task_data.get("tool_code")

    if not task_id or not tool_code_string:
        print("[SandboxRunner] Erro: 'task_id' ou 'tool_code' ausentes no arquivo de tarefa.", file=sys.stderr)
        sys.exit(1)
        
    print(f"[SandboxRunner] Processando tarefa ID: {task_id}")

    # 2. Executar as ferramentas
    execution_log = parse_and_execute_tools(tool_code_string)
    if execution_log is None:
        execution_log = "Nenhuma ferramenta encontrada na string fornecida."
        
    print(f"[SandboxRunner] Execução concluída. Log:\n{execution_log}")

    # 3. Escrever o resultado
    result_filename = f"result_{task_id}.json"
    # O resultado é escrito no mesmo diretório do arquivo de tarefa
    result_file_path = os.path.join(os.path.dirname(task_file_path), result_filename)
    
    result_data = {
        "task_id": task_id,
        "execution_log": execution_log
    }

    try:
        with open(result_file_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f)
    except Exception as e:
        print(f"[SandboxRunner] Erro ao escrever o arquivo de resultado: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"[SandboxRunner] Resultado da tarefa '{task_id}' salvo em '{result_file_path}'.")
    sys.exit(0)

if __name__ == "__main__":
    main()
