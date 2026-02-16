"""
Pipeline de desenvolvimento completo integrando todos os agentes especializados.
"""
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm_providers import llm_hub
from core.secure_executor import secure_executor


class DevelopmentPipeline:
    """
    Pipeline completo de desenvolvimento de software com agentes especializados.
    """
    
    def __init__(self):
        self.executor = secure_executor
        # Carregar personas dos agentes
        self.agent_personas = self._load_agent_personas()
    
    def _load_agent_personas(self) -> Dict[str, str]:
        """Carrega as personas dos agentes a partir dos arquivos MD."""
        personas = {}
        agents_dir = Path(__file__).parent.parent / "agents"
        
        agent_files = {
            "code-producer": "code-producer.md",
            "code-executor": "code-executor.md", 
            "security-auditor": "security-auditor.md",
            "performance-optimizer": "performance-optimizer.md"
        }
        
        for agent_name, filename in agent_files.items():
            file_path = agents_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        personas[agent_name] = f.read()
                except Exception as e:
                    print(f"Erro ao carregar persona do agente {agent_name}: {e}")
        
        return personas
    
    def execute_pipeline(self, requirements: str, 
                        languages: List[str] = ['python'],
                        security_check: bool = True,
                        performance_optimization: bool = True) -> Dict[str, Any]:
        """
        Executa o pipeline completo de desenvolvimento.
        
        Args:
            requirements: Requisitos do software a ser desenvolvido
            languages: Linguagens a serem usadas
            security_check: Se deve realizar auditoria de segurança
            performance_optimization: Se deve otimizar performance
        
        Returns:
            Dicionário com resultado completo do pipeline
        """
        result = {
            'status': 'started',
            'steps': {},
            'final_artifact': None,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Etapa 1: Produção de código
            result['steps']['code_production'] = self._produce_code(requirements, languages)
            
            if not result['steps']['code_production']['success']:
                result['status'] = 'failed_at_code_production'
                return result
            
            # Etapa 2: Validação de segurança (se solicitado)
            if security_check:
                result['steps']['security_audit'] = self._audit_security(
                    result['steps']['code_production']['code'], 
                    result['steps']['code_production']['language']
                )
                
                if not result['steps']['security_audit']['passed']:
                    result['issues'].extend(result['steps']['security_audit']['issues'])
            
            # Etapa 3: Otimização de performance (se solicitado)
            if performance_optimization:
                result['steps']['performance_optimization'] = self._optimize_performance(
                    result['steps']['code_production']['code'],
                    result['steps']['code_production']['language']
                )
                
                # Atualizar código com versão otimizada se bem sucedido
                if result['steps']['performance_optimization']['success']:
                    result['steps']['code_production']['code'] = result['steps']['performance_optimization']['optimized_code']
            
            # Etapa 4: Execução e teste
            result['steps']['execution'] = self._execute_and_test(
                result['steps']['code_production']['code'],
                result['steps']['code_production']['language']
            )
            
            # Etapa 5: Compilar resultado final
            result['status'] = 'completed' if result['steps']['execution']['success'] else 'completed_with_issues'
            result['final_artifact'] = {
                'code': result['steps']['code_production']['code'],
                'language': result['steps']['code_production']['language'],
                'execution_result': result['steps']['execution']
            }
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def _produce_code(self, requirements: str, languages: List[str]) -> Dict[str, Any]:
        """Produz código com base nos requisitos usando o agente de produção."""
        try:
            # Determinar linguagem principal
            primary_language = languages[0] if languages else 'python'
            
            # Preparar prompt para o agente de produção de código
            prompt = f"""
            Com base nos seguintes requisitos, gere código completo e funcional em {primary_language}:

            REQUISITOS:
            {requirements}

            INSTRUÇÕES:
            - Forneça código completo e executável
            - Inclua tratamento de erros adequado
            - Siga as melhores práticas da linguagem
            - Adicione comentários explicativos onde apropriado
            - Certifique-se de que o código seja seguro e eficiente
            """
            
            # Obter a persona do agente de produção de código
            system_prompt = self.agent_personas.get("code-producer", "Você é um assistente de programação.")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Gerar código usando o LLM
            code = llm_hub.query(messages=messages)
            
            return {
                'success': True,
                'code': code,
                'language': primary_language,
                'details': 'Código gerado com sucesso'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'code': None,
                'language': None
            }
    
    def _audit_security(self, code: str, language: str) -> Dict[str, Any]:
        """Realiza auditoria de segurança no código usando o agente de segurança."""
        try:
            # Preparar prompt para o agente de auditoria de segurança
            prompt = f"""
            Realize uma auditoria de segurança completa no seguinte código {language}:

            CÓDIGO:
            {code}

            INSTRUÇÕES:
            - Identifique todas as vulnerabilidades de segurança
            - Classifique por severidade (crítico, alto, médio, baixo)
            - Liste padrões inseguros ou más práticas
            - Forneça recomendações específicas para correção
            - Verifique conformidade com OWASP Top 10
            """
            
            # Obter a persona do agente de auditoria de segurança
            system_prompt = self.agent_personas.get("security-auditor", "Você é um especialista em segurança de aplicações.")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Obter análise de segurança
            security_analysis = llm_hub.query(messages=messages)
            
            # Simular análise de risco (em implementação real, isso seria mais elaborado)
            risk_level = "low" if "vulnerability" not in security_analysis.lower() else "medium"
            
            return {
                'passed': risk_level == 'low',
                'issues': [{"type": "security_issue", "description": security_analysis}],
                'risk_level': risk_level,
                'report': security_analysis
            }
        except Exception as e:
            return {
                'passed': False,
                'issues': [{'type': 'audit_error', 'description': str(e)}],
                'risk_level': 'unknown',
                'error': str(e)
            }
    
    def _optimize_performance(self, code: str, language: str) -> Dict[str, Any]:
        """Otimiza o código para performance usando o agente de otimização."""
        try:
            # Preparar prompt para o agente de otimização de performance
            prompt = f"""
            Otimizar o seguinte código {language} para melhor desempenho:

            CÓDIGO ORIGINAL:
            {code}

            INSTRUÇÕES:
            - Identifique gargalos de performance
            - Otimizar algoritmos e estruturas de dados
            - Melhorar eficiência de operações de I/O
            - Reduzir uso de memória quando possível
            - Manter funcionalidade e legibilidade
            - Forneça código otimizado e explicações
            """
            
            # Obter a persona do agente de otimização de performance
            system_prompt = self.agent_personas.get("performance-optimizer", "Você é um especialista em otimização de performance.")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Obter código otimizado
            optimized_result = llm_hub.query(messages=messages)
            
            # Extrair código otimizado (em implementação real, isso seria mais robusto)
            optimized_code = optimized_result
            
            return {
                'success': True,
                'optimized_code': optimized_code,
                'improvements': ["Otimização realizada pelo agente de performance"],
                'original_code': code
            }
        except Exception as e:
            return {
                'success': False,
                'optimized_code': code,  # Retornar código original em caso de erro
                'error': str(e),
                'improvements': [],
                'optimization_failed': True
            }
    
    def _execute_and_test(self, code: str, language: str) -> Dict[str, Any]:
        """Executa e testa o código em ambiente seguro."""
        try:
            # Primeiro validar o código
            validation = self.executor.validate_code(code, language)
            
            if not validation['valid']:
                return {
                    'success': False,
                    'validation_errors': validation['errors'],
                    'validation_warnings': validation['warnings'],
                    'stdout': '',
                    'stderr': 'Código não passou na validação de segurança'
                }
            
            # Executar o código
            execution_result = self.executor.execute_code(code, language)
            
            return {
                'success': execution_result['success'],
                'stdout': execution_result.get('stdout', ''),
                'stderr': execution_result.get('stderr', ''),
                'return_code': execution_result.get('return_code', -1),
                'execution_time': execution_result.get('execution_time', 0)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': str(e)
            }


# Instância global do pipeline
development_pipeline = DevelopmentPipeline()