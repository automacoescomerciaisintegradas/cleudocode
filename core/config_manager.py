"""
Cleudocode Configuration Manager
Similar to OpenClaw's configuration system
"""

import os
import yaml
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CleudocodeConfig:
    """Configuration data class"""
    config_path: Path
    data: Dict[str, Any]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'system.name')"""
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        data = self.data
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
    
    def save(self) -> None:
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Configuration saved to {self.config_path}")


class ConfigManager:
    """Manages Cleudocode configuration"""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".cleudocode"
    DEFAULT_CONFIG_FILE = "config.yaml"
    DEFAULT_TOKEN_FILE = ".gateway_token"
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager"""
        self.config_dir = config_dir or self.DEFAULT_CONFIG_DIR
        self.config_path = self.config_dir / self.DEFAULT_CONFIG_FILE
        self.token_path = self.config_dir / self.DEFAULT_TOKEN_FILE
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self._create_subdirectories()
    
    def _create_subdirectories(self) -> None:
        """Create necessary subdirectories"""
        subdirs = ['workspace', 'memory', 'skills', 'logs', 'cache', 'browser_data']
        for subdir in subdirs:
            (self.config_dir / subdir).mkdir(exist_ok=True)
    
    def _expand_env_vars(self, data: Any) -> Any:
        """Recursively expand environment variables in config"""
        if isinstance(data, dict):
            return {k: self._expand_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._expand_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith('${') and data.endswith('}'):
            env_var = data[2:-1]
            return os.getenv(env_var, data)
        return data
    
    def load_config(self) -> CleudocodeConfig:
        """Load configuration from file"""
        if not self.config_path.exists():
            logger.warning(f"Config file not found at {self.config_path}, creating default")
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Expand environment variables
            data = self._expand_env_vars(data)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return CleudocodeConfig(config_path=self.config_path, data=data)
        
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def _create_default_config(self) -> CleudocodeConfig:
        """Create default configuration"""
        # Try to load from project directory first
        project_config = Path(__file__).parent.parent / ".cleudocode" / "config.yaml"
        
        if project_config.exists():
            with open(project_config, 'r') as f:
                data = yaml.safe_load(f)
        else:
            # Fallback to minimal config
            data = {
                'system': {
                    'name': 'Cleudocode',
                    'version': '1.0.0'
                },
                'gateway': {
                    'host': '0.0.0.0',
                    'port': 18900,
                    'enable_auth': True
                },
                'llm': {
                    'default_provider': 'google-antigravity',
                    'default_model': 'gemini-1.5-flash'
                }
            }
        
        config = CleudocodeConfig(config_path=self.config_path, data=data)
        config.save()
        
        return config
    
    def get_or_create_token(self) -> str:
        """Get existing token or create a new one"""
        if self.token_path.exists():
            with open(self.token_path, 'r') as f:
                token = f.read().strip()
                if token:
                    return token
        
        # Generate new token
        token = str(uuid.uuid4())
        
        with open(self.token_path, 'w') as f:
            f.write(token)
        
        # Set restrictive permissions (Unix only)
        try:
            os.chmod(self.token_path, 0o600)
        except:
            pass
        
        logger.info(f"New gateway token generated: {token[:8]}...")
        return token
    
    def validate_token(self, token: str) -> bool:
        """Validate a token against the stored token"""
        stored_token = self.get_or_create_token()
        return token == stored_token
    
    def reset_token(self) -> str:
        """Generate a new token"""
        if self.token_path.exists():
            self.token_path.unlink()
        
        return self.get_or_create_token()
    
    def get_workspace_dir(self) -> Path:
        """Get workspace directory"""
        return self.config_dir / "workspace"
    
    def get_memory_dir(self) -> Path:
        """Get memory directory"""
        return self.config_dir / "memory"
    
    def get_skills_dir(self) -> Path:
        """Get skills directory"""
        return self.config_dir / "skills"
    
    def get_logs_dir(self) -> Path:
        """Get logs directory"""
        return self.config_dir / "logs"


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> CleudocodeConfig:
    """Get current configuration"""
    return get_config_manager().load_config()


def get_token() -> str:
    """Get gateway token"""
    return get_config_manager().get_or_create_token()


if __name__ == "__main__":
    # Test configuration
    logging.basicConfig(level=logging.INFO)
    
    manager = ConfigManager()
    config = manager.load_config()
    
    print(f"System Name: {config.get('system.name')}")
    print(f"Gateway Port: {config.get('gateway.port')}")
    print(f"LLM Provider: {config.get('llm.default_provider')}")
    print(f"Gateway Token: {manager.get_or_create_token()[:8]}...")
