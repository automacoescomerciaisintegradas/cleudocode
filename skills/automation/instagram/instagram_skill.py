"""
Instagram Skill para Cleudocode
===============================

Integração com Instagram Graph API.
Suporta fluxo OAuth2 e publicação de mídia.

Autor: Cleudocode Team
Data: 13/02/2026
"""

import os
import requests
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Ajuste de sys.path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.base import BaseSkill

logger = logging.getLogger(__name__)

class InstagramSkill(BaseSkill):
    """
    Skill para interação com Instagram Graph API.
    """
    
    def __init__(self):
        super().__init__(
            name="instagram",
            description="Integração com Instagram Graph API para publicação de mídia e gestão de perfil."
        )
        self.client_id = os.getenv("INSTAGRAM_CLIENT_ID", "")
        self.client_secret = os.getenv("INSTAGRAM_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("INSTAGRAM_REDIRECT_URI", "")
        self.oauth_server = f"http://localhost:{os.getenv('CLEUDOCODE_OAUTH_PORT', '18903')}"
        self.gateway_token = os.getenv("CLEUDOCODE_GATEWAY_TOKEN", "")
        self._access_token = None

    @property
    def access_token(self):
        """Busca o token do servidor OAuth se não houver um em memória."""
        if not self._access_token:
            self._access_token = self._fetch_token_from_server()
        return self._access_token

    def _fetch_token_from_server(self) -> Optional[str]:
        """Recupera o token do backend Node.js."""
        try:
            url = f"{self.oauth_server}/api/tokens/instagram"
            headers = {"Authorization": f"Bearer {self.gateway_token}"}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Token Instagram recuperado do servidor OAuth.")
                return data.get("access_token")
            else:
                logger.warning(f"⚠️ Servidor OAuth retornou status {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao servidor OAuth: {e}")
        return None

    def execute(self, params: str) -> str:
        # ... (mantém o resto igual mas usa self.access_token)
        parsed = self._parse_params(params)
        action = parsed.get('action', 'get_me')

        try:
            if action == 'get_auth_url':
                return self._get_auth_url()
            elif action == 'exchange_code':
                return self._exchange_code(parsed.get('code', ''))
            elif action == 'publish_photo':
                return self._publish_photo(parsed)
            elif action == 'get_me':
                return self._get_me()
            elif action == 'refresh_token':
                self._access_token = self._fetch_token_from_server()
                return "✅ Token atualizado via servidor OAuth."
            else:
                return f"Ação desconhecida: {action}."
        except Exception as e:
            logger.exception(f"Erro no InstagramSkill: {e}")
            return f"❌ Erro: {str(e)}"

    def _parse_params(self, params: str) -> Dict[str, str]:
        import re
        result = {}
        pattern = r'(\w+):(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))'
        matches = re.findall(pattern, params)
        for key, quoted_double, quoted_single, simple_val in matches:
            result[key] = quoted_double or quoted_single or simple_val
        return result

    def _get_auth_url(self) -> str:
        url = (
            f"https://api.instagram.com/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=user_profile,user_media"
            f"&response_type=code"
        )
        return f"🔗 URL de Autorização Instagram:\n{url}"

    def _exchange_code(self, code: str) -> str:
        if not code:
            return "❌ Código (code) não fornecido."
            
        url = "https://api.instagram.com/oauth/access_token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            data = response.json()
            # Em produção, guardar o access_token e user_id
            return f"✅ Token obtido com sucesso! User ID: {data.get('user_id')}\nToken: {data.get('access_token')[:10]}..."
        else:
            return f"❌ Erro na troca de código ({response.status_code}): {response.text}"

    def _get_me(self) -> str:
        if not self.access_token:
            return "❌ Access Token não configurado. Use action:get_auth_url primeiro."
            
        url = f"https://graph.instagram.com/me?fields=id,username&access_token={self.access_token}"
        response = requests.get(url)
        if response.status_code == 200:
            return f"👤 Perfil Instagram: {response.json().get('username')}"
        else:
            return f"❌ Erro ao obter perfil ({response.status_code}): {response.text}"

    def _publish_photo(self, params: Dict[str, str]) -> str:
        """Simula a publicação (exige API de Business ou Facebook Graph)"""
        image_url = params.get("image_url", "")
        caption = params.get("caption", "Nova oferta!")
        
        return f"📸 [SIMULAÇÃO] Publicando no Instagram:\n- Imagem: {image_url}\n- Legenda: {caption}"

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "instagram_auth",
                "description": "Inicia fluxo de autenticação do Instagram",
                "parameters": {}
            },
            {
                "name": "instagram_publish",
                "description": "Publica imagem no Instagram",
                "parameters": {
                    "image_url": {"type": "string", "description": "URL pública da imagem", "required": True},
                    "caption": {"type": "string", "description": "Legenda do post"}
                }
            }
        ]

if __name__ == "__main__":
    skill = InstagramSkill()
    print(skill.execute('action:get_auth_url'))
