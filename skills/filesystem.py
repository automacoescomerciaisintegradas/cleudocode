import os
import logging
from skills.base import BaseSkill

logger = logging.getLogger(__name__)

class FileReadSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Lê o conteúdo de um arquivo local. Forneça o caminho absoluto ou relativo."
        )

    def execute(self, params: str) -> str:
        filepath = params.strip()
        if not os.path.exists(filepath):
            return f"Erro: Arquivo '{filepath}' não encontrado."
            
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return f"--- Conteúdo de '{filepath}' ---\n{content}\n--- Fim do Arquivo ---"
        except Exception as e:
            return f"Erro ao ler arquivo: {e}"

class FileWriteSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Escreve conteúdo em um arquivo. A primeira linha DEVE ser o caminho do arquivo, o restante é o conteúdo."
        )

    def execute(self, params: str) -> str:
        parts = params.split('\n', 1)
        if len(parts) < 2:
            return "Erro de Formato: 'write_file' requer o caminho na primeira linha e o conteúdo nas linhas seguintes."
            
        filepath = parts[0].strip()
        content = parts[1]
        
        try:
            # Cria diretórios se não existirem
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"File created: {filepath}")
            return f"Sucesso: Arquivo '{filepath}' gravado com {len(content)} caracteres."
        except Exception as e:
            return f"Erro ao gravar arquivo: {e}"
