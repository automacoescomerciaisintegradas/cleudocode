"""
Base Skill para Cleudocode
==========================

Classe base para todas as habilidades (Tools) do agente, com suporte 
completo a metadados via SKILL.md e validação de requisitos.

Autor: Cleudocode Team
Data: 02/02/2026
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
import shutil
import os
import re
import logging

# Tenta importar yaml, fallback para parse manual se não disponível
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

logger = logging.getLogger(__name__)


@dataclass
class SkillMetadata:
    """
    Metadados de uma skill extraídos do SKILL.md.
    
    Attributes:
        name: Nome único da skill
        description: Descrição para o LLM
        emoji: Emoji representativo
        category: Categoria (builtin, productivity, etc.)
        homepage: URL da documentação
        requires: Requisitos (bins, env, packages)
        install: Instruções de instalação
        version: Versão da skill
        author: Autor da skill
    """
    name: str = ""
    description: str = ""
    emoji: str = "🔧"
    category: str = "builtin"
    homepage: str = ""
    requires: Dict[str, Any] = field(default_factory=dict)
    install: List[Dict] = field(default_factory=list)
    version: str = "1.0.0"
    author: str = "Cleudocode Team"
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "name": self.name,
            "description": self.description,
            "emoji": self.emoji,
            "category": self.category,
            "homepage": self.homepage,
            "requires": self.requires,
            "install": self.install,
            "version": self.version,
            "author": self.author
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SkillMetadata':
        """Cria SkillMetadata a partir de um dicionário."""
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            emoji=data.get('emoji', '🔧'),
            category=data.get('category', 'builtin'),
            homepage=data.get('homepage', ''),
            requires=data.get('requires', {}),
            install=data.get('install', []),
            version=data.get('version', '1.0.0'),
            author=data.get('author', 'Cleudocode Team')
        )


def parse_yaml_frontmatter(content: str) -> dict:
    """Parse do YAML frontmatter de um arquivo markdown."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    yaml_content = match.group(1)
    
    if HAS_YAML:
        try:
            return yaml.safe_load(yaml_content) or {}
        except Exception as e:
            logger.warning(f"Erro ao parsear YAML: {e}")
            return {}
    else:
        # Parse manual básico
        result = {}
        current_key = None
        for line in yaml_content.split('\n'):
            if ':' in line and not line.startswith(' '):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                if value:
                    result[key] = value
                else:
                    result[key] = {}
                current_key = key
        return result


