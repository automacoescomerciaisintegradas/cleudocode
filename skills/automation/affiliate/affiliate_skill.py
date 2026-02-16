"""
Affiliate Skill para Cleudocode
===============================

Processamento de links de afiliados Shopee, Amazon e Mercado Livre.
Detecta plataformas, converte links e extrai mídia.

Autor: Cleudocode Team
Data: 13/02/2026
"""

import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from pathlib import Path

# Ajuste de sys.path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.base import BaseSkill

logger = logging.getLogger(__name__)

class AffiliateSkill(BaseSkill):
    """
    Skill para gestão de links e mídia de afiliados.
    """
    
    def __init__(self):
        super().__init__(
            name="affiliate",
            description="Conversão de links e extração de mídia para programas de afiliados (Shopee, Amazon, Mercado Livre)."
        )
        self.shopee_id = os.getenv("SHOPEE_AFFILIATE_ID", "18372150411")
        self.amazon_tag = os.getenv("AMAZON_AFFILIATE_TAG", "")
        self.ml_id = os.getenv("ML_AFFILIATE_ID", "")

    def execute(self, params: str) -> str:
        """
        Executa ações de afiliados.
        
        Ações:
        - resolve: Detecta plataforma, gera link de afiliado e extrai mídia.
        - extract_media: Apenas extrai mídia de uma URL.
        """
        parsed = self._parse_params(params)
        action = parsed.get('action', 'resolve')
        url = parsed.get('url', '')

        if not url:
            return "❌ Erro: Uma URL deve ser fornecida (parâmetro url:\"...\")"

        try:
            if action == 'resolve':
                return self._resolve_all(url)
            elif action == 'extract_media':
                data = self._extract_media(url)
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                return f"Ação desconhecida: {action}."
        except Exception as e:
            logger.exception(f"Erro no AffiliateSkill: {e}")
            return f"❌ Erro: {str(e)}"

    def _parse_params(self, params: str) -> Dict[str, str]:
        import re
        result = {}
        pattern = r'(\w+):(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))'
        matches = re.findall(pattern, params)
        for key, quoted_double, quoted_single, simple_val in matches:
            result[key] = quoted_double or quoted_single or simple_val
        return result

    def _detect_platform(self, url: str) -> str:
        url = url.lower()
        if "shopee" in url or "shp.ee" in url:
            return "shopee"
        elif "amazon" in url or "amzn.to" in url:
            return "amazon"
        elif "mercadolivre" in url or "mlstatic" in url or "mercadolivre.com" in url:
            return "mercadolivre"
        return "unknown"

    def _resolve_all(self, url: str) -> str:
        """Resolve link e extrai mídia."""
        platform = self._detect_platform(url)
        
        # 1. Resolver Link Afiliado (Simulação ou API se disponível)
        affiliate_link = self._generate_affiliate_link(url, platform)
        
        # 2. Extrair Mídia
        media_data = self._extract_media(url, platform)
        
        result = {
            "platform": platform,
            "original_url": url,
            "affiliate_link": affiliate_link,
            "product_title": media_data.get("title", "Produto"),
            "price": media_data.get("price", "Sob consulta"),
            "old_price": media_data.get("old_price", ""),
            "category": media_data.get("category", "Geral"),
            "images": media_data.get("images", []),
            "videos": media_data.get("videos", [])
        }
        
        import json
        return f"✅ Link resolvido ({platform}):\n\n" + json.dumps(result, indent=2, ensure_ascii=False)

    def _generate_affiliate_link(self, url: str, platform: str) -> str:
        """Gera o link de afiliado."""
        if platform == "shopee":
            # Extrair IDs do produto se for um link longo
            # Ex: https://shopee.com.br/product/1006215031/22596833753
            match = re.search(r'product/(\d+)/(\d+)', url)
            if match:
                shop_id, item_id = match.groups()
                return f"https://shopee.com.br/product/{shop_id}/{item_id}?af_id={self.shopee_id}"
            
            # Formato de link encurtado (s.shopee.com.br) ou outros
            if "?" in url:
                return f"{url}&af_id={self.shopee_id}"
            return f"{url}?af_id={self.shopee_id}"
            
        elif platform == "amazon":
            joiner = "&" if "?" in url else "?"
            return f"{url}{joiner}tag={self.amazon_tag}"
        elif platform == "mercadolivre":
            return f"{url}#c_id={self.ml_id}"
        return url

    def _extract_media(self, url: str, platform: str = None) -> Dict[str, Any]:
        """Extrai mídia básica via scraping simples."""
        if not platform:
            platform = self._detect_platform(url)
            
        data = {"title": "", "price": "", "old_price": "", "category": "Geral", "images": [], "videos": []}
        
        try:
            # Em produção, usaríamos proxies ou APIs oficiais
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Título genérico
            title_tag = soup.find('title')
            if title_tag:
                data["title"] = title_tag.text.strip()
            
            # Lógica específica por plataforma (Simplificada para demo)
            if platform == "shopee":
                # Shopee é muito dinâmico (JS), scraping simples pode falhar
                # Buscamos tags OpenGraph
                og_image = soup.find('meta', property='og:image')
                if og_image:
                    data["images"].append(og_image['content'])
            
            elif platform == "amazon":
                # Amazon images
                img_tag = soup.find('img', id='landingImage')
                if img_tag:
                    data["images"].append(img_tag.get('src'))
            
            elif platform == "mercadolivre":
                # Título e Preço ML
                title_tag = soup.find('h1', class_='ui-pdp-title')
                if title_tag: data["title"] = title_tag.text.strip()
                
                # Preços
                price_meta = soup.find('meta', itemprop='price')
                if price_meta: data["price"] = f"R$ {price_meta['content']}"
                
                old_price_tag = soup.find('span', class_='andes-money-amount__fraction', style=re.compile(r'text-decoration:line-through'))
                if not old_price_tag:
                     old_price_tag = soup.find('s', class_='andes-money-amount')
                if old_price_tag: data["old_price"] = f"R$ {old_price_tag.text.strip()}"
                
                # Categoria
                breadcrumb = soup.find_all('a', class_='andes-breadcrumb__link')
                if breadcrumb and len(breadcrumb) > 1:
                    data["category"] = breadcrumb[1].text.strip() # Geralmente a segunda é a principal

                img_tag = soup.find('img', class_='ui-pdp-image')
                if img_tag:
                    data["images"].append(img_tag.get('src') or img_tag.get('data-src'))

        except Exception as e:
            logger.warning(f"Falha ao extrair mídia de {url}: {e}")
            
        return data

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "affiliate_resolve",
                "description": "Resolve link de produto e extrai mídia para Shopee, Amazon ou ML",
                "parameters": {
                    "url": {"type": "string", "description": "URL original do produto", "required": True}
                }
            }
        ]

if __name__ == "__main__":
    skill = AffiliateSkill()
    print(skill.execute('action:resolve url:"https://shopee.com.br/product_test"'))
