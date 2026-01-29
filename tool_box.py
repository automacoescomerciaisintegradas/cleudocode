import os
import subprocess
import json

def run_shell(command):
    """Executa um comando no shell e retorna (stdout, stderr, returncode)"""
    try:
        # Pagar cat não é necessário aqui, rodaremos direto
        # shell=True permite comandos compostos, mas exige cuidado. 
        # Como é um ambiente dev local, é aceitável.
        process = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='replace' # Evita crash com unicode
        )
        return {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "returncode": process.returncode
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Erro Python ao executar: {str(e)}",
            "returncode": -1
        }

def write_file(filepath, content):
    """Escreve conteúdo em um arquivo"""
    try:
        # Cria diretórios se não existirem
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"Arquivo {filepath} salvo."}
    except Exception as e:
        return {"success": False, "message": f"Erro ao salvar: {str(e)}"}

def read_file(filepath):
    """Lê conteúdo de um arquivo"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return {"success": True, "content": f.read()}
        return {"success": False, "message": "Arquivo não encontrado."}
    except Exception as e:
        return {"success": False, "message": f"Erro ao ler: {str(e)}"}

import requests
from bs4 import BeautifulSoup

def fetch_url(url):
    """(NOVA) Baixa e limpa o conteúdo de texto de uma URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts e estilos
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        text = soup.get_text()
        
        # Limpa linhas em branco
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return {"success": True, "content": clean_text[:10000]} # Limita a 10k caracteres para não estourar o prompt
    except Exception as e:
        return {"success": False, "message": f"Erro ao acessar {url}: {str(e)}"}

def list_dir(path="."):
    """Lista arquivos no diretório"""
    try:
        files = os.listdir(path)
        return {"success": True, "files": files}
    except Exception as e:
        return {"success": False, "message": str(e)}
