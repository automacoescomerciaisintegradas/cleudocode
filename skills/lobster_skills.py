"""
Skills adaptadas para o Lobster Workflow Engine.
Retornam dicts com formato {success, ...} em vez de strings.
"""

import os
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class FilesystemSkill:
    """Skill de operações de filesystem."""
    
    name = "filesystem"
    
    def create_directory(self, path: str) -> Dict[str, Any]:
        """Cria um diretório."""
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Diretório criado: {path}")
            return {
                "success": True,
                "path": path,
                "message": f"Diretório '{path}' criado"
            }
        except Exception as e:
            logger.error(f"Erro ao criar diretório: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def write_file(self, filepath: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
        """Escreve conteúdo em arquivo."""
        try:
            file_path = Path(filepath)
            
            # Verificar se arquivo existe
            if file_path.exists() and not overwrite:
                return {
                    "success": False,
                    "error": f"Arquivo '{filepath}' já existe. Use overwrite=true para sobrescrever."
                }
            
            # Criar diretórios se necessário
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escrever arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Arquivo escrito: {filepath}")
            return {
                "success": True,
                "filepath": str(file_path),
                "size": len(content),
                "message": f"Arquivo '{filepath}' escrito com {len(content)} caracteres"
            }
        except Exception as e:
            logger.error(f"Erro ao escrever arquivo: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Lê conteúdo de arquivo."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "filepath": filepath,
                "content": content,
                "size": len(content)
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Arquivo '{filepath}' não encontrado"
            }
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ShellSkill:
    """Skill de execução de comandos shell."""
    
    name = "shell"
    
    def execute(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Executa comando shell."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Comando excedeu timeout de {timeout}s"
            }
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class TelegramSkill:
    """Skill de integração com Telegram."""
    
    name = "telegram"
    
    def send_message(self, message: str, chat_id: str = None) -> Dict[str, Any]:
        """Envia mensagem via Telegram."""
        # Por enquanto, apenas simula o envio
        logger.info(f"[TELEGRAM] Mensagem: {message[:100]}...")
        
        return {
            "success": True,
            "message": "Mensagem enviada (simulado)",
            "chat_id": chat_id or "default"
        }
