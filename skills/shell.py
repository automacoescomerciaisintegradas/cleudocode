import subprocess
import logging
from skills.base import BaseSkill

logger = logging.getLogger(__name__)

class ShellSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="run_shell",
            description="Executa comandos no terminal do sistema operacional (Windows/Linux). Use com cuidado."
        )

    def execute(self, params: str) -> str:
        command = params.strip()
        logger.info(f"Executing Shell Command: {command}")
        
        try:
            # Timeout de segurança
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            output = f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"Return Code: {result.returncode}"
            
            return output
        except subprocess.TimeoutExpired:
            return "Erro: Comando excedeu o tempo limite de 60s."
        except Exception as e:
            return f"Erro na execução: {str(e)}"
