import docker
import json
import os
import uuid
import time

# Configurações do Sandbox
SANDBOX_CONTAINER_NAME = "cleudocode-sandbox"
SHARED_VOLUME_HOST_PATH = "sandbox_io" # Este é o nome do volume no docker-compose
SANDBOX_APP_PATH = "/app/sandbox"
TIMEOUT_SECONDS = 120

def get_docker_client():
    """Inicializa e retorna o cliente Docker."""
    try:
        # Tenta conectar usando o socket padrão
        client = docker.from_env()
        # Verifica se a conexão funciona
        client.ping()
        return client
    except Exception as e:
        print(f"[SandboxManager] Erro ao conectar ao Docker: {e}")
        return None

def execute_in_sandbox(tool_code_string: str):
    """
    Executa um bloco de código de ferramenta dentro do contêiner do sandbox.

    Args:
        tool_code_string: A string completa contendo uma ou mais tags <tool>.

    Returns:
        Um dicionário com o log de execução ou uma mensagem de erro.
    """
    client = get_docker_client()
    if not client:
        return {"success": False, "log": "Erro: Cliente Docker não está disponível."}

    task_id = str(uuid.uuid4())
    task_filename = f"task_{task_id}.json"
    result_filename = f"result_{task_id}.json"

    # O caminho no HOST onde o docker-compose cria o volume
    host_task_path = os.path.join(SHARED_VOLUME_HOST_PATH, task_filename)
    host_result_path = os.path.join(SHARED_VOLUME_HOST_PATH, result_filename)
    
    # O caminho que o SCRIPT DENTRO do sandbox vai usar
    sandbox_task_path = os.path.join(SANDBOX_APP_PATH, task_filename)

    # 1. Preparar e escrever o arquivo de tarefa
    task_data = {
        "task_id": task_id,
        "tool_code": tool_code_string
    }
    try:
        # Precisamos de um diretório real no host para escrever o arquivo de tarefa
        # que será montado no container
        if not os.path.exists(SHARED_VOLUME_HOST_PATH):
            os.makedirs(SHARED_VOLUME_HOST_PATH)
            
        with open(host_task_path, 'w', encoding='utf-8') as f:
            json.dump(task_data, f)
            
    except Exception as e:
        return {"success": False, "log": f"Erro ao criar arquivo de tarefa: {e}"}

    # 2. Executar o comando no contêiner do sandbox
    try:
        container = client.containers.get(SANDBOX_CONTAINER_NAME)
        
        # O comando que será executado dentro do sandbox
        command_to_run = f"python /app/sandbox_runner.py {sandbox_task_path}"
        
        print(f"[SandboxManager] Executando no sandbox: {command_to_run}")
        exit_code, (stdout, stderr) = container.exec_run(command_to_run, demux=True)

        if exit_code != 0:
            # Ocorreu um erro na execução do script runner
            error_log = f"Falha ao executar o runner no sandbox (Exit Code: {exit_code}).\n"
            if stdout:
                error_log += f"STDOUT: {stdout.decode('utf-8')}\n"
            if stderr:
                error_log += f"STDERR: {stderr.decode('utf-8')}\n"
            # Limpar arquivo de tarefa
            os.remove(host_task_path)
            return {"success": False, "log": error_log}

    except docker.errors.NotFound:
        os.remove(host_task_path)
        return {"success": False, "log": f"Erro: O contêiner '{SANDBOX_CONTAINER_NAME}' não foi encontrado."}
    except Exception as e:
        os.remove(host_task_path)
        return {"success": False, "log": f"Erro ao executar comando no Docker: {e}"}

    # 3. Aguardar e ler o arquivo de resultado
    start_time = time.time()
    while time.time() - start_time < TIMEOUT_SECONDS:
        if os.path.exists(host_result_path):
            try:
                with open(host_result_path, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                
                # Limpeza
                os.remove(host_task_path)
                os.remove(host_result_path)
                
                return {"success": True, "log": result_data.get("execution_log", "")}
            except Exception as e:
                # Limpeza
                os.remove(host_task_path)
                os.remove(host_result_path)
                return {"success": False, "log": f"Erro ao ler arquivo de resultado: {e}"}
        time.sleep(0.5)

    # Limpeza em caso de timeout
    os.remove(host_task_path)
    return {"success": False, "log": "Erro: Timeout esperando pelo resultado do sandbox."}

if __name__ == '__main__':
    # Exemplo de como usar (para teste)
    print("Testando o Sandbox Manager...")
    
    # Simula um código de ferramenta que o LLM geraria
    test_code = """
    <tool code="run_shell">
    echo "Olá do sandbox!"
    ls -l /app
    </tool>
    <tool code="write_file">
    /app/sandbox/teste.txt
    Este arquivo foi escrito pelo sandbox.
    </tool>
    """
    
    result = execute_in_sandbox(test_code)
    
    print("\n--- Resultado do Teste ---")
    if result["success"]:
        print(result["log"])
    else:
        print(f"FALHA: {result['log']}")
    print("------------------------")
