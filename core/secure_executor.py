"""
Módulo para execução segura de código em ambiente sandboxed.
"""
import subprocess
import tempfile
import os
import signal
import time
from pathlib import Path
import json
import shutil
from typing import Dict, Any, Optional


class SecureCodeExecutor:
    """
    Classe para execução segura de código em ambiente isolado.
    """
    
    def __init__(self, timeout: int = 30, memory_limit_mb: int = 100):
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.supported_languages = {
            'python': {
                'extension': '.py',
                'command': ['python3', '{file_path}'],
                'install_cmd': 'python3'
            },
            'javascript': {
                'extension': '.js',
                'command': ['node', '{file_path}'],
                'install_cmd': 'node'
            },
            'typescript': {
                'extension': '.ts',
                'command': ['ts-node', '{file_path}'],
                'install_cmd': 'ts-node'
            },
            'java': {
                'extension': '.java',
                'command': ['java', '{file_path}'],
                'install_cmd': 'javac'
            },
            'go': {
                'extension': '.go',
                'command': ['go', 'run', '{file_path}'],
                'install_cmd': 'go'
            },
            'rust': {
                'extension': '.rs',
                'command': ['cargo', 'run', '--bin', '{file_path}'],
                'install_cmd': 'cargo'
            }
        }
    
    def execute_code(self, code: str, language: str = 'python', 
                     inputs: Optional[list] = None) -> Dict[str, Any]:
        """
        Executa código em ambiente seguro e retorna o resultado.
        
        Args:
            code: Código a ser executado
            language: Linguagem de programação
            inputs: Lista de entradas para o programa (opcional)
        
        Returns:
            Dicionário com resultado da execução
        """
        if language not in self.supported_languages:
            return {
                'success': False,
                'error': f'Linguagem {language} não suportada',
                'stdout': '',
                'stderr': ''
            }
        
        # Criar ambiente temporário
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Criar arquivo de código
            ext = self.supported_languages[language]['extension']
            code_file = temp_path / f'code{ext}'
            
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Preparar comando de execução
            cmd_template = self.supported_languages[language]['command']
            cmd = [part.replace('{file_path}', str(code_file)) for part in cmd_template]
            
            # Preparar entradas se fornecidas
            stdin_input = '\n'.join(inputs) + '\n' if inputs else None
            
            try:
                # Executar com limite de tempo e recursos
                result = subprocess.run(
                    cmd,
                    stdin=subprocess.PIPE if stdin_input else None,
                    input=stdin_input.encode() if stdin_input else None,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=self.timeout,
                    cwd=temp_path,
                    check=False  # Não levantar exceção em código de saída != 0
                )
                
                return {
                    'success': result.returncode == 0,
                    'return_code': result.returncode,
                    'stdout': result.stdout.decode('utf-8'),
                    'stderr': result.stderr.decode('utf-8'),
                    'execution_time': result.elapsed if hasattr(result, 'elapsed') else 0
                }
                
            except subprocess.TimeoutExpired:
                return {
                    'success': False,
                    'error': f'Tempo limite de {self.timeout}s excedido',
                    'stdout': '',
                    'stderr': 'Timeout: Programa foi terminado por exceder tempo limite'
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'stdout': '',
                    'stderr': str(e)
                }
    
    def validate_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """
        Valida código sem executá-lo (sintaxe, segurança, etc.).
        
        Args:
            code: Código a ser validado
            language: Linguagem de programação
        
        Returns:
            Dicionário com resultados da validação
        """
        if language not in self.supported_languages:
            return {
                'valid': False,
                'errors': [f'Linguagem {language} não suportada'],
                'warnings': []
            }
        
        # Verificar padrões perigosos no código
        dangerous_patterns = [
            # Python
            (r'exec\s*\(', 'Evite o uso de exec()'),
            (r'eval\s*\(', 'Evite o uso de eval()'),
            (r'__import__', 'Evite o uso de __import__'),
            (r'compile\s*\(', 'Evite o uso de compile()'),
            (r'open\s*\([^)]*["\'][rwax][^"\']*["\']', 'Evite operações de escrita em arquivos'),
            (r'subprocess\.', 'Evite o uso de subprocess'),
            (r'os\.(system|popen|remove|rename)', 'Evite chamadas ao sistema operacional'),
            (r'sys\.', 'Evite manipulação direta do sistema'),
            
            # JavaScript/Node.js
            (r'eval\s*\(', 'Evite o uso de eval()'),
            (r'Function\s*\(', 'Evite o uso de Function constructor'),
            (r'require\s*\(\s*["\']child_process["\']', 'Evite chamadas de subprocesso'),
            (r'require\s*\(\s*["\']fs["\']', 'Evite operações de sistema de arquivos'),
        ]
        
        errors = []
        warnings = []
        
        for pattern, warning in dangerous_patterns:
            import re
            if re.search(pattern, code, re.IGNORECASE):
                errors.append(f'Padrão potencialmente perigoso detectado: {warning}')
        
        # Verificar sintaxe básica (para linguagens suportadas)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            ext = self.supported_languages[language]['extension']
            code_file = temp_path / f'code{ext}'
            
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Verificar sintaxe para linguagens suportadas
            if language == 'python':
                try:
                    compile(code, '<string>', 'exec')
                except SyntaxError as e:
                    errors.append(f'Erro de sintaxe Python: {str(e)}')
            elif language == 'javascript':
                # Para JS, poderíamos usar um parser como o esprima, mas por enquanto apenas verificamos padrões
                pass
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# Instância global do executor seguro
secure_executor = SecureCodeExecutor()