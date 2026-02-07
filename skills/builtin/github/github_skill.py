"""
GitHub Skill para Cleudocode
============================

Interage com o GitHub usando a CLI `gh`.
Suporta issues, PRs, CI/CD status e queries avançadas.

Autor: Cleudocode Team
Data: 02/02/2026
"""

import subprocess
import json
import re
from typing import Dict, Any, List, Optional
import logging

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.base import BaseSkill

logger = logging.getLogger(__name__)


class GitHubSkill(BaseSkill):
    """
    Skill para interação com o GitHub via CLI `gh`.
    
    Funcionalidades:
    - Listar e gerenciar issues
    - Listar e gerenciar PRs
    - Verificar status de CI/CD
    - Queries avançadas via API
    """
    
    def __init__(self):
        super().__init__(
            name="github",
            description="Interage com o GitHub usando a CLI `gh`. Use para issues, PRs, CI runs e queries avançadas."
        )
    
    def execute(self, params: str) -> str:
        """
        Executa a skill com os parâmetros fornecidos.
        
        Formato: action:<action> [repo:<owner/repo>] [outros params]
        
        Actions:
        - issue_list: Lista issues
        - issue_create: Cria issue
        - issue_close: Fecha issue
        - pr_list: Lista PRs
        - pr_checks: Verifica CI de um PR
        - run_list: Lista workflow runs
        - run_view: Visualiza detalhes de um run
        - api: Query direta à API
        - auth_status: Verifica autenticação
        """
        # Parse dos parâmetros
        parsed = self._parse_params(params)
        action = parsed.get('action', 'issue_list')
        repo = parsed.get('repo', '')
        
        try:
            if action == 'auth_status':
                return self._auth_status()
            elif action == 'issue_list':
                return self._issue_list(repo, parsed.get('state', 'open'), parsed.get('limit', '10'))
            elif action == 'issue_create':
                return self._issue_create(repo, parsed.get('title', ''), parsed.get('body', ''))
            elif action == 'issue_close':
                return self._issue_close(repo, parsed.get('number', ''))
            elif action == 'pr_list':
                return self._pr_list(repo, parsed.get('state', 'open'), parsed.get('limit', '10'))
            elif action == 'pr_checks':
                return self._pr_checks(repo, parsed.get('pr', parsed.get('number', '')))
            elif action == 'run_list':
                return self._run_list(repo, parsed.get('limit', '10'))
            elif action == 'run_view':
                return self._run_view(repo, parsed.get('run_id', ''))
            elif action == 'api':
                return self._api_query(parsed.get('endpoint', ''), parsed.get('jq', ''))
            else:
                return f"Ação desconhecida: {action}. Use: issue_list, issue_create, pr_list, pr_checks, run_list, api"
        except Exception as e:
            return f"Erro ao executar GitHub skill: {str(e)}"
    
    def _parse_params(self, params: str) -> Dict[str, str]:
        """Parse de parâmetros no formato key:value."""
        result = {}
        # Regex para capturar key:value (suporta valores com aspas)
        pattern = r'(\w+):(?:"([^"]+)"|([^\s]+))'
        matches = re.findall(pattern, params)
        for key, quoted_val, simple_val in matches:
            result[key] = quoted_val if quoted_val else simple_val
        return result
    
    def _run_gh(self, args: List[str], timeout: int = 30) -> str:
        """Executa comando gh e retorna output."""
        cmd = ['gh'] + args
        logger.debug(f"Executando: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"gh falhou: {error_msg}")
        
        return result.stdout.strip()
    
    def _auth_status(self) -> str:
        """Verifica status de autenticação."""
        try:
            output = self._run_gh(['auth', 'status'])
            return f"✅ Autenticado:\n{output}"
        except RuntimeError as e:
            return f"❌ Não autenticado: {e}\n\nExecute: gh auth login"
    
    def _issue_list(self, repo: str, state: str, limit: str) -> str:
        """Lista issues."""
        args = ['issue', 'list', '--state', state, '--limit', limit]
        if repo:
            args.extend(['--repo', repo])
        
        # Formato JSON para melhor parsing
        args.extend(['--json', 'number,title,state,author', '--jq', '.[] | "\\(.number): [\\(.state)] \\(.title) (@\\(.author.login))"'])
        
        output = self._run_gh(args)
        if not output:
            return f"Nenhuma issue encontrada (state={state})"
        return f"📋 Issues ({state}):\n{output}"
    
    def _issue_create(self, repo: str, title: str, body: str) -> str:
        """Cria uma issue."""
        if not title:
            return "❌ Título é obrigatório. Use: title:\"Seu título\""
        
        args = ['issue', 'create', '--title', title]
        if body:
            args.extend(['--body', body])
        if repo:
            args.extend(['--repo', repo])
        
        output = self._run_gh(args)
        return f"✅ Issue criada: {output}"
    
    def _issue_close(self, repo: str, number: str) -> str:
        """Fecha uma issue."""
        if not number:
            return "❌ Número da issue é obrigatório. Use: number:123"
        
        args = ['issue', 'close', number]
        if repo:
            args.extend(['--repo', repo])
        
        output = self._run_gh(args)
        return f"✅ Issue #{number} fechada: {output}"
    
    def _pr_list(self, repo: str, state: str, limit: str) -> str:
        """Lista PRs."""
        args = ['pr', 'list', '--state', state, '--limit', limit]
        if repo:
            args.extend(['--repo', repo])
        
        args.extend(['--json', 'number,title,state,author,headRefName', 
                     '--jq', '.[] | "\\(.number): [\\(.state)] \\(.title) (\\(.headRefName)) @\\(.author.login)"'])
        
        output = self._run_gh(args)
        if not output:
            return f"Nenhum PR encontrado (state={state})"
        return f"🔀 Pull Requests ({state}):\n{output}"
    
    def _pr_checks(self, repo: str, pr_number: str) -> str:
        """Verifica status de CI de um PR."""
        if not pr_number:
            return "❌ Número do PR é obrigatório. Use: pr:55"
        
        args = ['pr', 'checks', pr_number]
        if repo:
            args.extend(['--repo', repo])
        
        output = self._run_gh(args)
        return f"🔍 CI Status do PR #{pr_number}:\n{output}"
    
    def _run_list(self, repo: str, limit: str) -> str:
        """Lista workflow runs."""
        args = ['run', 'list', '--limit', limit]
        if repo:
            args.extend(['--repo', repo])
        
        output = self._run_gh(args)
        return f"🏃 Workflow Runs:\n{output}"
    
    def _run_view(self, repo: str, run_id: str) -> str:
        """Visualiza detalhes de um run."""
        if not run_id:
            return "❌ ID do run é obrigatório. Use: run_id:123456"
        
        args = ['run', 'view', run_id]
        if repo:
            args.extend(['--repo', repo])
        
        output = self._run_gh(args)
        return f"📊 Detalhes do Run #{run_id}:\n{output}"
    
    def _api_query(self, endpoint: str, jq_filter: str) -> str:
        """Executa query direta à API."""
        if not endpoint:
            return "❌ Endpoint é obrigatório. Use: endpoint:repos/owner/repo/issues"
        
        args = ['api', endpoint]
        if jq_filter:
            args.extend(['--jq', jq_filter])
        
        output = self._run_gh(args)
        return f"🔗 API Response:\n{output}"
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna lista de ferramentas disponíveis para o LLM."""
        return [
            {
                "name": "github_issue_list",
                "description": "Lista issues de um repositório",
                "parameters": {
                    "repo": {"type": "string", "description": "Repositório no formato owner/repo"},
                    "state": {"type": "string", "description": "Estado: open, closed, all", "default": "open"},
                    "limit": {"type": "integer", "description": "Número máximo de resultados", "default": 10}
                }
            },
            {
                "name": "github_pr_checks",
                "description": "Verifica status de CI/CD de um PR",
                "parameters": {
                    "repo": {"type": "string", "description": "Repositório no formato owner/repo", "required": True},
                    "pr": {"type": "integer", "description": "Número do PR", "required": True}
                }
            },
            {
                "name": "github_api",
                "description": "Query direta à API do GitHub",
                "parameters": {
                    "endpoint": {"type": "string", "description": "Endpoint da API", "required": True},
                    "jq": {"type": "string", "description": "Filtro JQ opcional"}
                }
            }
        ]
    
    def get_definition(self) -> str:
        """Retorna definição para o LLM."""
        return f"""<tool_definition>
<name>{self.name}</name>
<emoji>{self.metadata.emoji}</emoji>
<description>{self.description}</description>
<available>{self.is_available()}</available>
<usage>
<tool code="github">
action:issue_list repo:owner/repo state:open limit:10
</tool>

<tool code="github">
action:pr_checks repo:owner/repo pr:55
</tool>

<tool code="github">
action:issue_create repo:owner/repo title:"Bug encontrado" body:"Descrição do bug"
</tool>

<tool code="github">
action:api endpoint:repos/owner/repo/releases jq:".[].tag_name"
</tool>
</usage>
<actions>
- auth_status: Verifica autenticação
- issue_list: Lista issues
- issue_create: Cria issue
- issue_close: Fecha issue
- pr_list: Lista PRs
- pr_checks: Verifica CI de um PR
- run_list: Lista workflow runs
- run_view: Detalhes de um run
- api: Query direta à API
</actions>
</tool_definition>"""


# Para testes diretos
if __name__ == "__main__":
    skill = GitHubSkill()
    print(skill.get_definition())
    print("\n--- Teste: Auth Status ---")
    print(skill.execute('action:auth_status'))
