import os
import json
import importlib.util
import multiprocessing
import traceback
from pathlib import Path
from typing import Dict, List, Optional

class PluginContext:
    """Objeto seguro fornecido aos plugins para interagir com o sistema."""
    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        self.results = {}

    def log(self, message: str):
        print(f"[{self.plugin_name}] {message}")

    def set_result(self, key: str, value: any):
        self.results[key] = value

    def get_env(self, key: str, default: str = None):
        """Acessa variáveis de ambiente de forma segura."""
        # Podemos filtrar quais chaves o plugin pode ver se quisermos mais segurança
        import os
        return os.getenv(key, default)

    def read_file_safe(self, path: str) -> str:
        """Lê um arquivo do projeto, garantindo que não saia da raiz."""
        safe_path = Path(path).resolve()
        root_path = Path(os.getcwd()).resolve()
        
        if not str(safe_path).startswith(str(root_path)):
            raise PermissionError(f"Acesso negado ao arquivo fora do projeto: {path}")
            
        if not safe_path.exists():
            return ""
            
        return safe_path.read_text(encoding='utf-8', errors='ignore')

def _sandbox_worker(plugin_path, pipe, args):
    """Função executada em um processo isolado."""
    try:
        # 1. Carregar manifest
        manifest_path = Path(plugin_path) / "manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        # 2. Carregar código do plugin
        spec = importlib.util.spec_from_file_location("plugin_entry", Path(plugin_path) / "main.py")
        module = importlib.util.module_from_spec(spec)
        
        # 3. Criar contexto
        ctx = PluginContext(manifest.get("name", "Unknown"))
        
        # 4. Executar
        spec.loader.exec_module(module)
        if hasattr(module, 'run'):
            module.run(ctx, **args)
        
        # 5. Retornar resultados via pipe
        pipe.send({"status": "success", "results": ctx.results})
    except Exception as e:
        pipe.send({"status": "error", "message": str(e), "trace": traceback.format_exc()})
    finally:
        pipe.close()

class PluginManager:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir()

    def list_plugins(self) -> List[Dict]:
        plugins = []
        for d in self.plugins_dir.iterdir():
            if d.is_dir():
                manifest_path = d / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                            manifest["id"] = d.name
                            plugins.append(manifest)
                    except Exception:
                        pass
        return plugins

    def run_plugin(self, plugin_id: str, timeout: int = 30, **args) -> Dict:
        plugin_path = self.plugins_dir / plugin_id
        if not plugin_path.exists():
            return {"status": "error", "message": f"Plugin {plugin_id} não encontrado."}

        # Usar multiprocessing para isolamento de processo
        parent_conn, child_conn = multiprocessing.Pipe()
        process = multiprocessing.Process(target=_sandbox_worker, args=(str(plugin_path), child_conn, args))
        
        process.start()
        
        try:
            if parent_conn.poll(timeout):
                result = parent_conn.recv()
            else:
                process.terminate()
                result = {"status": "error", "message": f"Timeout após {timeout}s"}
        except EOFError:
            result = {"status": "error", "message": "Processo do plugin encerrou inesperadamente."}
        finally:
            process.join(timeout=1)
            if process.is_alive():
                process.kill()

        return result

# Singleton
plugin_manager = PluginManager()
