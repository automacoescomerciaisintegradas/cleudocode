import logging
import re
from typing import Dict
from skills.base import BaseSkill
from skills.shell import ShellSkill
from skills.filesystem import FileReadSkill, FileWriteSkill
from skills.telegram_utils import TelegramLookupSkill

logger = logging.getLogger(__name__)

class SkillManager:
    """
    Gerencia o registro e a execução de Skills.
    """
    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}
        self._register_defaults()
        
    def _register_defaults(self):
        self.register(ShellSkill())
        self.register(FileReadSkill())
        self.register(FileWriteSkill())
        self.register(TelegramLookupSkill())
        
    def register(self, skill: BaseSkill):
        self.skills[skill.name] = skill
        
    def get_all_definitions(self) -> str:
        """Gera o texto de ajuda para o System Prompt"""
        defs = [s.get_definition() for s in self.skills.values()]
        return "\n\n".join(defs)

    def parse_and_execute(self, llm_response: str) -> str:
        """
        Analisa a resposta do LLM, busca tags <tool code="..."> e executa.
        Retorna o log de execução ou None se nada foi executado.
        """
        pattern = r'<tool code="([^"]+)">\s*(.*?)\s*</tool>'
        matches = re.finditer(pattern, llm_response, re.DOTALL)
        
        log = []
        found = False
        
        for match in matches:
            found = True
            tool_name = match.group(1)
            params = match.group(2)
            
            if tool_name in self.skills:
                logger.info(f"Invoking skill: {tool_name}")
                result = self.skills[tool_name].execute(params)
                log_entry = f"--- Tool Execution: {tool_name} ---\n{result}\n"
                log.append(log_entry)
            else:
                log.append(f"Erro: Ferramenta '{tool_name}' não reconhecida.")
                
        return "\n".join(log) if found else None
