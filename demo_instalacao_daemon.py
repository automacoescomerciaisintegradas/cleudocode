#!/usr/bin/env python3
"""
Script de demonstração da funcionalidade cleudocodebot onboard --install-daemon
"""
import os
import sys
import subprocess
import platform

def demo_instalacao_daemon():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                 DEMONSTRAÇÃO: cleudocodebot                ║")
    print("║              onboard --install-daemon                      ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    print("1. Verificando o sistema operacional...")
    sistema = platform.system()
    print(f"   Sistema detectado: {sistema}")
    print()
    
    print("2. Verificando se o comando CLI está disponível...")
    try:
        result = subprocess.run([sys.executable, "-m", "cli.main", "--help"], 
                              capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print("   ✅ Comando CLI disponível")
        else:
            print("   ❌ Comando CLI não encontrado")
            return
    except Exception as e:
        print(f"   ❌ Erro ao verificar CLI: {e}")
        return
    print()
    
    print("3. Demonstrando o comando de instalação do daemon...")
    print("   Comando: cleudocodebot onboard --install-daemon")
    print()
    
    print("   Este comando irá:")
    print("   • Detectar automaticamente o sistema operacional")
    print("   • Criar o serviço apropriado para o sistema:")
    print("     - Linux: serviço systemd em /etc/systemd/system/cleudocodebot.service")
    print("     - Windows: tarefa agendada ou serviço NSSM")
    print("     - macOS: agente launchd")
    print("   • Iniciar o serviço automaticamente")
    print("   • Configurar para iniciar com o sistema")
    print()
    
    print("4. Após a instalação, o sistema estará disponível como serviço:")
    print("   • API REST: http://localhost:5001")
    print("   • Dashboard: streamlit run web/dashboard.py")
    print("   • O daemon iniciará automaticamente com o sistema")
    print()
    
    print("5. Exemplo de uso após instalação:")
    print("   # Verificar status do daemon")
    print("   cleudocodebot status")
    print()
    print("   # Parar o daemon")
    print("   cleudocodebot stop")
    print()
    print("   # Iniciar o daemon")
    print("   cleudocodebot start")
    print()
    
    print("6. Segurança:")
    print("   • O arquivo .env com chaves sensíveis NÃO é incluído no commit")
    print("   • O sistema usa tokens JWT para autenticação")
    print("   • Todos os endpoints têm proteção adequada")
    print()
    
    print("🎉 Demonstração completa!")
    print()
    print("Para instalar o daemon em seu sistema, execute:")
    print(f"   python -m cli.main onboard --install-daemon")
    print()
    print("OU com o executável instalado:")
    print("   cleudocodebot onboard --install-daemon")

if __name__ == "__main__":
    demo_instalacao_daemon()