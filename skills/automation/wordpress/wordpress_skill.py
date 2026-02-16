"""
WordPress Skill para Cleudocode
===============================

Integração com WordPress REST API usando Application Passwords.
Suporta publicação de posts, upload de mídia e gestão de conteúdo.

Autor: Cleudocode Team
Data: 13/02/2026
"""

import os
import json
import base64
import requests
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Ajuste de sys.path para importar BaseSkill
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.base import BaseSkill

logger = logging.getLogger(__name__)

class WordPressSkill(BaseSkill):
    """
    Skill para interação com WordPress via REST API.
    """
    
    def __init__(self):
        super().__init__(
            name="wordpress",
            description="Integração profunda com WordPress REST API para gestão de conteúdo, mídia e automação de afiliados."
        )
        self.wp_url = os.getenv("WP_URL", "").rstrip("/")
        self.username = os.getenv("WP_USERNAME", "")
        self.app_password = os.getenv("WP_APPLICATION_PASSWORD", "")
        self.client_id = os.getenv("WP_CLIENT_ID", "")
        self.client_secret = os.getenv("WP_CLIENT_SECRET", "")
        self._token = None
        
    def _get_auth_header(self) -> Dict[str, str]:
        """Gera o header de autenticação (OAuth2 Token ou Basic Auth)."""
        # Priorizar OAuth2 se as credenciais estiverem no .env
        if self.client_id and self.client_secret:
            if not self._token:
                self._token = self._fetch_oauth_token()
            if self._token:
                return {"Authorization": f"Bearer {self._token}"}
                
        # Fallback para Basic Auth
        auth_str = f"{self.username}:{self.app_password}"
        encoded_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        return {
            "Authorization": f"Basic {encoded_auth}"
        }

    def _fetch_oauth_token(self) -> Optional[str]:
        """Busca token via OAuth2 Client Credentials."""
        try:
            token_url = f"{self.wp_url}/wp-json/oauth2/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            response = requests.post(token_url, data=data, timeout=10)
            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                logger.error(f"Erro OAuth2: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exceção ao obter token OAuth2: {e}")
            return None

    def execute(self, params: str) -> str:
        """
        Executa ações do WordPress.
        
        Ações:
        - create_post: Cria um novo post
        - upload_media: Faz upload de imagem/vídeo
        - list_posts: Lista posts recentes
        - delete_post: Remove um post
        """
        parsed = self._parse_params(params)
        action = parsed.get('action', 'list_posts')
        
        if not self.wp_url:
            return "❌ Erro: WP_URL deve estar no .env"
        
        if not (self.app_password or (self.client_id and self.client_secret)):
            return "❌ Erro: Credenciais do WordPress ausentes (Senha de Aplicativo ou OAuth2)."

        try:
            if action == 'create_post':
                return self._create_post(parsed)
            elif action == 'upload_media':
                return self._upload_media(parsed)
            elif action == 'list_posts':
                return self._list_posts(parsed)
            elif action == 'delete_post':
                return self._delete_post(parsed.get('id', ''))
            else:
                return f"Ação desconhecida: {action}. Use: create_post, upload_media, list_posts, delete_post"
        except Exception as e:
            logger.exception(f"Erro no WordPressSkill: {e}")
            return f"❌ Erro: {str(e)}"

    def _parse_params(self, params: str) -> Dict[str, str]:
        """Parse básico de parâmetros key:value."""
        import re
        result = {}
        pattern = r'(\w+):(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))'
        matches = re.findall(pattern, params)
        for key, quoted_double, quoted_single, simple_val in matches:
            result[key] = quoted_double or quoted_single or simple_val
        return result

    def _create_post(self, params: Dict[str, str]) -> str:
        """Cria um post no WordPress."""
        url = f"{self.wp_url}/wp-json/wp/v2/posts"
        
        payload = {
            "title": params.get("title", "Novo Post Cleudocode"),
            "content": params.get("content", ""),
            "status": params.get("status", "draft"),
            "categories": [int(c) for c in params.get("categories", "1").split(",") if c.isdigit()],
            "format": params.get("format", "standard")
        }
        
        if "featured_media" in params:
            payload["featured_media"] = int(params["featured_media"])

        response = requests.post(url, json=payload, headers=self._get_auth_header())
        
        if response.status_code in [200, 201]:
            post_data = response.json()
            return f"✅ Post criado com sucesso! ID: {post_data['id']} - Link: {post_data['link']}"
        else:
            return f"❌ Erro ao criar post ({response.status_code}): {response.text}"

    def _upload_media(self, params: Dict[str, str]) -> str:
        """Faz upload de mídia."""
        file_path = params.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            return f"❌ Arquivo não encontrado: {file_path}"
            
        url = f"{self.wp_url}/wp-json/wp/v2/media"
        filename = os.path.basename(file_path)
        
        headers = self._get_auth_header()
        headers["Content-Disposition"] = f"attachment; filename={filename}"
        # Tentar detectar content-type
        import mimetypes
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type:
            headers["Content-Type"] = content_type

        with open(file_path, "rb") as f:
            response = requests.post(url, data=f, headers=headers)

        if response.status_code in [200, 201]:
            media_data = response.json()
            return f"✅ Mídia enviada! ID: {media_data['id']} - URL: {media_data['source_url']}"
        else:
            return f"❌ Erro no upload ({response.status_code}): {response.text}"

    def _list_posts(self, params: Dict[str, str]) -> str:
        """Lista posts recentes."""
        per_page = int(params.get("per_page", "5"))
        url = f"{self.wp_url}/wp-json/wp/v2/posts?per_page={per_page}"
        
        response = requests.get(url, headers=self._get_auth_header())
        
        if response.status_code == 200:
            posts = response.json()
            if not posts:
                return "📭 Nenhum post encontrado."
            
            lines = [f"📋 Últimos {len(posts)} posts no WordPress:\n"]
            for p in posts:
                lines.append(f"- [{p['id']}] {p['title']['rendered']} ({p['status']})")
                lines.append(f"  Link: {p['link']}\n")
            return "\n".join(lines)
        else:
            return f"❌ Erro ao listar posts ({response.status_code}): {response.text}"

    def _delete_post(self, post_id: str) -> str:
        """Deleta um post."""
        if not post_id:
            return "❌ ID do post é obrigatório."
            
        url = f"{self.wp_url}/wp-json/wp/v2/posts/{post_id}"
        response = requests.delete(url, headers=self._get_auth_header())
        
        if response.status_code == 200:
            return f"🗑️ Post {post_id} movido para a lixeira."
        else:
            return f"❌ Erro ao deletar post ({response.status_code}): {response.text}"

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "wp_create_post",
                "description": "Cria um novo post no WordPress",
                "parameters": {
                    "title": {"type": "string", "description": "Título do post", "required": True},
                    "content": {"type": "string", "description": "Conteúdo HTML ou texto", "required": True},
                    "status": {"type": "string", "description": "Status: publish, draft, pending", "default": "draft"},
                    "featured_media": {"type": "integer", "description": "ID da imagem de destaque"}
                }
            },
            {
                "name": "wp_upload_media",
                "description": "Faz upload de um arquivo para a biblioteca do WordPress",
                "parameters": {
                    "file_path": {"type": "string", "description": "Caminho local do arquivo", "required": True}
                }
            }
        ]

if __name__ == "__main__":
    # Teste rápido se rodar diretamente
    skill = WordPressSkill()
    print(skill.get_definition())
