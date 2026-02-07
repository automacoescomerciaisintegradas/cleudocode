"""
skills/deploy_version.py — Skill para executar deploy de versão, integrando com automated_deploy.py.

Esta skill é carregada dinamicamente pelo skill_loader.py e pode ser usada por agentes (ex: ExecutorAgent).

Autor: Cleudo Code Team
Data: 31/01/2026
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, Any, Optional
from skill_loader import skill  # ✅ Importação explícita do decorator

# Caminhos dos scripts existentes
DEPLOY_SCRIPTS = [
    Path(__file__).parent.parent / "automated_deploy.py",
    Path(__file__).parent.parent / "auto_deploy_brasil.py"
]

# Encontra o primeiro script que existe
DEPLOY_SCRIPT = None
for script in DEPLOY_SCRIPTS:
    if script.exists():
        DEPLOY_SCRIPT = script
        break

if DEPLOY_SCRIPT is None:
    raise FileNotFoundError(
        f"Nenhum script de deploy encontrado em: {[str(s) for s in DEPLOY_SCRIPTS]}"
    )

def validate_version(version: str) -> bool:
    """Valida formato de versão (ex: v2.1, 3.0.0, latest)."""
    return bool(re.match(r'^[vV]?\d+(\.\d+)*$|^latest$', version))

@skill
def deploy_version(
    version: str,
    env: str = "production",
    force: bool = False
) -> Dict[str, Any]:
    """
    Executa deploy de uma versão específica usando seu script existente.
    
    Args:
        version (str): Versão a ser implantada (ex: "v2.1", "latest")
        env (str): Ambiente ("production", "staging", "dev") — padrão: "production"
        force (bool): Força deploy mesmo se já estiver na versão atual
    
    Returns:
        Dict com status, versão, ambiente, output, etc.
    """
    # Validação de entrada
    if not isinstance(version, str) or not validate_version(version):
        return {"status": "error", "message": "Versão inválida. Use formatos como 'v2.1', '3.0.0' ou 'latest'."}
    
    if not isinstance(env, str) or env not in ["production", "staging", "dev"]:
        return {"status": "error", "message": "Ambiente inválido. Use: production, staging, dev."}
    
    # Prepara argumentos para o script existente
    args = [
        "python",
        str(DEPLOY_SCRIPT),
        "--version", version,
        "--env", env
    ]
    if force:
        args.append("--force")

    try:
        # Executa o script existente (sandbox seguro: só dentro do projeto)
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutos máximo para deploy
            cwd=Path(__file__).parent.parent  # executa no root do projeto
        )
        
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode == 0:
            return {
                "status": "success",
                "version": version,
                "env": env,
                "force": force,
                "output": stdout[:300],
                "timestamp": stdout.splitlines()[-1] if stdout else None
            }
        else:
            return {
                "status": "error",
                "returncode": result.returncode,
                "stderr": stderr[:500],
                "stdout": stdout[:500],
                "message": "Deploy falhou"
            }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Tempo limite excedido (600s) durante deploy"}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao executar deploy: {type(e).__name__}: {e}"}