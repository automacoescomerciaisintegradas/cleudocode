"""
Cliente MCP (Model Context Protocol) para Cleudocode

Suporta integração com serviços MCP como Stitch (Google)
"""

import os
import json
import subprocess
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """Cliente genérico para Model Context Protocol"""
    
    @classmethod
    def list_all_services(cls, config_path: Optional[str] = None) -> List[str]:
        """Lista todos os serviços MCP configurados"""
        temp = cls.__new__(cls)
        config = temp._load_config(config_path)
        return list(config.get("mcp", {}).keys())
        
    def __init__(self, service_name: str = "stitch", config_path: Optional[str] = None):
        """
        Inicializa o cliente MCP
        
        Args:
            service_name: Nome do serviço MCP (ex: 'stitch')
            config_path: Caminho para config.yaml (opcional)
        """
        self.service_name = service_name
        self.config = self._load_config(config_path)
        self.service_config = self.config.get("mcp", {}).get(service_name, {})
        
        if not self.service_config.get("enabled", False):
            raise ValueError(f"Serviço MCP '{service_name}' não está habilitado")
        
        self.url = self.service_config.get("url")
        self.auth_config = self.service_config.get("auth", {})
        self.tools_config = self.service_config.get("tools", {})
        
        logger.info(f"Cliente MCP inicializado para: {service_name}")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Carrega configuração do config.yaml"""
        if config_path is None:
            config_path = os.path.expanduser("~/.cleudocode/config.yaml")
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar config: {e}")
            return {}
    
    def _get_access_token(self) -> str:
        """Obtém token de acesso OAuth2 via ADC"""
        auth_type = self.auth_config.get("type", "")
        
        if auth_type == "oauth2_adc":
            try:
                result = subprocess.run(
                    ["gcloud", "auth", "application-default", "print-access-token"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            except subprocess.CalledProcessError as e:
                raise Exception(f"Erro ao obter token ADC: {e}")
        else:
            raise ValueError(f"Tipo de autenticação não suportado: {auth_type}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Gera headers para requisição"""
        token = self._get_access_token()
        project_id = self.auth_config.get("project_id", "")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        if project_id:
            headers["X-Goog-User-Project"] = project_id
        
        return headers
    
    def call_tool(
        self, 
        tool_name: str, 
        arguments: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Chama uma ferramenta MCP
        
        Args:
            tool_name: Nome da ferramenta (ex: 'list_projects')
            arguments: Argumentos da ferramenta
            timeout: Timeout em segundos
        
        Returns:
            Resultado da chamada
        """
        # Verificar se ferramenta está habilitada
        tool_config = self.tools_config.get(tool_name, {})
        if not tool_config.get("enabled", False):
            raise ValueError(f"Ferramenta '{tool_name}' não está habilitada")
        
        # Preparar payload JSON-RPC 2.0
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            },
            "id": 1
        }
        
        logger.info(f"Chamando ferramenta MCP: {tool_name}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                self.url,
                headers=self._get_headers(),
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verificar se há erro no resultado
                if "result" in result:
                    rpc_result = result["result"]
                    
                    if rpc_result.get("isError"):
                        error_msg = self._extract_error_message(rpc_result)
                        raise Exception(f"Erro MCP: {error_msg}")
                    
                    # Extrair conteúdo
                    return self._extract_content(rpc_result)
                
                return result
            else:
                raise Exception(
                    f"Erro HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de requisição: {e}")
    
    def _extract_error_message(self, rpc_result: Dict) -> str:
        """Extrai mensagem de erro do resultado RPC"""
        if "content" in rpc_result:
            for content in rpc_result["content"]:
                if content.get("type") == "text":
                    return content.get("text", "Erro desconhecido")
        return "Erro desconhecido"
    
    def _extract_content(self, rpc_result: Dict) -> Any:
        """Extrai conteúdo do resultado RPC"""
        if "content" in rpc_result:
            for content in rpc_result["content"]:
                if content.get("type") == "text":
                    text = content.get("text", "")
                    # Tentar parsear como JSON
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return text
        return rpc_result
    
    def list_available_tools(self) -> List[Dict[str, str]]:
        """Lista ferramentas disponíveis e habilitadas"""
        tools = []
        for tool_name, tool_config in self.tools_config.items():
            if tool_config.get("enabled", False):
                tools.append({
                    "name": tool_name,
                    "description": tool_config.get("description", ""),
                    "enabled": True
                })
        return tools


# Funções de conveniência para Stitch

class StitchClient(MCPClient):
    """Cliente especializado para Stitch MCP"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(service_name="stitch", config_path=config_path)
    
    def list_projects(self) -> List[Dict]:
        """Lista todos os projetos do Stitch"""
        result = self.call_tool("list_projects")
        return result.get("projects", [])
    
    def get_project(self, project_id: str) -> Dict:
        """Obtém detalhes de um projeto"""
        return self.call_tool("get_project", {"project_id": project_id})
    
    def create_project(self, title: str, **kwargs) -> Dict:
        """Cria novo projeto"""
        args = {"title": title, **kwargs}
        return self.call_tool("create_project", args)
    
    def list_screens(self, project_id: str) -> List[Dict]:
        """Lista telas de um projeto"""
        result = self.call_tool("list_screens", {"project_id": project_id})
        return result.get("screens", [])
    
    def get_screen(self, screen_id: str) -> Dict:
        """Obtém detalhes de uma tela"""
        return self.call_tool("get_screen", {"screen_id": screen_id})
    
    def generate_screen(
        self, 
        prompt: str, 
        project_id: Optional[str] = None,
        device_type: str = "MOBILE",
        **kwargs
    ) -> Dict:
        """Gera nova tela a partir de prompt"""
        args = {
            "prompt": prompt,
            "device_type": device_type,
            **kwargs
        }
        if project_id:
            args["project_id"] = project_id
        
        return self.call_tool("generate_screen_from_text", args)
    
    def fetch_screen_code(self, screen_id: str) -> str:
        """Baixa código HTML/CSS/JS de uma tela"""
        result = self.call_tool("fetch_screen_code", {"screen_id": screen_id})
        return result.get("code", "")
    
    def fetch_screen_image(self, screen_id: str) -> str:
        """Baixa URL da imagem de uma tela"""
        result = self.call_tool("fetch_screen_image", {"screen_id": screen_id})
        return result.get("image_url", "")
    
    def extract_design_context(self, screen_id: str) -> Dict:
        """Extrai contexto de design de uma tela"""
        return self.call_tool("extract_design_context", {"screen_id": screen_id})


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.INFO)
    
    try:
        client = StitchClient()
        print("✅ Cliente Stitch inicializado")
        
        # Listar ferramentas
        tools = client.list_available_tools()
        print(f"\n📋 Ferramentas disponíveis: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # Listar projetos
        print("\n🎨 Listando projetos...")
        projects = client.list_projects()
        print(f"Total: {len(projects)} projetos")
        
        for i, proj in enumerate(projects[:3], 1):
            print(f"\n  Projeto {i}:")
            print(f"    Nome: {proj.get('title', 'N/A')}")
            print(f"    ID: {proj.get('name', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
