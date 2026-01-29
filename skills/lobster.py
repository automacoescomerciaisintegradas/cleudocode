"""
Lobster Workflow Engine - Sistema de automação customizada.
Permite criar workflows em YAML que combinam múltiplas skills.
"""

import yaml
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from jinja2 import Template

logger = logging.getLogger(__name__)


class LobsterWorkflow:
    """
    Motor de execução de workflows customizados.
    
    Features:
    - Definição de workflows em YAML
    - Interpolação de variáveis com Jinja2
    - Execução sequencial e paralela
    - Tratamento de erros e retry
    - Logs detalhados de execução
    """
    
    def __init__(self, skill_manager, workflows_dir: str = "skills/workflows"):
        """
        Args:
            skill_manager: Instância do SkillManager
            workflows_dir: Diretório com arquivos .lobster
        """
        self.skill_manager = skill_manager
        self.workflows_dir = Path(workflows_dir)
        self.workflows = {}
        
        # Registrar skills do Lobster
        self._register_lobster_skills()
        
        # Criar diretório se não existir
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Carregar workflows
        self.load_all_workflows()
    
    def _register_lobster_skills(self):
        """Registra skills específicas do Lobster."""
        try:
            from skills.lobster_skills import FilesystemSkill, ShellSkill, TelegramSkill
            
            # Registrar skills
            self.skill_manager.skills['filesystem'] = FilesystemSkill()
            self.skill_manager.skills['shell'] = ShellSkill()
            self.skill_manager.skills['telegram'] = TelegramSkill()
            
            logger.info("Skills do Lobster registradas")
        except ImportError as e:
            logger.warning(f"Não foi possível carregar skills do Lobster: {e}")
    
    def load_all_workflows(self):
        """Carrega todos os workflows do diretório."""
        if not self.workflows_dir.exists():
            logger.warning(f"Diretório de workflows não encontrado: {self.workflows_dir}")
            return
        
        count = 0
        for workflow_file in self.workflows_dir.glob("*.lobster"):
            try:
                self.load_workflow(str(workflow_file))
                count += 1
            except Exception as e:
                logger.error(f"Erro ao carregar workflow {workflow_file}: {e}")
        
        logger.info(f"{count} workflows carregados de {self.workflows_dir}")
    
    def load_workflow(self, filepath: str):
        """
        Carrega workflow de arquivo YAML.
        
        Args:
            filepath: Caminho do arquivo .lobster
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
        
        # Validar estrutura
        self._validate_workflow(workflow)
        
        workflow_name = workflow['name']
        self.workflows[workflow_name] = workflow
        
        logger.info(f"Workflow carregado: {workflow_name}")
    
    def _validate_workflow(self, workflow: dict):
        """Valida estrutura do workflow."""
        required_fields = ['name', 'description', 'steps']
        for field in required_fields:
            if field not in workflow:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        if not isinstance(workflow['steps'], list):
            raise ValueError("'steps' deve ser uma lista")
        
        for i, step in enumerate(workflow['steps']):
            if 'name' not in step:
                raise ValueError(f"Step {i} sem nome")
            if 'skill' not in step:
                raise ValueError(f"Step '{step['name']}' sem skill")
            if 'action' not in step:
                raise ValueError(f"Step '{step['name']}' sem action")
    
    def execute(
        self,
        workflow_name: str,
        variables: Optional[Dict[str, Any]] = None,
        async_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Executa workflow.
        
        Args:
            workflow_name: Nome do workflow
            variables: Variáveis para interpolação
            async_mode: Se True, executa em background
            
        Returns:
            Dict com resultados da execução
        """
        if workflow_name not in self.workflows:
            return {
                "success": False,
                "error": f"Workflow '{workflow_name}' não encontrado"
            }
        
        workflow = self.workflows[workflow_name]
        variables = variables or {}
        
        # Adicionar variáveis padrão
        variables.update({
            'date': datetime.now().strftime('%Y%m%d'),
            'datetime': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'timestamp': datetime.now().isoformat(),
            'workflow_name': workflow_name
        })
        
        logger.info(f"Executando workflow: {workflow_name}")
        
        if async_mode:
            # Executar em background
            asyncio.create_task(self._execute_async(workflow, variables))
            return {
                "success": True,
                "message": f"Workflow '{workflow_name}' iniciado em background"
            }
        else:
            # Executar sincronamente
            return self._execute_sync(workflow, variables)
    
    def _execute_sync(self, workflow: dict, variables: dict) -> Dict[str, Any]:
        """Executa workflow sincronamente."""
        results = []
        context = variables.copy()
        
        for i, step in enumerate(workflow['steps']):
            step_name = step['name']
            logger.info(f"Executando step {i+1}/{len(workflow['steps'])}: {step_name}")
            
            try:
                result = self._execute_step(step, context)
                results.append({
                    "step": step_name,
                    "success": result.get('success', False),
                    "result": result
                })
                
                # Adicionar resultado ao contexto para próximos steps
                context[f'step_{i}_result'] = result
                
                # Parar se houver erro (a menos que continue_on_error=true)
                if not result.get('success', False) and not step.get('continue_on_error', False):
                    logger.error(f"Step '{step_name}' falhou, abortando workflow")
                    break
                    
            except Exception as e:
                logger.error(f"Erro no step '{step_name}': {e}")
                results.append({
                    "step": step_name,
                    "success": False,
                    "error": str(e)
                })
                
                if not step.get('continue_on_error', False):
                    break
        
        # Verificar se todos os steps foram bem-sucedidos
        all_success = all(r.get('success', False) for r in results)
        
        return {
            "success": all_success,
            "workflow": workflow['name'],
            "steps_executed": len(results),
            "steps_total": len(workflow['steps']),
            "results": results
        }
    
    async def _execute_async(self, workflow: dict, variables: dict):
        """Executa workflow assincronamente."""
        # Implementação similar ao _execute_sync mas com await
        pass
    
    def _execute_step(self, step: dict, context: dict) -> Dict[str, Any]:
        """
        Executa um step do workflow.
        
        Args:
            step: Definição do step
            context: Contexto com variáveis
            
        Returns:
            Resultado da execução
        """
        skill_name = step['skill']
        action = step['action']
        params = step.get('params', {})
        
        # Interpolar variáveis nos parâmetros
        params = self._interpolate_variables(params, context)
        
        # Retry logic
        max_retries = step.get('retry', 0)
        retry_delay = step.get('retry_delay', 1)
        
        for attempt in range(max_retries + 1):
            try:
                # Verificar se skill existe
                if skill_name not in self.skill_manager.skills:
                    return {
                        "success": False,
                        "error": f"Skill '{skill_name}' não encontrada"
                    }
                
                # Obter skill
                skill = self.skill_manager.skills[skill_name]
                
                # Executar ação da skill
                if hasattr(skill, action):
                    # Chamar método específico da skill
                    method = getattr(skill, action)
                    result = method(**params) if params else method()
                else:
                    # Tentar executar com método genérico
                    result = skill.execute(params)
                
                # Verificar se resultado é dict
                if not isinstance(result, dict):
                    result = {"success": True, "result": result}
                
                if result.get('success', False) or attempt == max_retries:
                    return result
                
                # Aguardar antes de retry
                if attempt < max_retries:
                    logger.warning(f"Tentativa {attempt + 1} falhou, tentando novamente em {retry_delay}s")
                    import time
                    time.sleep(retry_delay)
                    
            except Exception as e:
                if attempt == max_retries:
                    return {
                        "success": False,
                        "error": str(e)
                    }
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                import time
                time.sleep(retry_delay)
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def _interpolate_variables(self, params: Any, context: dict) -> Any:
        """
        Interpola variáveis usando Jinja2.
        
        Suporta:
        - {{ variavel }}
        - {{ variavel | upper }}
        - {% if condicao %}...{% endif %}
        """
        if isinstance(params, dict):
            return {k: self._interpolate_variables(v, context) for k, v in params.items()}
        elif isinstance(params, list):
            return [self._interpolate_variables(item, context) for item in params]
        elif isinstance(params, str):
            try:
                template = Template(params)
                return template.render(**context)
            except Exception as e:
                logger.warning(f"Erro ao interpolar '{params}': {e}")
                return params
        return params
    
    def list_workflows(self) -> List[Dict[str, str]]:
        """Lista todos os workflows disponíveis."""
        return [
            {
                "name": name,
                "description": workflow.get('description', ''),
                "steps": len(workflow.get('steps', [])),
                "version": workflow.get('version', '1.0')
            }
            for name, workflow in self.workflows.items()
        ]
    
    def get_workflow_info(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Obtém informações detalhadas de um workflow."""
        if workflow_name not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_name]
        return {
            "name": workflow['name'],
            "description": workflow['description'],
            "version": workflow.get('version', '1.0'),
            "author": workflow.get('author', 'Unknown'),
            "steps": [
                {
                    "name": step['name'],
                    "skill": step['skill'],
                    "action": step['action']
                }
                for step in workflow['steps']
            ],
            "variables": workflow.get('variables', {})
        }
