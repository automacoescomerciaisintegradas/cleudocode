import re
import tool_box

def parse_and_execute_tools(llm_response: str):
    """
    Busca por tags <tool code="...">...</tool> na resposta, executa as ferramentas
    correspondentes e retorna um log de execução.

    Args:
        llm_response: A string de texto gerada pelo LLM.

    Returns:
        Uma string contendo o log concatenado da execução de todas as ferramentas.
        Retorna None se nenhuma ferramenta for encontrada.
    """
    execution_log = ""
    
    # Regex para capturar <tool code="comando">argumento</tool>
    # Suporta multiline e atributos
    pattern = r'<tool code="([^"]+)">\s*(.*?)\s*</tool>'
    matches = re.finditer(pattern, llm_response, re.DOTALL)
    
    found_tools = False
    for match in matches:
        found_tools = True
        tool_code = match.group(1).strip()
        tool_arg = match.group(2).strip()
        
        print(f"[ToolParser] Executando ferramenta: {tool_code}")
        
        log_header = f"--- Resultado de '{tool_code}' ---\n"
        log_content = ""

        try:
            if tool_code == "run_shell":
                res = tool_box.run_shell(tool_arg)
                log_content = f"STDOUT:\n{res.get('stdout', '')}\nSTDERR:\n{res.get('stderr', '')}\nReturn Code: {res.get('returncode', 'N/A')}\n"
                print(f"[ToolParser] Shell command executed with return code: {res.get('returncode')}")

            elif tool_code == "write_file":
                parts = tool_arg.split('\n', 1)
                if len(parts) >= 2:
                    filename = parts[0].strip()
                    content = parts[1]
                    res = tool_box.write_file(filename, content)
                    log_content = f"{res.get('message', 'Nenhuma mensagem de retorno.')}\n"
                    print(f"[ToolParser] File write operation: {res.get('message')}")
                else:
                    log_content = "Erro: 'write_file' requer um nome de arquivo na primeira linha e o conteúdo nas linhas seguintes.\n"
                    print(f"[ToolParser] 'write_file' failed due to incorrect format.")

            elif tool_code == "read_file":
                res = tool_box.read_file(tool_arg)
                if res.get('success'):
                    log_content = f"Conteúdo de '{tool_arg}':\n{res.get('content', '')}\n"
                else:
                    log_content = f"Erro ao ler '{tool_arg}': {res.get('message', 'Erro desconhecido.')}\n"
                print(f"[ToolParser] File read operation for '{tool_arg}' success: {res.get('success')}")

            elif tool_code == "fetch_url":
                res = tool_box.fetch_url(tool_arg)
                if res.get('success'):
                    log_content = f"Conteúdo da URL '{tool_arg}':\n{res.get('content', '')}\n"
                else:
                    log_content = f"Erro ao baixar URL '{tool_arg}': {res.get('message', 'Erro desconhecido.')}\n"
                print(f"[ToolParser] Fetch URL operation for '{tool_arg}' success: {res.get('success')}")
            
            else:
                log_content = f"Erro: Ferramenta '{tool_code}' desconhecida.\n"
                print(f"[ToolParser] Unknown tool '{tool_code}'.")

        except Exception as e:
            log_content = f"Exceção ao executar a ferramenta '{tool_code}': {e}\n"
            print(f"[ToolParser] Exception while running tool '{tool_code}': {e}")

        execution_log += log_header + log_content + "\n"
            
    if not found_tools:
        return None
        
    return execution_log
