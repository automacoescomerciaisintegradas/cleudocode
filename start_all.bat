@echo off
echo Iniciando Cleudocodebot Environment...

:: Ativa o ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Inicia o Daemon em uma nova janela
echo Iniciando Daemon...
start "CleudoDaemon Core" cmd /k "python run_daemon.py"

:: Espera um pouco para o Daemon subir
timeout /t 5

:: Inicia o Web App em uma nova janela (ou na mesma, mas o streamlit abre navegador)
echo Iniciando Web App...
streamlit run web_app.py

pause
