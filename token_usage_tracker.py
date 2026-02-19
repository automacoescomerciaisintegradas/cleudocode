"""Token Usage Tracker - Simples módulo para rastrear uso de tokens e quotas."""

import os
import json
from datetime import datetime, timedelta


class TokenUsageTracker:
    """Rastreador de uso de tokens para diferentes modelos e provedores."""
    
    def __init__(self):
        self.usage_data = {}
        self.daily_limits = {}
        self.load_usage()

    def load_usage(self):
        """Carrega dados de uso de um arquivo JSON."""
        try:
            usage_file = os.path.join(os.path.dirname(__file__), 'logs', 'token_usage.json')
            if os.path.exists(usage_file):
                with open(usage_file, 'r') as f:
                    self.usage_data = json.load(f)
        except Exception:
            self.usage_data = {}

    def record_usage(self, model, tokens):
        """Registra o uso de tokens para um modelo específico."""
        if model not in self.usage_data:
            self.usage_data[model] = {
                'today': str(datetime.now().date()),
                'used_tokens': 0,
                'requests_count': 0
            }
        
        self.usage_data[model]['used_tokens'] += tokens
        self.usage_data[model]['requests_count'] += 1
        
        # Salva os dados atualizados
        self.save_usage()

    def is_rate_limited(self, model):
        """Verifica se o modelo está sob limite de taxa."""
        # Por enquanto, não impõe limites rígidos, apenas verifica se há dados
        today = str(datetime.now().date())
        if model in self.usage_data:
            model_data = self.usage_data[model]
            if model_data['today'] != today:
                # Reset daily counter
                model_data['today'] = today
                model_data['used_tokens'] = 0
                model_data['requests_count'] = 0
        
        return False  # Não impõe limites por enquanto

    def save_usage(self):
        """Salva os dados de uso em arquivo JSON."""
        try:
            logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            
            usage_file = os.path.join(logs_dir, 'token_usage.json')
            with open(usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Erro ao salvar dados de uso: {e}")


def create_quota_exceeded_message(model, tracker):
    """Cria uma mensagem quando a cota é excedida."""
    return f"Limite de uso do modelo {model} atingido. Por favor, verifique sua cota de tokens."