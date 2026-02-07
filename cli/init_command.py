"""
Comando: cleudocode init

Wizard interativo de configuração inicial do Cleudocode
"""

import os
import sys
import subprocess
import uuid
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import shutil


class Colors:
    """Cores ANSI para terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class InitWizard:
    """Wizard de inicialização do Cleudocode"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".cleudocode"
        self.config_file = self.config_dir / "config.yaml"
        self.token_file = self.config_dir / ".gateway_token"
        self.config = {}
        
    def print_header(self, text: str):
        """Imprime cabeçalho formatado"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    def print_step(self, step: int, total: int, text: str):
        """Imprime passo do wizard"""
        print(f"{Colors.CYAN}[{step}/{total}] {text}{Colors.ENDC}")
    
    def print_success(self, text: str):
        """Imprime mensagem de sucesso"""
        print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")
    
    def print_error(self, text: str):
        """Imprime mensagem de erro"""
        print(f"{Colors.RED}❌ {text}{Colors.ENDC}")
    
    def print_warning(self, text: str):
        """Imprime mensagem de aviso"""
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")
    
    def print_info(self, text: str):
        """Imprime mensagem informativa"""
        print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")
    
    def ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Pergunta sim/não"""
        default_str = "S/n" if default else "s/N"
        response = input(f"{Colors.CYAN}❓ {question} [{default_str}]: {Colors.ENDC}").strip().lower()
        
        if not response:
            return default
        
        return response in ['s', 'sim', 'y', 'yes']
    
    def ask_input(self, question: str, default: str = "") -> str:
        """Pergunta com input de texto"""
        if default:
            response = input(f"{Colors.CYAN}❓ {question} [{default}]: {Colors.ENDC}").strip()
            return response if response else default
        else:
            return input(f"{Colors.CYAN}❓ {question}: {Colors.ENDC}").strip()
    
    def ask_choice(self, question: str, choices: list, default: int = 0) -> str:
        """Pergunta com múltipla escolha"""
        print(f"\n{Colors.CYAN}❓ {question}{Colors.ENDC}")
        for i, choice in enumerate(choices, 1):
            marker = "→" if i-1 == default else " "
            print(f"  {marker} {i}. {choice}")
        
        while True:
            response = input(f"{Colors.CYAN}Escolha [1-{len(choices)}] (padrão: {default+1}): {Colors.ENDC}").strip()
            
            if not response:
                return choices[default]
            
            try:
                idx = int(response) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
                else:
                    self.print_error(f"Escolha um número entre 1 e {len(choices)}")
            except ValueError:
                self.print_error("Digite um número válido")
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Verifica dependências do sistema"""
        self.print_step(1, 7, "Verificando dependências...")
        
        dependencies = {
            "python3": False,
            "pip": False,
            "git": False,
            "docker": False,
            "gcloud": False
        }
        
        # Python
        try:
            result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                dependencies["python3"] = True
                version = result.stdout.strip()
                self.print_success(f"Python: {version}")
        except FileNotFoundError:
            self.print_error("Python 3 não encontrado")
        
        # Pip
        try:
            result = subprocess.run(["pip3", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                dependencies["pip"] = True
                self.print_success("pip instalado")
        except FileNotFoundError:
            self.print_error("pip não encontrado")
        
        # Git
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                dependencies["git"] = True
                version = result.stdout.strip()
                self.print_success(f"Git: {version}")
        except FileNotFoundError:
            self.print_warning("Git não encontrado (opcional)")
        
        # Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                dependencies["docker"] = True
                version = result.stdout.strip()
                self.print_success(f"Docker: {version}")
        except FileNotFoundError:
            self.print_warning("Docker não encontrado (opcional)")
        
        # Google Cloud SDK
        try:
            result = subprocess.run(["gcloud", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                dependencies["gcloud"] = True
                self.print_success("Google Cloud SDK instalado")
        except FileNotFoundError:
            self.print_warning("Google Cloud SDK não encontrado (opcional para Stitch MCP)")
        
        return dependencies
    
    def create_directory_structure(self):
        """Cria estrutura de diretórios"""
        self.print_step(2, 7, "Criando estrutura de diretórios...")
        
        directories = [
            self.config_dir,
            self.config_dir / "workspace",
            self.config_dir / "memory",
            self.config_dir / "skills",
            self.config_dir / "logs",
            self.config_dir / "cache",
            self.config_dir / "browser_data"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.print_success(f"Criado: {directory}")
    
    def generate_gateway_token(self) -> str:
        """Gera token do gateway"""
        self.print_step(3, 7, "Gerando token de autenticação...")
        
        if self.token_file.exists():
            with open(self.token_file, 'r') as f:
                token = f.read().strip()
            
            if self.ask_yes_no("Token existente encontrado. Gerar novo?", default=False):
                token = str(uuid.uuid4())
                with open(self.token_file, 'w') as f:
                    f.write(token)
                self.token_file.chmod(0o600)
                self.print_success("Novo token gerado")
            else:
                self.print_info("Usando token existente")
        else:
            token = str(uuid.uuid4())
            with open(self.token_file, 'w') as f:
                f.write(token)
            self.token_file.chmod(0o600)
            self.print_success(f"Token gerado: {token[:8]}...{token[-8:]}")
        
        return token
    
    def configure_llm_provider(self):
        """Configura provedor de LLM"""
        self.print_step(4, 7, "Configurando provedor de LLM...")
        
        providers = [
            "Ollama (Local)",
            "OpenAI",
            "Anthropic (Claude)",
            "Google (Gemini)",
            "Pular configuração"
        ]
        
        choice = self.ask_choice("Qual provedor de LLM você deseja usar?", providers, default=0)
        
        if choice == "Ollama (Local)":
            self.config["llm"] = {
                "default_provider": "ollama",
                "default_model": "qwen2.5-coder",
                "providers": {
                    "ollama": {
                        "host": self.ask_input("URL do Ollama", "http://localhost:11434"),
                        "enabled": True
                    }
                }
            }
            self.print_success("Ollama configurado")
        
        elif choice == "OpenAI":
            api_key = self.ask_input("OpenAI API Key (deixe vazio para usar variável de ambiente)")
            self.config["llm"] = {
                "default_provider": "openai",
                "default_model": "gpt-4",
                "providers": {
                    "openai": {
                        "api_key": api_key or "${OPENAI_API_KEY}",
                        "enabled": True,
                        "model": "gpt-4"
                    }
                }
            }
            self.print_success("OpenAI configurado")
        
        elif choice == "Anthropic (Claude)":
            api_key = self.ask_input("Anthropic API Key (deixe vazio para usar variável de ambiente)")
            self.config["llm"] = {
                "default_provider": "anthropic",
                "default_model": "claude-3-sonnet-20240229",
                "providers": {
                    "anthropic": {
                        "api_key": api_key or "${ANTHROPIC_API_KEY}",
                        "enabled": True,
                        "model": "claude-3-sonnet-20240229"
                    }
                }
            }
            self.print_success("Anthropic configurado")
        
        elif choice == "Google (Gemini)":
            api_key = self.ask_input("Google API Key (deixe vazio para usar variável de ambiente)")
            self.config["llm"] = {
                "default_provider": "google",
                "default_model": "gemini-pro",
                "providers": {
                    "google": {
                        "api_key": api_key or "${GOOGLE_API_KEY}",
                        "enabled": True,
                        "model": "gemini-pro"
                    }
                }
            }
            self.print_success("Google Gemini configurado")
        
        else:
            self.print_info("Configuração de LLM pulada")
    
    def configure_mcp(self, has_gcloud: bool):
        """Configura MCP (Stitch)"""
        self.print_step(5, 7, "Configurando integrações MCP...")
        
        if not has_gcloud:
            self.print_warning("Google Cloud SDK não encontrado. Pulando configuração do Stitch MCP.")
            return
        
        if self.ask_yes_no("Deseja configurar Stitch MCP (geração de UI com IA)?", default=True):
            # Verificar se ADC está configurado
            try:
                result = subprocess.run(
                    ["gcloud", "auth", "application-default", "print-access-token"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.print_success("Credenciais ADC encontradas")
                    
                    # Obter projeto
                    result = subprocess.run(
                        ["gcloud", "config", "get-value", "project"],
                        capture_output=True,
                        text=True
                    )
                    
                    project_id = result.stdout.strip() if result.returncode == 0 else ""
                    
                    if project_id:
                        self.print_success(f"Projeto Google Cloud: {project_id}")
                        
                        # Adicionar configuração MCP
                        self.config["mcp"] = {
                            "enabled": True,
                            "stitch": {
                                "enabled": True,
                                "provider": "google",
                                "url": "https://stitch.googleapis.com/mcp",
                                "auth": {
                                    "type": "oauth2_adc",
                                    "project_id": project_id,
                                    "credentials_file": "~/.config/gcloud/application_default_credentials.json"
                                }
                            }
                        }
                        self.print_success("Stitch MCP configurado")
                    else:
                        self.print_warning("Projeto Google Cloud não configurado")
                else:
                    self.print_warning("ADC não configurado. Execute: gcloud auth application-default login")
            except Exception as e:
                self.print_error(f"Erro ao verificar ADC: {e}")
        else:
            self.print_info("Configuração MCP pulada")
    
    def save_config(self):
        """Salva configuração"""
        self.print_step(6, 7, "Salvando configuração...")
        
        # Carregar config base se existir
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                base_config = yaml.safe_load(f) or {}
        else:
            base_config = {}
        
        # Merge com nova config
        base_config.update(self.config)
        
        # Salvar
        with open(self.config_file, 'w') as f:
            yaml.dump(base_config, f, default_flow_style=False, allow_unicode=True)
        
        self.print_success(f"Configuração salva em: {self.config_file}")
    
    def validate_installation(self):
        """Valida instalação"""
        self.print_step(7, 7, "Validando instalação...")
        
        checks = []
        
        # Verificar estrutura de diretórios
        if self.config_dir.exists():
            checks.append(("Diretório de configuração", True))
        else:
            checks.append(("Diretório de configuração", False))
        
        # Verificar config.yaml
        if self.config_file.exists():
            checks.append(("Arquivo de configuração", True))
        else:
            checks.append(("Arquivo de configuração", False))
        
        # Verificar token
        if self.token_file.exists():
            checks.append(("Token de autenticação", True))
        else:
            checks.append(("Token de autenticação", False))
        
        # Exibir resultados
        print()
        for check, status in checks:
            if status:
                self.print_success(check)
            else:
                self.print_error(check)
        
        all_passed = all(status for _, status in checks)
        
        if all_passed:
            self.print_success("\n✨ Instalação validada com sucesso!")
        else:
            self.print_error("\n❌ Alguns checks falharam")
        
        return all_passed
    
    def show_next_steps(self):
        """Mostra próximos passos"""
        self.print_header("PRÓXIMOS PASSOS")
        
        print(f"{Colors.BOLD}Comandos disponíveis:{Colors.ENDC}\n")
        
        commands = [
            ("cleudocode dashboard", "Abrir dashboard web"),
            ("cleudocode status", "Ver status dos serviços"),
            ("cleudocode config", "Ver configuração"),
            ("cleudocode stitch list", "Listar projetos Stitch (se configurado)"),
        ]
        
        for cmd, desc in commands:
            print(f"  {Colors.GREEN}${Colors.ENDC} {Colors.CYAN}{cmd}{Colors.ENDC}")
            print(f"    {desc}\n")
        
        print(f"{Colors.BOLD}Documentação:{Colors.ENDC}")
        print(f"  📖 README: https://github.com/cleudocode/cleudocode")
        print(f"  📚 Docs: ./docs/")
        print(f"  💡 NotebookLM: https://notebooklm.google.com/notebook/8dc6916e-a1b0-4cdd-b6f7-50e4dafb5c69\n")
    
    def run(self):
        """Executa wizard completo"""
        self.print_header("CLEUDOCODE - WIZARD DE INICIALIZAÇÃO")
        
        print(f"{Colors.BOLD}Bem-vindo ao Cleudocode!{Colors.ENDC}")
        print("Este wizard irá configurar seu ambiente.\n")
        
        if not self.ask_yes_no("Deseja continuar?", default=True):
            print("\n👋 Até logo!")
            return
        
        try:
            # 1. Verificar dependências
            deps = self.check_dependencies()
            
            # 2. Criar estrutura
            self.create_directory_structure()
            
            # 3. Gerar token
            self.generate_gateway_token()
            
            # 4. Configurar LLM
            self.configure_llm_provider()
            
            # 5. Configurar MCP
            self.configure_mcp(deps.get("gcloud", False))
            
            # 6. Salvar config
            self.save_config()
            
            # 7. Validar
            if self.validate_installation():
                self.show_next_steps()
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}✨ Configuração concluída!{Colors.ENDC}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}⚠️  Configuração cancelada pelo usuário{Colors.ENDC}")
            sys.exit(1)
        except Exception as e:
            self.print_error(f"Erro durante configuração: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Função principal"""
    wizard = InitWizard()
    wizard.run()


if __name__ == "__main__":
    main()
