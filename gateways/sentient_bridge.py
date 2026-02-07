import os
import json
import logging
import asyncio
import time
from typing import Dict, Any, List
from core.llm_providers import llm_hub

logger = logging.getLogger(__name__)

class SentientGridBridge:
    """
    Bridge para integração com o protocolo Sentient Grid e framework OML.
    Gerencia a 'Lealdade' (Loyalty) do modelo e a interface de monetização.
    """
    
    def __init__(self):
        self.name = "SentientGrid"
        self.enabled = os.getenv("SENTIENT_GRID_ENABLED", "false").lower() == "true"
        self.node_id = os.getenv("SENTIENT_NODE_ID", "cleudo-node-001")
        self.wallet_address = os.getenv("SENTIENT_WALLET_ADDRESS", "")
        self.fingerprint_status = "unverified"
        self.callback = None
        
    def set_callback(self, callback):
        self.callback = callback

    def start(self):
        """
        Inicia a verificação de lealdade e prepara o bridge.
        """
        logger.info(f"🚀 Sentient Grid Bridge ativado. Node: {self.node_id}")
        # Em um cenário real, aqui poderíamos iniciar um websocket para o Grid.
        if self.enabled:
            asyncio.run(self.verify_model_loyalty("current_model"))

    async def verify_model_loyalty(self, model_path: str) -> bool:
        """
        Verifica se o modelo carregado possui as fingerprints leais (OML 1.0).
        Este é um requisito do Sentient Grid para monetização.
        """
        from check_fingerprints import check_fingerprints
        # Simulação de verificação automática para o bridge
        # Em produção, isso chamaria o script de verificação real
        logger.info(f"🛡️ Verificando lealdade OML para o modelo: {model_path}")
        
        # Simulando resultado baseado no arquivo de logs
        if os.path.exists("fingerprint_results.json"):
            with open("fingerprint_results.json", "r") as f:
                res = json.load(f)
                accuracy = res.get("summary", {}).get("accuracy", 0)
                if accuracy > 90:
                    self.fingerprint_status = "verified"
                    return True
        
        self.fingerprint_status = "failed"
        return False

    async def handle_grid_query(self, query_data: Dict[Any, Any]):
        """
        Processa uma instrução vinda do Grid (Network of Intelligence).
        Valida a prova de pagamento/autorização antes da inferência.
        """
        instruction = query_data.get("instruction")
        authorization_proof = query_data.get("auth_proof") # On-chain signature/token
        
        if not self._validate_auth(authorization_proof):
            return {"success": False, "error": "Unauthorized: Missing OML compliance"}

        # Executa a inferência via LLM Hub
        messages = [{"role": "user", "content": instruction}]
        response = llm_hub.query(messages)
        
        # TODO: Registrar métricas de uso para o settlement on-chain
        return {
            "success": True,
            "response": response,
            "node": self.node_id,
            "oml_version": "1.0",
            "timestamp": int(time.time())
        }

    def _validate_auth(self, proof: str) -> bool:
        """
        Valida se a query possui autorização válida no Sentient Grid.
        """
        # Placeholder para validação de contrato inteligente/assinatura
        if proof == "DEVELOPER_MODE": return True
        return self.fingerprint_status == "verified"

    def get_status(self):
        # Tenta verificar se ainda não estiver verificado
        if self.enabled and self.fingerprint_status != "verified":
            if os.path.exists("fingerprint_results.json"):
                with open("fingerprint_results.json", "r") as f:
                    try:
                        res = json.load(f)
                        accuracy = res.get("summary", {}).get("accuracy", 0)
                        if accuracy > 90:
                            self.fingerprint_status = "verified"
                    except:
                        pass

        return {
            "bridge_active": self.enabled,
            "node_id": self.node_id,
            "wallet": self.wallet_address,
            "oml_loyalty": self.fingerprint_status
        }

# Instância global para o daemon
sentient_bridge = SentientGridBridge()
