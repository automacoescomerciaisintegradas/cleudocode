@echo off
echo ==========================================
echo    INICIANDO NOVO LAYOUT MODERN AI 🚀
echo ==========================================
echo.
echo 1. Ativando Ambiente Virtual...
call venv\Scripts\activate

echo 2. Abrindo Edge e Iniciando Servidor...
echo.
echo    Acesse: http://localhost:5000
echo.
start msedge http://localhost:5000
python web_server.py
pause
