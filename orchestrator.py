import logging
import os
import json
import time
from pathlib import Path
from core.daemon import CleudoDaemon
from core.llm_providers import llm_hub

logger = logging.getLogger("Orchestrator")

class Orchestrator:
    def __init__(self):
        self.daemon = CleudoDaemon()
        self.agents_dir = Path("agents")
        self.agent_personas = {}
        self.mission_history = []
        self.agent_status = {} # Track what each agent is doing
        self.state_file = Path(".agent_status.json")
        self._load_all_personas()
        self._load_state()

    def _load_state(self):
        """Carrega o estado persistido dos agentes se existir"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    saved_status = json.load(f)
                    # Merge saved status with loaded personas
                    for agent, status in saved_status.items():
                        if agent in self.agent_status:
                            self.agent_status[agent].update(status)
                logger.info("Estado dos agentes restaurado do disco.")
            except Exception as e:
                logger.error(f"Erro ao carregar estado: {e}")

    def _save_state(self):
        """Salva o estado atual dos agentes em disco para o CLI ler"""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.agent_status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")

        
    def _load_all_personas(self):
        """Carrega todas as personas dos arquivos .md na pasta agents/"""
        if not self.agents_dir.exists():
            logger.warning(f"Diretório de agentes não encontrado: {self.agents_dir}")
            return
            
        for agent_file in self.agents_dir.glob("*.md"):
            try:
                name = agent_file.stem.lower()
                content = agent_file.read_text(encoding='utf-8')
                self.agent_personas[name] = content
                self.agent_personas[name] = content
                if name not in self.agent_status:
                    self.agent_status[name] = {
                        "state": "idle", 
                        "last_task": "Aguardando ordens", 
                        "last_active": time.time(),
                        "progress": 0,
                        "role": name.replace("-", " ").title()
                    }
                logger.debug(f"Persona carregada: {name}")
            except Exception as e:
                logger.error(f"Erro ao carregar persona {agent_file}: {e}")

    def get_agent_persona(self, name: str) -> str:
        return self.agent_personas.get(name.lower(), "Você é um assistente especializado do Cleudocode.")

    def get_status(self):
        """Retorna o status consolidado do Mission Control para a UI"""
        return {
            "agents": self.agent_status,
            "mission_history": self.mission_history[-10:] # Últimas 10 missões
        }

    def _log_mission(self, task: str, result: dict):
        self.mission_history.append({
            "timestamp": time.time(),
            "task": task,
            "status": result.get("status"),
            "agent": result.get("agent", "jarvis")
        })

    def delegate_task(self, target_agent: str, task: str):
        """Delega uma tarefa de um agente para outro (via Jarvis ou sistema)"""
        persona = self.get_agent_persona(target_agent)
        
        # Update status to busy
        self.agent_status[target_agent.lower()].update({
            "state": "busy", 
            "last_task": task[:100], 
            "last_active": time.time(),
            "progress": 10
        })
        self._save_state()

        messages = [
            {"role": "system", "content": persona},
            {"role": "user", "content": task}
        ]
        
        logger.info(f"Delegando para {target_agent}: {task[:50]}...")
        try:
            response = llm_hub.query(messages=messages)
            
            # Update status back to idle
            self.agent_status[target_agent.lower()]["state"] = "idle"
            self.agent_status[target_agent.lower()]["progress"] = 100
            self._save_state()
            
            result = {
                "agent": target_agent,
                "status": "success",
                "output": response
            }
            self._log_mission(task, result)
            return result
        except Exception as e:
            logger.error(f"Falha na delegação para {target_agent}: {e}")
            self.agent_status[target_agent.lower()]["state"] = "error"
            self._save_state()
            return {
                "agent": target_agent,
                "status": "error",
                "output": str(e)
            }

    def brainstorm(self, agents_list: list, task: str):
        """Implementa debate entre múltiplos agentes (Threaded Discussions)"""
        discussion_log = f"📌 Início de Debate sobre: {task}\n"
        context = task
        
        for agent in agents_list:
            self.agent_status[agent.lower()]["state"] = "busy"
            self.agent_status[agent.lower()]["last_task"] = f"Debatendo: {task[:50]}"
            
            persona = self.get_agent_persona(agent)
            prompt = f"Contexto do Debate:\n{discussion_log}\n\nSua vez ({agent}), contribua com sua visão técnica baseada em sua persona."
            
            try:
                response = llm_hub.query(messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": prompt}
                ])
                discussion_log += f"\n--- CONTRIBUTIÇÃO DE {agent.upper()} ---\n{response}\n"
                self.agent_status[agent.lower()]["state"] = "idle"
            except Exception as e:
                logger.error(f"Erro no debate com {agent}: {e}")
                self.agent_status[agent.lower()]["state"] = "error"
            
            self._save_state()

        # Synth by Jarvis
        jarvis_persona = self.get_agent_persona("jarvis")
        synth_prompt = f"Analise o debate abaixo e entregue a solução final consolidada ao usuário.\n\n{discussion_log}"
        final_output = llm_hub.query(messages=[
            {"role": "system", "content": jarvis_persona},
            {"role": "user", "content": synth_prompt}
        ])
        
        return final_output

    def receive_message(self, msg: dict):
        """
        Interpreta a mensagem e decide se executa um workflow direto,
        se delega ou se inicia um debate entre agentes.
        """
        text = msg.get("text", "")
        
        logger.info(f"Recebendo comando: {text}")

        # 1. Threaded Discussion Trigger (ex: /debate [agent1,agent2] [task])
        if text.startswith("/debate "):
            try:
                parts = text.replace("/debate ", "").split(" ", 1)
                agents_raw = parts[0].strip("[]").split(",")
                task_desc = parts[1]
                
                logger.info(f"Iniciando debate entre: {agents_raw}")
                result = self.brainstorm(agents_raw, task_desc)
                
                return {
                    "status": "success",
                    "mission_control": "collaborative_reasoning",
                    "result": {"output": result}
                }
            except Exception as e:
                logger.error(f"Erro ao iniciar debate: {e}")

        # 2. Seleção de Personagem (Default: Jarvis)
        target = msg.get("targeted_agent", "jarvis").lower()
        persona = self.get_agent_persona(target)
        
        persona = self.get_agent_persona(target)
        
        self.agent_status[target].update({
            "state": "busy", 
            "last_task": text[:100], 
            "last_active": time.time(),
            "progress": 20
        })
        self._save_state()
        
        if target == "jarvis":
            system_prompt = f"{persona}\n\nVocê deve analisar se pode resolver o pedido ou se deve delegar. Use a sintaxe 'delegate-task [agent-id] [task-description]' se necessário."
        else:
            system_prompt = persona

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        try:
            response = llm_hub.query(messages=messages)
            self.agent_status[target]["state"] = "idle"
            self.agent_status[target]["progress"] = 100
            self._save_state()
            
            # Checa se Jarvis decidiu delegar
            if "delegate-task" in response:
                try:
                    p = response.split("delegate-task", 1)[1].strip().split(" ", 1)
                    if len(p) >= 2:
                        agent_id = p[0]
                        delegated_task = p[1]
                        delegation_result = self.delegate_task(agent_id, delegated_task)
                        return {
                            "status": "success",
                            "mission_control": "delegated",
                            "agent": agent_id,
                            "result": {"output": delegation_result["output"], "jarvis_decision": response}
                        }
                except Exception as parse_err:
                    logger.error(f"Erro ao parsear delegação: {parse_err}")

            res = {
                "status": "success",
                "mission_control": "handled_by_lead",
                "result": {"overall_status": "success", "output": response}
            }
            self._log_mission(text, {"status": "success", "agent": target})
            return res
            
        except Exception as e:
            logger.error(f"Erro no Mission Control: {e}")
            self.agent_status[target]["state"] = "error"
            self._save_state()
            return {"status": "error", "message": f"Erro {target}: {str(e)}"}

orchestrator = Orchestrator()
