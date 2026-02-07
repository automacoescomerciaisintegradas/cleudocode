"""
Browser Skill para Cleudocode
=============================

Controla navegador para automação web, scraping e screenshots
usando Playwright ou alternativas.

Autor: Cleudocode Team
Data: 02/02/2026
"""

import subprocess
import json
import os
import tempfile
import base64
from typing import Dict, Any, List, Optional
from pathlib import Path
import re
import logging

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.base import BaseSkill

logger = logging.getLogger(__name__)

# Tenta importar Playwright
try:
    from playwright.sync_api import sync_playwright, Page, Browser
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    logger.warning("Playwright não instalado. Funcionalidade limitada.")


class BrowserSkill(BaseSkill):
    """
    Skill para automação de navegador web.
    
    Funcionalidades:
    - Navegar para URLs
    - Capturar screenshots
    - Extrair conteúdo (texto, HTML)
    - Interagir com elementos (click, type)
    - Executar JavaScript
    
    Requer: pip install playwright && playwright install chromium
    """
    
    def __init__(self):
        super().__init__(
            name="browser",
            description="Controla navegador para automação web, scraping e screenshots."
        )
        self._browser: Optional['Browser'] = None
        self._page: Optional['Page'] = None
        self._playwright = None
    
    def _ensure_browser(self, headless: bool = True) -> 'Page':
        """Garante que o navegador está iniciado e retorna a página."""
        if not HAS_PLAYWRIGHT:
            raise RuntimeError(
                "Playwright não instalado. Execute:\n"
                "  pip install playwright\n"
                "  playwright install chromium"
            )
        
        if self._page is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=headless)
            self._page = self._browser.new_page()
            self._page.set_default_timeout(30000)  # 30s timeout
        
        return self._page
    
    def _close_browser(self):
        """Fecha o navegador se estiver aberto."""
        if self._page:
            self._page.close()
            self._page = None
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
    
    def execute(self, params: str) -> str:
        """
        Executa a skill com os parâmetros fornecidos.
        
        Formato: action:<action> [url:<url>] [selector:<selector>] [outros params]
        
        Actions:
        - navigate: Navegar para uma URL
        - screenshot: Capturar screenshot
        - extract: Extrair texto/HTML
        - click: Clicar em elemento
        - type: Digitar texto
        - eval: Executar JavaScript
        - close: Fechar navegador
        - status: Verificar status
        """
        parsed = self._parse_params(params)
        action = parsed.get('action', 'status')
        headless = parsed.get('headless', 'true').lower() != 'false'
        
        try:
            if action == 'status':
                return self._status()
            elif action == 'navigate':
                return self._navigate(parsed.get('url', ''), headless)
            elif action == 'screenshot':
                return self._screenshot(parsed.get('output', ''), 
                                       parsed.get('fullpage', 'false').lower() == 'true',
                                       headless)
            elif action == 'extract':
                return self._extract(parsed.get('selector', 'body'),
                                    parsed.get('format', 'text'),
                                    headless)
            elif action == 'click':
                return self._click(parsed.get('selector', ''), headless)
            elif action == 'type':
                return self._type_text(parsed.get('selector', ''),
                                       parsed.get('text', ''),
                                       headless)
            elif action == 'eval':
                return self._eval_js(parsed.get('script', ''), headless)
            elif action == 'close':
                return self._close()
            elif action == 'curl':
                # Fallback sem Playwright
                return self._curl_fetch(parsed.get('url', ''))
            else:
                return f"Ação desconhecida: {action}. Use: navigate, screenshot, extract, click, type, eval, close"
        except Exception as e:
            logger.exception(f"Erro no BrowserSkill: {e}")
            return f"❌ Erro: {str(e)}"
    
    def _parse_params(self, params: str) -> Dict[str, str]:
        """Parse de parâmetros no formato key:value."""
        result = {}
        pattern = r'(\w+):(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))'
        matches = re.findall(pattern, params)
        for key, quoted_double, quoted_single, simple_val in matches:
            result[key] = quoted_double or quoted_single or simple_val
        return result
    
    def _status(self) -> str:
        """Retorna status do navegador."""
        status_lines = ["🌐 Browser Skill Status:\n"]
        
        status_lines.append(f"  Playwright: {'✅ Instalado' if HAS_PLAYWRIGHT else '❌ Não instalado'}")
        status_lines.append(f"  Navegador: {'🟢 Ativo' if self._browser else '⚪ Inativo'}")
        
        if self._page:
            try:
                url = self._page.url
                title = self._page.title()
                status_lines.append(f"  URL atual: {url}")
                status_lines.append(f"  Título: {title}")
            except:
                status_lines.append("  Página: (erro ao obter info)")
        
        if not HAS_PLAYWRIGHT:
            status_lines.append("\n⚠️ Para funcionalidade completa, instale:")
            status_lines.append("  pip install playwright")
            status_lines.append("  playwright install chromium")
            status_lines.append("\n💡 Modo fallback disponível: action:curl url:<url>")
        
        return "\n".join(status_lines)
    
    def _navigate(self, url: str, headless: bool = True) -> str:
        """Navega para uma URL."""
        if not url:
            return "❌ URL é obrigatória. Use: url:\"https://example.com\""
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        page = self._ensure_browser(headless)
        
        response = page.goto(url, wait_until='domcontentloaded')
        status = response.status if response else 'N/A'
        title = page.title()
        
        return f"""✅ Navegação concluída!

  URL: {url}
  Status: {status}
  Título: {title}
  
📌 Próximos passos:
  - action:screenshot output:"pagina.png"
  - action:extract selector:"body"
  - action:close"""
    
    def _screenshot(self, output: str, fullpage: bool, headless: bool) -> str:
        """Captura screenshot da página."""
        page = self._ensure_browser(headless)
        
        if not output:
            # Gera nome temporário
            output = os.path.join(tempfile.gettempdir(), 'cleudocode_screenshot.png')
        
        # Garante extensão .png
        if not output.endswith('.png'):
            output += '.png'
        
        # Garante que o diretório existe
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        
        page.screenshot(path=output, full_page=fullpage)
        
        return f"""📸 Screenshot capturado!

  Arquivo: {output}
  Full page: {fullpage}
  URL: {page.url}"""
    
    def _extract(self, selector: str, format_type: str, headless: bool) -> str:
        """Extrai conteúdo da página."""
        page = self._ensure_browser(headless)
        
        try:
            element = page.query_selector(selector)
            if not element:
                return f"❌ Elemento não encontrado: {selector}"
            
            if format_type == 'html':
                content = element.inner_html()
            elif format_type == 'outer':
                content = element.evaluate('el => el.outerHTML')
            else:  # text
                content = element.inner_text()
            
            # Limita tamanho do output
            if len(content) > 5000:
                content = content[:5000] + f"\n\n[... truncado, total: {len(content)} chars]"
            
            return f"""📄 Conteúdo extraído (selector: {selector}):

{content}"""
        except Exception as e:
            return f"❌ Erro ao extrair: {str(e)}"
    
    def _click(self, selector: str, headless: bool) -> str:
        """Clica em um elemento."""
        if not selector:
            return "❌ Selector é obrigatório. Use: selector:\"#button\""
        
        page = self._ensure_browser(headless)
        
        try:
            page.click(selector)
            return f"✅ Click executado em: {selector}"
        except Exception as e:
            return f"❌ Erro ao clicar: {str(e)}"
    
    def _type_text(self, selector: str, text: str, headless: bool) -> str:
        """Digita texto em um campo."""
        if not selector:
            return "❌ Selector é obrigatório. Use: selector:\"#input\""
        if not text:
            return "❌ Text é obrigatório. Use: text:\"seu texto\""
        
        page = self._ensure_browser(headless)
        
        try:
            page.fill(selector, text)
            return f"✅ Texto digitado em {selector}: {text[:50]}{'...' if len(text) > 50 else ''}"
        except Exception as e:
            return f"❌ Erro ao digitar: {str(e)}"
    
    def _eval_js(self, script: str, headless: bool) -> str:
        """Executa JavaScript na página."""
        if not script:
            return "❌ Script é obrigatório. Use: script:\"document.title\""
        
        page = self._ensure_browser(headless)
        
        try:
            result = page.evaluate(script)
            
            if isinstance(result, (dict, list)):
                result_str = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                result_str = str(result)
            
            return f"""⚡ JavaScript executado:

Script: {script}

Resultado:
{result_str}"""
        except Exception as e:
            return f"❌ Erro ao executar JS: {str(e)}"
    
    def _close(self) -> str:
        """Fecha o navegador."""
        if self._browser:
            self._close_browser()
            return "✅ Navegador fechado."
        else:
            return "ℹ️ Navegador já estava fechado."
    
    def _curl_fetch(self, url: str) -> str:
        """Fallback: busca URL via curl (sem Playwright)."""
        if not url:
            return "❌ URL é obrigatória."
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            result = subprocess.run(
                ['curl', '-s', '-L', '-A', 'Mozilla/5.0', url],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            
            content = result.stdout
            if len(content) > 5000:
                content = content[:5000] + f"\n\n[... truncado, total: {len(content)} chars]"
            
            return f"""📄 Conteúdo de {url} (via curl):

{content}"""
        except Exception as e:
            return f"❌ Erro no curl: {str(e)}"
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna lista de ferramentas para o LLM."""
        return [
            {
                "name": "browser_navigate",
                "description": "Navega para uma URL",
                "parameters": {
                    "url": {"type": "string", "description": "URL para navegar", "required": True},
                    "headless": {"type": "boolean", "description": "Modo invisível", "default": True}
                }
            },
            {
                "name": "browser_screenshot",
                "description": "Captura screenshot da página atual",
                "parameters": {
                    "output": {"type": "string", "description": "Caminho para salvar o arquivo"},
                    "fullpage": {"type": "boolean", "description": "Capturar página inteira", "default": False}
                }
            },
            {
                "name": "browser_extract",
                "description": "Extrai texto ou HTML de um elemento",
                "parameters": {
                    "selector": {"type": "string", "description": "Seletor CSS", "default": "body"},
                    "format": {"type": "string", "description": "Formato: text, html, outer", "default": "text"}
                }
            }
        ]
    
    def get_definition(self) -> str:
        """Retorna definição para o LLM."""
        playwright_status = "✅ Instalado" if HAS_PLAYWRIGHT else "❌ Não instalado (modo fallback)"
        
        return f"""<tool_definition>
<name>{self.name}</name>
<emoji>{self.metadata.emoji}</emoji>
<description>{self.description}</description>
<available>{self.is_available()}</available>
<playwright>{playwright_status}</playwright>

<usage>
<!-- Verificar status -->
<tool code="browser">
action:status
</tool>

<!-- Navegar para URL -->
<tool code="browser">
action:navigate url:"https://example.com"
</tool>

<!-- Screenshot -->
<tool code="browser">
action:screenshot output:"/tmp/page.png" fullpage:true
</tool>

<!-- Extrair conteúdo -->
<tool code="browser">
action:extract selector:"h1"
</tool>

<!-- Interação -->
<tool code="browser">
action:click selector:"#submit-btn"
</tool>

<tool code="browser">
action:type selector:"#search" text:"minha busca"
</tool>

<!-- JavaScript -->
<tool code="browser">
action:eval script:"document.querySelectorAll('a').length"
</tool>

<!-- Fechar -->
<tool code="browser">
action:close
</tool>

<!-- Fallback (sem Playwright) -->
<tool code="browser">
action:curl url:"https://example.com"
</tool>
</usage>

<actions>
- status: Verificar status do navegador
- navigate: Navegar para URL
- screenshot: Capturar screenshot
- extract: Extrair texto/HTML
- click: Clicar em elemento
- type: Digitar texto
- eval: Executar JavaScript
- close: Fechar navegador
- curl: Fetch via curl (fallback)
</actions>
</tool_definition>"""
    
    def __del__(self):
        """Garante que o navegador é fechado."""
        try:
            self._close_browser()
        except:
            pass


# Para testes diretos
if __name__ == "__main__":
    skill = BrowserSkill()
    print(skill.get_definition())
    print("\n--- Teste: Status ---")
    print(skill.execute('action:status'))
