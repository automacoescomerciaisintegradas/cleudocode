"""
skills/send_campaign.py — Skill para enviar campanhas via WhatsApp, integrando com campanha_massa_whatsapp.py.

Esta skill é carregada dinamicamente pelo skill_loader.py e pode ser usada por agentes (ex: NotifierAgent).

Autor: Cleudo Code Team
Data: 31/01/2026
"""

import subprocess
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from skill_loader import skill  # ✅ Importação explícita do decorator

# Caminho do script existente
CAMPAIGN_SCRIPT = Path(__file__).parent.parent / "campanha_massa_whatsapp.py"
if not CAMPAIGN_SCRIPT.exists():
    raise FileNotFoundError(f"Script de campanha não encontrado: {CAMPAIGN_SCRIPT}")

def validate_phone(phone: str) -> bool:
    """Valida formato de número de telefone (ex: +5511999999999)."""
    return bool(re.match(r'^\+\d{10,15}$', phone))

def validate_contacts(contatos: List[str]) -> bool:
    """Valida lista de contatos."""
    return all(isinstance(c, str) and validate_phone(c) for c in contatos)

@skill
def send_campaign_message(
    mensagem: str,
    contatos: List[str],
    delay_seconds: float = 0.5
) -> Dict[str, Any]:
    """
    Envia uma mensagem de campanha para uma lista de contatos via WhatsApp.
    
    Args:
        mensagem (str): Texto da mensagem (máx. 1000 caracteres)
        contatos (List[str]): Lista de números no formato +5511999999999
        delay_seconds (float): Atraso entre mensagens (padrão: 0.5s)
    
    Returns:
        Dict com status, total_enviados, erros, etc.
    """
    # Validação de entrada
    if not isinstance(mensagem, str) or len(mensagem) > 1000:
        return {"status": "error", "message": "Mensagem muito longa (máx. 1000 caracteres)"}
    
    if not isinstance(contatos, list):
        return {"status": "error", "message": "Contatos deve ser uma lista"}
    
    if not validate_contacts(contatos):
        return {"status": "error", "message": "Formato inválido de número de telefone. Use +5511999999999"}
    
    # Prepara argumentos para o script existente
    # Supondo que seu campanha_massa_whatsapp.py aceite:
    #   --mensagens "texto" --contatos "+5511..." "+5522..."
    args = [
        "python",
        str(CAMPAIGN_SCRIPT),
        "--mensagem", mensagem,
        "--contatos"
    ] + contatos
    
    if delay_seconds > 0:
        args.extend(["--delay", str(delay_seconds)])
    
    try:
        # Executa o script existente (sandbox seguro: só dentro do projeto)
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos máximo
            cwd=Path(__file__).parent.parent  # executa no root do projeto
        )
        
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if result.returncode == 0:
            return {
                "status": "success",
                "total_enviados": len(contatos),
                "mensagem": mensagem[:50] + ("..." if len(mensagem) > 50 else ""),
                "output": stdout[:200],
                "timestamp": result.stdout.splitlines()[-1] if stdout else None
            }
        else:
            return {
                "status": "error",
                "returncode": result.returncode,
                "stderr": stderr[:500],
                "stdout": stdout[:500]
            }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Tempo limite excedido (300s)"}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao executar campanha: {type(e).__name__}: {e}"}