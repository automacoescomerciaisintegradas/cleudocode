from abc import ABC, abstractmethod

class BaseSkill(ABC):
    """
    Classe base para todas as habilidades (Tools) do agente.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, params: str) -> str:
        """
        Executa a skill com os parametros fornecidos (geralmente string crua do XML).
        Retorna o resultado como string.
        """
        pass

    def get_definition(self) -> str:
        """
        Retorna a definição XML/Prompt para o LLM saber como usar.
        """
        return f"""<tool_definition>
<name>{self.name}</name>
<description>{self.description}</description>
<usage>
<tool code="{self.name}">
[argumentos]
</tool>
</usage>
</tool_definition>"""