class BaseSkill(ABC):
    """
    Classe base para todas as habilidades (Tools) do Cleudocode.
    
    Fornece:
    - Suporte a metadados via SKILL.md
    - Validação de requisitos (bins, env vars, packages)
    - Definição de ferramentas para o LLM
    - Hot-reload automático
    
    Exemplo de implementação:
    
    ```python
    class WeatherSkill(BaseSkill):
        def __init__(self):
            super().__init__(
                name="weather",
                description="Obtém previsão do tempo."
            )
        
        def execute(self, params: str) -> str:
            # Implementação...
            return "Resultado"
        
        def get_tools(self) -> list:
            return [{"name": "weather_current", ...}]
    ```
    """
    
    def __init__(self, name: str, description: str):
        """
        Inicializa a skill.
        
        Args:
            name: Nome único da skill
            description: Descrição para o LLM
        """
        self.name = name
        self.description = description
        self.metadata = SkillMetadata(name=name, description=description)
        self._skill_dir: Optional[Path] = None
        self._load_metadata_from_file()
    
    def _find_skill_dir(self) -> Optional[Path]:
        """Tenta encontrar o diretório da skill."""
        # Tenta encontrar baseado no arquivo atual
        import inspect
        try:
            frame = inspect.currentframe()
            if frame and frame.f_back and frame.f_back.f_back:
                caller_file = inspect.getfile(frame.f_back.f_back)
                caller_dir = Path(caller_file).parent
                if (caller_dir / "SKILL.md").exists():
                    return caller_dir
        except:
            pass
        return None
    
    def _load_metadata_from_file(self):
        """Carrega metadados do SKILL.md se existir."""
        skill_dir = self._find_skill_dir()
        if not skill_dir:
            return
        
        self._skill_dir = skill_dir
        skill_md = skill_dir / "SKILL.md"
        
        if not skill_md.exists():
            return
        
        try:
            content = skill_md.read_text(encoding='utf-8')
            frontmatter = parse_yaml_frontmatter(content)
            
            # Atualiza metadados básicos
            self.metadata.name = frontmatter.get('name', self.name)
            self.metadata.description = frontmatter.get('description', self.description)
            self.metadata.homepage = frontmatter.get('homepage', '')
            
            # Metadados específicos do Cleudocode
            cleudo_meta = frontmatter.get('metadata', {}).get('cleudocode', {})
            if cleudo_meta:
                self.metadata.emoji = cleudo_meta.get('emoji', '🔧')
                self.metadata.category = cleudo_meta.get('category', 'builtin')
                self.metadata.requires = cleudo_meta.get('requires', {})
                self.metadata.install = cleudo_meta.get('install', [])
            
            # Sincroniza com atributos da instância
            self.name = self.metadata.name
            self.description = self.metadata.description
            
        except Exception as e:
            logger.warning(f"Erro ao carregar SKILL.md: {e}")
    
    def set_metadata(self, metadata: SkillMetadata):
        """Define os metadados da skill (usado pelo loader)."""
        self.metadata = metadata
        self.name = metadata.name
        self.description = metadata.description
    
    @abstractmethod
    def execute(self, params: str) -> str:
        """
        Executa a skill com os parâmetros fornecidos.
        
        Args:
            params: Parâmetros da skill (geralmente string do XML)
            
        Returns:
            Resultado da execução como string
        """
        pass
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de ferramentas disponíveis para o LLM.
        
        Override este método para definir ferramentas estruturadas.
        
        Returns:
            Lista de dicionários com definição das ferramentas
        """
        return [{
            "name": self.name,
            "description": self.description,
            "parameters": {}
        }]
    
    def check_requirements(self) -> Dict[str, bool]:
        """
        Verifica se os requisitos estão satisfeitos.
        
        Returns:
            Dicionário {requisito: bool} indicando status
        """
        results = {}
        
        # Verificar binários obrigatórios
        for bin_name in self.metadata.requires.get('bins', []):
            results[f"bin:{bin_name}"] = shutil.which(bin_name) is not None
        
        # Verificar se qualquer um dos binários opcionais existe
        any_bins = self.metadata.requires.get('anyBins', [])
        if any_bins:
            found_any = any(shutil.which(b) is not None for b in any_bins)
            results[f"anyBins:{','.join(any_bins)}"] = found_any
        
        # Verificar variáveis de ambiente
        for env_name in self.metadata.requires.get('env', []):
            results[f"env:{env_name}"] = env_name in os.environ
        
        # Verificar pacotes Python
        for package in self.metadata.requires.get('packages', []):
            pkg_name = package.split('>=')[0].split('==')[0].split('<')[0]
            try:
                __import__(pkg_name.replace('-', '_'))
                results[f"package:{pkg_name}"] = True
            except ImportError:
                results[f"package:{pkg_name}"] = False
        
        return results
    
    def is_available(self) -> bool:
        """
        Verifica se a skill está disponível para uso.
        
        Returns:
            True se todos os requisitos estão satisfeitos
        """
        reqs = self.check_requirements()
        return all(reqs.values()) if reqs else True
    
    def get_missing_requirements(self) -> List[str]:
        """
        Retorna lista de requisitos não satisfeitos.
        
        Returns:
            Lista de nomes de requisitos faltantes
        """
        reqs = self.check_requirements()
        return [req for req, met in reqs.items() if not met]
    
    def get_install_instructions(self) -> List[Dict]:
        """
        Retorna instruções de instalação para requisitos faltantes.
        
        Returns:
            Lista de instruções de instalação
        """
        return self.metadata.install
    
    def get_definition(self) -> str:
        """
        Retorna a definição XML/Prompt para o LLM saber como usar.
        
        Returns:
            String XML com a definição da skill
        """
        emoji = self.metadata.emoji if hasattr(self.metadata, 'emoji') else "🔧"
        
        return f"""<tool_definition>
<name>{self.name}</name>
<emoji>{emoji}</emoji>
<description>{self.description}</description>
<available>{self.is_available()}</available>
<usage>
<tool code="{self.name}">
[argumentos]
</tool>
</usage>
</tool_definition>"""
    
    def get_help(self) -> str:
        """
        Retorna texto de ajuda formatado para a skill.
        
        Returns:
            Texto de ajuda markdown
        """
        status = "✅ Disponível" if self.is_available() else "❌ Requisitos faltando"
        missing = self.get_missing_requirements()
        missing_text = f"\n⚠️ Faltando: {', '.join(missing)}" if missing else ""
        
        return f"""## {self.metadata.emoji} {self.name}

**Descrição:** {self.description}

**Status:** {status}{missing_text}

**Categoria:** {self.metadata.category}
**Versão:** {self.metadata.version}
"""
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', available={self.is_available()})>"
    
    def __str__(self) -> str:
        return f"{self.metadata.emoji} {self.name}: {self.description}"
