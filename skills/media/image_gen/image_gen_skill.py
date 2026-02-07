"""
Image Generation Skill para Cleudocode
======================================

Gera imagens usando APIs de IA (DALL-E, Replicate, Stability AI).

Autor: Cleudocode Team
Data: 02/02/2026
"""

import os
import json
import base64
import uuid
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import logging

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.base import BaseSkill

logger = logging.getLogger(__name__)


class ImageGenSkill(BaseSkill):
    """
    Skill para geração de imagens com IA.
    
    Provedores suportados:
    - OpenAI (DALL-E 3, DALL-E 2)
    - Replicate (Stable Diffusion, FLUX)
    - Stability AI (SDXL)
    """
    
    # Configurações de provedores
    PROVIDERS = {
        'openai': {
            'api_url': 'https://api.openai.com/v1/images/generations',
            'env_key': 'OPENAI_API_KEY',
            'default_model': 'dall-e-3'
        },
        'replicate': {
            'api_url': 'https://api.replicate.com/v1/predictions',
            'env_key': 'REPLICATE_API_TOKEN',
            'default_model': 'stability-ai/sdxl'
        },
        'stability': {
            'api_url': 'https://api.stability.ai/v1/generation',
            'env_key': 'STABILITY_API_KEY',
            'default_model': 'stable-diffusion-xl-1024-v1-0'
        }
    }
    
    def __init__(self):
        super().__init__(
            name="image-gen",
            description="Gera imagens usando APIs de IA como DALL-E, Stable Diffusion e Replicate."
        )
        self.output_dir = Path(os.environ.get('IMAGE_GEN_OUTPUT_DIR', './outputs/images'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, params: str) -> str:
        """
        Executa a skill.
        
        Formato: action:<action> prompt:<prompt> [provider:<provider>] [outros params]
        
        Actions:
        - generate: Gera uma nova imagem
        - variation: Cria variação de imagem existente
        - edit: Edita imagem com máscara (inpainting)
        - providers: Lista provedores disponíveis
        """
        parsed = self._parse_params(params)
        action = parsed.get('action', 'generate')
        
        try:
            if action == 'providers':
                return self._list_providers()
            elif action == 'generate':
                return self._generate(parsed)
            elif action == 'variation':
                return self._variation(parsed)
            elif action == 'edit':
                return self._edit(parsed)
            else:
                return f"Ação desconhecida: {action}"
        except Exception as e:
            logger.exception(f"Erro no ImageGenSkill: {e}")
            return f"❌ Erro: {str(e)}"
    
    def _parse_params(self, params: str) -> Dict[str, str]:
        """Parse de parâmetros."""
        result = {}
        pattern = r'(\w+):(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))'
        matches = re.findall(pattern, params)
        for key, q1, q2, simple in matches:
            result[key] = q1 or q2 or simple
        return result
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Obtém API key para o provedor."""
        env_key = self.PROVIDERS.get(provider, {}).get('env_key', '')
        return os.environ.get(env_key)
    
    def _list_providers(self) -> str:
        """Lista provedores disponíveis."""
        lines = ["🎨 Provedores de Image Gen:\n"]
        
        for name, config in self.PROVIDERS.items():
            api_key = self._get_api_key(name)
            status = "✅" if api_key else "❌"
            lines.append(f"  {status} {name}")
            lines.append(f"     Modelo padrão: {config['default_model']}")
            lines.append(f"     Env: {config['env_key']}")
        
        return "\n".join(lines)
    
    def _generate(self, params: Dict[str, str]) -> str:
        """Gera uma imagem."""
        prompt = params.get('prompt', '')
        if not prompt:
            return "❌ prompt é obrigatório"
        
        provider = params.get('provider', 'openai')
        model = params.get('model', self.PROVIDERS.get(provider, {}).get('default_model', 'dall-e-3'))
        size = params.get('size', '1024x1024')
        quality = params.get('quality', 'standard')
        style = params.get('style', 'vivid')
        output = params.get('output', '')
        
        # Verifica API key
        api_key = self._get_api_key(provider)
        if not api_key:
            return f"❌ API key não configurada para {provider}. Defina {self.PROVIDERS[provider]['env_key']}"
        
        # Gera baseado no provedor
        if provider == 'openai':
            return self._generate_openai(prompt, model, size, quality, style, output, api_key)
        elif provider == 'replicate':
            return self._generate_replicate(prompt, model, size, output, api_key)
        elif provider == 'stability':
            return self._generate_stability(prompt, model, size, output, api_key)
        else:
            return f"❌ Provedor não suportado: {provider}"
    
    def _generate_openai(self, prompt: str, model: str, size: str, 
                         quality: str, style: str, output: str, api_key: str) -> str:
        """Gera imagem via OpenAI."""
        url = 'https://api.openai.com/v1/images/generations'
        
        payload = {
            'model': model,
            'prompt': prompt,
            'n': 1,
            'size': size,
            'quality': quality,
            'style': style,
            'response_format': 'b64_json'
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if hasattr(e, 'read') else str(e)
            return f"❌ Erro OpenAI: {error_body}"
        
        # Salva imagem
        image_data = result['data'][0]['b64_json']
        revised_prompt = result['data'][0].get('revised_prompt', prompt)
        
        output_path = self._save_image(image_data, output, 'openai')
        
        return f"""🎨 Imagem gerada com sucesso!

📁 Arquivo: {output_path}
🤖 Modelo: {model}
📐 Tamanho: {size}

💬 Prompt revisado:
{revised_prompt[:200]}{'...' if len(revised_prompt) > 200 else ''}"""
    
    def _generate_replicate(self, prompt: str, model: str, size: str, 
                            output: str, api_key: str) -> str:
        """Gera imagem via Replicate."""
        url = 'https://api.replicate.com/v1/predictions'
        
        # Monta payload baseado no modelo
        width, height = size.split('x') if 'x' in size else ('1024', '1024')
        
        payload = {
            'version': model,
            'input': {
                'prompt': prompt,
                'width': int(width),
                'height': int(height)
            }
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Token {api_key}'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if hasattr(e, 'read') else str(e)
            return f"❌ Erro Replicate: {error_body}"
        
        # Replicate retorna um ID de predição, precisa polling
        prediction_id = result.get('id')
        get_url = result.get('urls', {}).get('get', f'{url}/{prediction_id}')
        
        return f"""⏳ Geração iniciada!

ID: {prediction_id}
Status: {result.get('status')}

Use `image-gen action:status id:{prediction_id}` para verificar."""
    
    def _generate_stability(self, prompt: str, model: str, size: str,
                            output: str, api_key: str) -> str:
        """Gera imagem via Stability AI."""
        width, height = size.split('x') if 'x' in size else ('1024', '1024')
        
        url = f'https://api.stability.ai/v1/generation/{model}/text-to-image'
        
        payload = {
            'text_prompts': [{'text': prompt, 'weight': 1}],
            'cfg_scale': 7,
            'height': int(height),
            'width': int(width),
            'samples': 1,
            'steps': 30
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if hasattr(e, 'read') else str(e)
            return f"❌ Erro Stability: {error_body}"
        
        # Salva primeira imagem
        artifacts = result.get('artifacts', [])
        if not artifacts:
            return "❌ Nenhuma imagem gerada"
        
        image_data = artifacts[0].get('base64')
        output_path = self._save_image(image_data, output, 'stability')
        
        return f"""🎨 Imagem gerada com sucesso!

📁 Arquivo: {output_path}
🤖 Modelo: {model}
📐 Tamanho: {size}"""
    
    def _variation(self, params: Dict[str, str]) -> str:
        """Cria variação de imagem existente."""
        image_path = params.get('image', '')
        if not image_path or not Path(image_path).exists():
            return "❌ Caminho da imagem é obrigatório e deve existir"
        
        return "⚠️ Variação ainda não implementada. Use action:generate."
    
    def _edit(self, params: Dict[str, str]) -> str:
        """Edita imagem com máscara."""
        image_path = params.get('image', '')
        mask_path = params.get('mask', '')
        prompt = params.get('prompt', '')
        
        if not all([image_path, prompt]):
            return "❌ image e prompt são obrigatórios"
        
        return "⚠️ Edição (inpainting) ainda não implementada. Use action:generate."
    
    def _save_image(self, b64_data: str, output_path: str, prefix: str) -> str:
        """Salva imagem base64 em arquivo."""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.output_dir / f"{prefix}_{timestamp}_{uuid.uuid4().hex[:6]}.png"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        image_bytes = base64.b64decode(b64_data)
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
        
        return str(output_path)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "image_generate",
                "description": "Gera uma imagem a partir de prompt",
                "parameters": {
                    "prompt": {"type": "string", "required": True},
                    "provider": {"type": "string", "enum": ["openai", "replicate", "stability"]},
                    "size": {"type": "string", "default": "1024x1024"}
                }
            }
        ]


# Para testes
if __name__ == "__main__":
    skill = ImageGenSkill()
    print(skill.get_definition())
    print("\n--- Provedores ---")
    print(skill.execute('action:providers'))
