"""
Configuração temporária para os workflows
"""
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

class Settings:
    def __init__(self):
        self._settings = {}
        
    def get(self, key, default=None):
        """Obtém uma configuração do ambiente ou retorna default"""
        return os.getenv(key, default)
    
    def set(self, key, value):
        """Define uma configuração"""
        self._settings[key] = value
        
    def __getitem__(self, key):
        return self.get(key)

    def __getattr__(self, name):
        """Permite acessar variáveis de ambiente como atributos"""
        val = self.get(name)
        if val is None:
             # Retorna None em vez de erro para não quebrar scripts de descoberta
             return None
        return val

# Instância global
settings = Settings()