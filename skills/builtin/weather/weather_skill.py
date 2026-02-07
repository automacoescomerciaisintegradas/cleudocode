"""
Weather Skill para Cleudocode
Obtém previsão do tempo usando wttr.in (sem API key)
"""

import subprocess
import json
import urllib.parse
from typing import Optional, Dict, Any
import sys
sys.path.insert(0, str(__file__).split('skills')[0])

from skills.base import BaseSkill


class WeatherSkill(BaseSkill):
    """Skill para consulta de previsão do tempo."""
    
    def __init__(self):
        super().__init__(
            name="weather",
            description="Obtém previsão do tempo atual e forecast (sem API key necessária)."
        )
    
    def execute(self, params: str) -> str:
        """Executa a skill com os parâmetros fornecidos."""
        # Parse básico dos parâmetros
        action = "current"
        location = "São Paulo"
        format_type = "text"
        days = 1
        
        # Parse simples de parâmetros
        parts = params.strip().split()
        for i, part in enumerate(parts):
            if part.startswith("action:"):
                action = part.split(":")[1]
            elif part.startswith("location:"):
                # Pega tudo após location: até o próximo parâmetro
                location = part.split(":", 1)[1].strip('"\'')
            elif part.startswith("format:"):
                format_type = part.split(":")[1]
            elif part.startswith("days:"):
                days = int(part.split(":")[1])
        
        if action == "current":
            return self._get_current_weather(location, format_type)
        elif action == "forecast":
            return self._get_forecast(location, days)
        else:
            return f"Ação desconhecida: {action}. Use 'current' ou 'forecast'."
    
    def _get_current_weather(self, location: str, format_type: str = "text") -> str:
        """Obtém o tempo atual para uma localização."""
        encoded_location = urllib.parse.quote(location)
        
        if format_type == "json":
            url = f"wttr.in/{encoded_location}?format=j1"
        else:
            url = f"wttr.in/{encoded_location}?format=%l:+%c+%t+%h+%w"
        
        try:
            result = subprocess.run(
                ["curl", "-s", url],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Erro ao consultar tempo: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Timeout ao consultar serviço de tempo."
        except Exception as e:
            return f"Erro: {str(e)}"
    
    def _get_forecast(self, location: str, days: int = 3) -> str:
        """Obtém forecast para os próximos dias."""
        encoded_location = urllib.parse.quote(location)
        url = f"wttr.in/{encoded_location}?{days}T"
        
        try:
            result = subprocess.run(
                ["curl", "-s", url],
                capture_output=True,
                text=True,
                timeout=15,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Erro ao consultar forecast: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Timeout ao consultar serviço de tempo."
        except Exception as e:
            return f"Erro: {str(e)}"
    
    def get_tools(self) -> list:
        """Retorna lista de ferramentas disponíveis para o LLM."""
        return [
            {
                "name": "weather_current",
                "description": "Obtém o tempo atual para uma localização",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "Nome da cidade ou localização",
                        "required": True
                    },
                    "format": {
                        "type": "string",
                        "description": "Formato de saída: 'text' ou 'json'",
                        "default": "text"
                    }
                }
            },
            {
                "name": "weather_forecast",
                "description": "Obtém previsão do tempo para os próximos dias",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "Nome da cidade ou localização",
                        "required": True
                    },
                    "days": {
                        "type": "integer",
                        "description": "Número de dias para o forecast (1-3)",
                        "default": 3
                    }
                }
            }
        ]
    
    def get_definition(self) -> str:
        """Retorna a definição XML/Prompt para o LLM saber como usar."""
        return f"""<tool_definition>
<name>{self.name}</name>
<emoji>{self.metadata.emoji}</emoji>
<description>{self.description}</description>
<usage>
<tool code="weather">
action:current location:"São Paulo"
</tool>

<tool code="weather">
action:forecast location:"Rio de Janeiro" days:3
</tool>
</usage>
<examples>
- Tempo atual: weather action:current location:"Brasilia"
- Forecast: weather action:forecast location:"Curitiba" days:2
- JSON: weather action:current location:"Recife" format:json
</examples>
</tool_definition>"""


# Para testes diretos
if __name__ == "__main__":
    skill = WeatherSkill()
    print(skill.get_definition())
    print("\n--- Teste: Tempo atual em São Paulo ---")
    print(skill.execute('action:current location:"São Paulo"'))
