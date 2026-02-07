"""
Coding Agent Skill para Cleudocode
==================================

Executa agentes de código (Codex CLI, Claude Code, Pi) via processo 
em background para controle programático.

IMPORTANTE: Agentes de código são aplicações de terminal interativas
que precisam de PTY para funcionar corretamente.

Autor: Cleudocode Team
Data: 02/02/2026
"""

import subprocess
import os
import signal
import threading
import time
import uuid
import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import logging

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.base import BaseSkill

logger = logging.getLogger(__name__)


@dataclass
class AgentSession:
    """Representa uma sessão de agente em execução."""
    session_id: str
    agent: str
    prompt: str
    workdir: str
    process: Optional[subprocess.Popen] = None
    started_at: datetime = field(default_factory=datetime.now)
    output_buffer: List[str] = field(default_factory=list)
    status: str = "running"  # running, completed, failed, killed
    exit_code: Optional[int] = None
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "agent": self.agent,
            "prompt": self.prompt[:100] + "..." if len(self.prompt) > 100 else self.prompt,
            "workdir": self.workdir,
            "started_at": self.started_at.isoformat(),
            "status": self.status,
            "exit_code": self.exit_code,
            "output_lines": len(self.output_buffer)
        }


class CodingAgentSkill(BaseSkill):
    """
    Skill para execução de agentes de código (Codex, Claude Code, Pi).
    
    Suporta:
    - Execução one-shot e background
    - Múltiplos agentes (codex, claude, pi, opencode)
    - Monitoramento de sessões
    - Envio de input para processos
    
    IMPORTANTE: Sempre use modo PTY para agentes interativos!
    """
    
    # Configurações dos agentes suportados
    AGENTS = {
        'codex': {
            'cmd': 'codex',
            'exec_flag': 'exec',
            'auto_flag': '--full-auto',
            'yolo_flag': '--yolo',
            'requires_git': True
        },
        'claude': {
            'cmd': 'claude',
            'exec_flag': None,
            'auto_flag': None,
            'yolo_flag': None,
            'requires_git': False
        },
        'pi': {
            'cmd': 'pi',
            'exec_flag': '-p',
            'auto_flag': None,
            'yolo_flag': None,
            'requires_git': False
        },
        'opencode': {
            'cmd': 'opencode',
            'exec_flag': None,
            'auto_flag': None,
            'yolo_flag': None,
            'requires_git': False
        }
    }
    
    def __init__(self):
        super().__init__(
            name="coding-agent",
            description="Executa agentes de código (Codex CLI, Claude Code, Pi) via processo em background para controle programático."
        )
        self._sessions: Dict[str, AgentSession] = {}
        self._lock = threading.Lock()
    
    def execute(self, params: str) -> str:
        """
        Executa a skill com os parâmetros fornecidos.
        
        Formato: action:<action> [agent:<agent>] [workdir:<path>] [prompt:<text>] [sessionId:<id>]
        
        Actions:
        - exec: Executa agente (one-shot)
        - start: Inicia agente em background
        - list: Lista sessões ativas
        - poll: Verifica status de uma sessão
        - log: Obtém output de uma sessão
        - write: Envia input para uma sessão
        - kill: Termina uma sessão
        - available: Lista agentes disponíveis
        """
        parsed = self._parse_params(params)
        action = parsed.get('action', 'exec')
        
        try:
            if action == 'available':
                return self._list_available_agents()
            elif action == 'exec':
                return self._exec_agent(parsed)
            elif action == 'start':
                return self._start_background(parsed)
            elif action == 'list':
                return self._list_sessions()
            elif action == 'poll':
                return self._poll_session(parsed.get('sessionId', parsed.get('session_id', '')))
            elif action == 'log':
                return self._get_log(parsed.get('sessionId', parsed.get('session_id', '')), 
                                     int(parsed.get('lines', '50')))
            elif action == 'write':
                return self._write_input(parsed.get('sessionId', parsed.get('session_id', '')),
                                        parsed.get('data', parsed.get('input', '')))
            elif action == 'kill':
                return self._kill_session(parsed.get('sessionId', parsed.get('session_id', '')))
            else:
                return f"Ação desconhecida: {action}. Use: exec, start, list, poll, log, write, kill, available"
        except Exception as e:
            logger.exception(f"Erro no CodingAgentSkill: {e}")
            return f"❌ Erro: {str(e)}"
    
    def _parse_params(self, params: str) -> Dict[str, str]:
        """Parse de parâmetros no formato key:value."""
        result = {}
        # Regex para capturar key:value (suporta valores com aspas)
        pattern = r'(\w+):(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))'
        matches = re.findall(pattern, params)
        for key, quoted_double, quoted_single, simple_val in matches:
            result[key] = quoted_double or quoted_single or simple_val
        return result
    
    def _get_agent_path(self, agent_name: str) -> Optional[str]:
        """Verifica se um agente está disponível."""
        import shutil
        agent_config = self.AGENTS.get(agent_name.lower())
        if not agent_config:
            return None
        return shutil.which(agent_config['cmd'])
    
    def _list_available_agents(self) -> str:
        """Lista agentes disponíveis no sistema."""
        lines = ["🤖 Agentes de Código Disponíveis:\n"]
        
        for name, config in self.AGENTS.items():
            path = self._get_agent_path(name)
            if path:
                lines.append(f"  ✅ {name} ({config['cmd']}) - {path}")
            else:
                lines.append(f"  ❌ {name} ({config['cmd']}) - Não instalado")
        
        lines.append("\n📝 Para usar: action:exec agent:codex prompt:\"Sua tarefa\"")
        return "\n".join(lines)
    
    def _exec_agent(self, params: Dict[str, str]) -> str:
        """Executa um agente de forma síncrona (one-shot)."""
        agent = params.get('agent', 'codex').lower()
        prompt = params.get('prompt', '')
        workdir = params.get('workdir', os.getcwd())
        auto = params.get('auto', 'false').lower() == 'true'
        yolo = params.get('yolo', 'false').lower() == 'true'
        timeout = int(params.get('timeout', '300'))  # 5 min default
        
        if not prompt:
            return "❌ Prompt é obrigatório. Use: prompt:\"Sua tarefa\""
        
        agent_path = self._get_agent_path(agent)
        if not agent_path:
            return f"❌ Agente '{agent}' não encontrado. Use action:available para ver agentes instalados."
        
        # Monta o comando
        cmd = self._build_command(agent, prompt, auto, yolo)
        
        logger.info(f"Executando {agent}: {' '.join(cmd[:3])}...")
        
        try:
            # Em Windows, não temos pty nativo, usamos subprocess normal
            result = subprocess.run(
                cmd,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n\n[STDERR]:\n{result.stderr}"
            
            status = "✅" if result.returncode == 0 else "⚠️"
            return f"{status} Agente {agent} concluído (exit code: {result.returncode}):\n\n{output}"
            
        except subprocess.TimeoutExpired:
            return f"⏰ Timeout após {timeout}s. Use action:start para tarefas longas."
        except Exception as e:
            return f"❌ Erro ao executar {agent}: {str(e)}"
    
    def _build_command(self, agent: str, prompt: str, auto: bool, yolo: bool) -> List[str]:
        """Constrói o comando para o agente."""
        config = self.AGENTS[agent]
        cmd = [config['cmd']]
        
        # Adiciona flags específicas do agente
        if config['exec_flag']:
            cmd.append(config['exec_flag'])
        
        if yolo and config['yolo_flag']:
            cmd.append(config['yolo_flag'])
        elif auto and config['auto_flag']:
            cmd.append(config['auto_flag'])
        
        cmd.append(prompt)
        return cmd
    
    def _start_background(self, params: Dict[str, str]) -> str:
        """Inicia um agente em background."""
        agent = params.get('agent', 'codex').lower()
        prompt = params.get('prompt', '')
        workdir = params.get('workdir', os.getcwd())
        auto = params.get('auto', 'true').lower() == 'true'  # Default true para background
        yolo = params.get('yolo', 'false').lower() == 'true'
        
        if not prompt:
            return "❌ Prompt é obrigatório. Use: prompt:\"Sua tarefa\""
        
        agent_path = self._get_agent_path(agent)
        if not agent_path:
            return f"❌ Agente '{agent}' não encontrado."
        
        # Gera session ID
        session_id = f"{agent}-{uuid.uuid4().hex[:8]}"
        
        # Monta comando
        cmd = self._build_command(agent, prompt, auto, yolo)
        
        try:
            # Inicia processo em background
            process = subprocess.Popen(
                cmd,
                cwd=workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Cria sessão
            session = AgentSession(
                session_id=session_id,
                agent=agent,
                prompt=prompt,
                workdir=workdir,
                process=process
            )
            
            # Registra sessão
            with self._lock:
                self._sessions[session_id] = session
            
            # Inicia thread para capturar output
            output_thread = threading.Thread(
                target=self._capture_output,
                args=(session,),
                daemon=True
            )
            output_thread.start()
            
            return f"""🚀 Agente iniciado em background!

📋 Detalhes:
  Session ID: {session_id}
  Agente: {agent}
  Workdir: {workdir}
  Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}

📌 Para monitorar:
  action:poll sessionId:{session_id}
  action:log sessionId:{session_id}
  action:kill sessionId:{session_id}"""
            
        except Exception as e:
            return f"❌ Erro ao iniciar {agent}: {str(e)}"
    
    def _capture_output(self, session: AgentSession):
        """Thread para capturar output do processo."""
        try:
            for line in session.process.stdout:
                session.output_buffer.append(line)
                if len(session.output_buffer) > 10000:  # Limite de linhas
                    session.output_buffer = session.output_buffer[-5000:]
            
            # Processo terminou
            session.exit_code = session.process.wait()
            session.status = "completed" if session.exit_code == 0 else "failed"
            
        except Exception as e:
            logger.error(f"Erro ao capturar output: {e}")
            session.status = "failed"
    
    def _list_sessions(self) -> str:
        """Lista sessões ativas."""
        with self._lock:
            if not self._sessions:
                return "📭 Nenhuma sessão ativa."
            
            lines = ["📋 Sessões de Agentes:\n"]
            for sid, session in self._sessions.items():
                emoji = {
                    "running": "🏃",
                    "completed": "✅",
                    "failed": "❌",
                    "killed": "💀"
                }.get(session.status, "❓")
                
                lines.append(f"  {emoji} {sid}")
                lines.append(f"     Agente: {session.agent}")
                lines.append(f"     Status: {session.status}")
                lines.append(f"     Linhas de output: {len(session.output_buffer)}")
                lines.append("")
            
            return "\n".join(lines)
    
    def _poll_session(self, session_id: str) -> str:
        """Verifica status de uma sessão."""
        if not session_id:
            return "❌ sessionId é obrigatório."
        
        with self._lock:
            session = self._sessions.get(session_id)
        
        if not session:
            return f"❌ Sessão não encontrada: {session_id}"
        
        # Atualiza status se processo terminou
        if session.process and session.process.poll() is not None:
            session.exit_code = session.process.returncode
            session.status = "completed" if session.exit_code == 0 else "failed"
        
        emoji = {"running": "🏃", "completed": "✅", "failed": "❌", "killed": "💀"}.get(session.status, "❓")
        
        return f"""{emoji} Status da Sessão {session_id}:
  
  Agente: {session.agent}
  Status: {session.status}
  Exit Code: {session.exit_code if session.exit_code is not None else 'N/A'}
  Iniciado em: {session.started_at.strftime('%H:%M:%S')}
  Linhas de output: {len(session.output_buffer)}
  Workdir: {session.workdir}"""
    
    def _get_log(self, session_id: str, lines: int = 50) -> str:
        """Obtém log de uma sessão."""
        if not session_id:
            return "❌ sessionId é obrigatório."
        
        with self._lock:
            session = self._sessions.get(session_id)
        
        if not session:
            return f"❌ Sessão não encontrada: {session_id}"
        
        if not session.output_buffer:
            return f"📭 Nenhum output ainda para {session_id}"
        
        # Pega últimas N linhas
        output_lines = session.output_buffer[-lines:]
        output = "".join(output_lines)
        
        return f"""📜 Log da Sessão {session_id} (últimas {len(output_lines)} linhas):

{output}

[Total de linhas: {len(session.output_buffer)}]"""
    
    def _write_input(self, session_id: str, data: str) -> str:
        """Envia input para uma sessão."""
        if not session_id:
            return "❌ sessionId é obrigatório."
        if not data:
            return "❌ data é obrigatório."
        
        with self._lock:
            session = self._sessions.get(session_id)
        
        if not session:
            return f"❌ Sessão não encontrada: {session_id}"
        
        if session.status != "running":
            return f"❌ Sessão não está rodando (status: {session.status})"
        
        try:
            session.process.stdin.write(data + "\n")
            session.process.stdin.flush()
            return f"✅ Input enviado para {session_id}: {data}"
        except Exception as e:
            return f"❌ Erro ao enviar input: {str(e)}"
    
    def _kill_session(self, session_id: str) -> str:
        """Termina uma sessão."""
        if not session_id:
            return "❌ sessionId é obrigatório."
        
        with self._lock:
            session = self._sessions.get(session_id)
        
        if not session:
            return f"❌ Sessão não encontrada: {session_id}"
        
        if session.status != "running":
            return f"ℹ️ Sessão já não está rodando (status: {session.status})"
        
        try:
            session.process.terminate()
            time.sleep(0.5)
            if session.process.poll() is None:
                session.process.kill()
            
            session.status = "killed"
            session.exit_code = -1
            
            return f"💀 Sessão {session_id} terminada."
        except Exception as e:
            return f"❌ Erro ao terminar sessão: {str(e)}"
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna lista de ferramentas para o LLM."""
        return [
            {
                "name": "coding_agent_exec",
                "description": "Executa um agente de código (one-shot)",
                "parameters": {
                    "agent": {"type": "string", "description": "Agente: codex, claude, pi", "default": "codex"},
                    "prompt": {"type": "string", "description": "Tarefa para o agente", "required": True},
                    "workdir": {"type": "string", "description": "Diretório de trabalho"},
                    "auto": {"type": "boolean", "description": "Modo auto-approve", "default": False}
                }
            },
            {
                "name": "coding_agent_start",
                "description": "Inicia agente em background para tarefas longas",
                "parameters": {
                    "agent": {"type": "string", "description": "Agente: codex, claude, pi", "default": "codex"},
                    "prompt": {"type": "string", "description": "Tarefa para o agente", "required": True},
                    "workdir": {"type": "string", "description": "Diretório de trabalho"}
                }
            },
            {
                "name": "coding_agent_poll",
                "description": "Verifica status de uma sessão",
                "parameters": {
                    "sessionId": {"type": "string", "description": "ID da sessão", "required": True}
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

<warning>
⚠️ Agentes de código são aplicações de terminal INTERATIVAS!
Use action:start para tarefas longas e monitore com action:poll
</warning>

<usage>
<!-- Listar agentes disponíveis -->
<tool code="coding-agent">
action:available
</tool>

<!-- Execução rápida (one-shot) -->
<tool code="coding-agent">
action:exec agent:codex prompt:"Criar função de validação de email"
</tool>

<!-- Background para tarefas longas -->
<tool code="coding-agent">
action:start agent:pi workdir:~/projeto prompt:"Refatorar API"
</tool>

<!-- Monitorar sessão -->
<tool code="coding-agent">
action:poll sessionId:codex-abc123
</tool>

<!-- Ver log -->
<tool code="coding-agent">
action:log sessionId:codex-abc123 lines:100
</tool>

<!-- Terminar sessão -->
<tool code="coding-agent">
action:kill sessionId:codex-abc123
</tool>
</usage>

<agents>
- codex: OpenAI Codex CLI (requer git repo)
- claude: Anthropic Claude Code
- pi: Pi Coding Agent
- opencode: OpenCode
</agents>
</tool_definition>"""


# Para testes diretos
if __name__ == "__main__":
    skill = CodingAgentSkill()
    print(skill.get_definition())
    print("\n--- Teste: Agentes Disponíveis ---")
    print(skill.execute('action:available'))
