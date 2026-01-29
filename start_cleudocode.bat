@echo off
setlocal enabledelayedexpansion

TITLE CleudoCode - Sistema Unificado 🤖🚀

echo ============================================================
echo           INICIANDO CLEUDOCODE ECOSYSTEM 🤖🚀
echo ============================================================
echo.

:: 1. Verificar/Ativar Ambiente Virtual
echo [+] Verificando Ambiente Virtual (venv)...
if not exist "venv\Scripts\activate.bat" (
    echo [!] Erro: Ambiente virtual 'venv' nao encontrado!
    echo [!] Por favor, execute: python -m venv venv
    pause
    exit /b
)
call venv\Scripts\activate.bat
echo [OK] Ambiente Virtual Ativado.
echo.

:: 2. Verificar dependencias
echo [+] Validando dependencias...
pip install -q -r requirements.txt
echo [OK] Dependencias verificadas.
echo.

:: 3. Iniciar Daemon (Porta 5001)
echo [+] Iniciando CleudoDaemon (Porta 5001)...
start "CleudoDaemon Core" cmd /k "venv\Scripts\python.exe run_daemon.py"
timeout /t 3 > nul

:: 4. Iniciar Web Server Flask (Porta 5000)
echo [+] Iniciando Flask Web Server (Porta 5000)...
start "Cleudo Web Server" cmd /k "venv\Scripts\python.exe web_server.py"
timeout /t 3 > nul

:: 5. Iniciar Streamlit App (Porta 8501)
echo [+] Iniciando Streamlit Interface (Porta 8501)...
start "Cleudo Streamlit" cmd /k "venv\Scripts\python.exe -m streamlit run web_app.py --server.port 8501"

echo.
echo ============================================================
echo ✅ TODOS OS SERVICOS FORAM DISPARADOS!
echo.
echo - Web Interface:      http://localhost:5000
echo - Streamlit App:      http://localhost:8501
echo - Daemon API:         http://localhost:5001
echo - Ollama Remoto:      Configurado via .env
echo.
echo Mantenha as janelas de log abertas para monitoramento.
echo ============================================================
pause
