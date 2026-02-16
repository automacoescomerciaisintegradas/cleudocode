"""
WhatsApp Skill para Cleudocode (Evolution API v2)
================================================

Integração com Evolution API para envio de mensagens, imagens e gestão de grupos.
Suporta o envio automático de ofertas com fotos e links.

Autor: Cleudocode Team
Data: 13/02/2026
"""

import os
import requests
import logging
import base64
from typing import Dict, Any, List, Optional
from pathlib import Path

# Ajuste de sys.path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.base import BaseSkill

logger = logging.getLogger(__name__)

class WhatsAppSkill(BaseSkill):
    """
    Skill para interação com Evolution API (WhatsApp).
    """
    
    def __init__(self):
        super().__init__(
            name="whatsapp",
            description="Integração com Evolution API para envio de mensagens e mídia no WhatsApp."
        )
        self.api_url = os.getenv("WHATSAPP_BASE_URL", "").rstrip("/")
        self.instance = os.getenv("WHATSAPP_INSTANCE_NAME", "cleudocode")
        self.api_key = os.getenv("WHATSAPP_API_TOKEN_INSTANCE", "")
        self.target_chat = os.getenv("WHATSAPP_TARGET_NUMBER", "") # Sugestão de nova env
        
    def _get_headers(self) -> Dict[str, str]:
        return {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    def execute(self, params: str) -> str:
        parsed = self._parse_params(params)
        action = parsed.get('action', 'send_message')

        if not self.api_url or not self.api_key:
            return "❌ Erro: WHATSAPP_API_URL e WHATSAPP_API_KEY devem estar no .env"

        try:
            if action == 'send_message':
                return self._send_message(parsed)
            elif action == 'send_media':
                return self._send_media(parsed)
            elif action == 'check_status':
                return self._check_status()
            else:
                return f"Ação desconhecida: {action}."
        except Exception as e:
            logger.exception(f"Erro no WhatsAppSkill: {e}")
            return f"❌ Erro: {str(e)}"

    def _parse_params(self, params: str) -> Dict[str, str]:
        import re
        result = {}
        pattern = r'(\w+):(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))'
        matches = re.findall(pattern, params)
        for key, quoted_double, quoted_single, simple_val in matches:
            result[key] = quoted_double or quoted_single or simple_val
        return result

    def _check_status(self) -> str:
        url = f"{self.api_url}/instance/connectionState/{self.instance}"
        response = requests.get(url, headers=self._get_headers())
        if response.status_code == 200:
            state = response.json().get("instance", {}).get("state", "unknown")
            return f"📱 Status WhatsApp ({self.instance}): {state}"
        return f"❌ Erro ao verificar status: {response.text}"

    def _send_message(self, params: Dict[str, str]) -> str:
        number = params.get("number", self.target_chat)
        text = params.get("text", "")
        
        if not number or not text:
            return "❌ Número e texto são obrigatórios."

        url = f"{self.api_url}/message/sendText/{self.instance}"
        payload = {
            "number": number,
            "text": text,
            "linkPreview": True
        }
        
        response = requests.post(url, json=payload, headers=self._get_headers())
        if response.status_code in [200, 201]:
            return f"✅ Mensagem enviada para {number}."
        return f"❌ Erro ao enviar mensagem: {response.text}"

    def _send_media(self, params: Dict[str, str]) -> str:
        """Envia imagem ou vídeo com legenda (Evolution v2)"""
        number = params.get("number", self.target_chat)
        media_url = params.get("media_url", "")
        caption = params.get("caption", "")
        media_type = params.get("media_type", "image") 
        file_path = params.get("file_path", "")
        
        if not number or (not media_url and not file_path):
            return "❌ Número e (URL ou Arquivo) são obrigatórios."

        media_data = media_url
        
        # Se for um arquivo local, converte para base64
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    media_data = f"data:{media_type}/jpeg;base64,{encoded}"
            except Exception as e:
                logger.error(f"Erro ao converter arquivo para base64: {e}")

        url = f"{self.api_url}/message/sendMedia/{self.instance}"
        payload = {
            "number": number,
            "mediatype": media_type,
            "media": media_data,
            "caption": caption
        }
        
        response = requests.post(url, json=payload, headers=self._get_headers())
        
        # Se falhou com URL, tenta um "Proxy Download" interno e manda como base64
        if response.status_code != 200 and media_url and not file_path:
            logger.info("Tentando fallback de download direto para Base64...")
            try:
                res_down = requests.get(media_url, timeout=10)
                if res_down.status_code == 200:
                    encoded = base64.b64encode(res_down.content).decode('utf-8')
                    payload["media"] = f"data:{media_type}/jpeg;base64,{encoded}"
                    response = requests.post(url, json=payload, headers=self._get_headers())
            except: pass

        if response.status_code in [200, 201]:
            return f"✅ Mídia ({media_type}) enviada para {number}."
        return f"❌ Erro ao enviar mídia: {response.text}"

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "whatsapp_send",
                "description": "Envia mensagem ou mídia via WhatsApp Evolution API",
                "parameters": {
                    "number": {"type": "string", "description": "Número (DDI+DDD+Número) ou ID de Grupo"},
                    "text": {"type": "string", "description": "Texto da mensagem"},
                    "media_url": {"type": "string", "description": "URL da imagem ou vídeo"},
                    "caption": {"type": "string", "description": "Legenda da mídia"}
                }
            }
        ]

if __name__ == "__main__":
    skill = WhatsAppSkill()
    print(skill.execute('action:check_status'))
