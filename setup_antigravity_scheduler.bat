@echo off
echo ========================================
echo  CONFIGURANDO AGENDAMENTO ANTIGRAVITY
echo ========================================
echo.

cd /d "%~dp0"

echo [INFO] Configurando tarefas agendadas para workflows Antigravity...
echo.

REM Monitoramento contínuo (a cada 5 minutos)
echo [1/4] Configurando monitoramento contínuo...
schtasks /create /tn "Antigravity Monitor" /tr "python \"%CD%\workflow_manager.py\" run \"Antigravity Monitor\"" /sc minute /mo 5 /f >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Monitor configurado - executa a cada 5 minutos
) else (
    echo ❌ Erro ao configurar monitor
)

REM Status diário (9h da manhã)
echo [2/4] Configurando verificação diária de status...
schtasks /create /tn "Antigravity Status Daily" /tr "python \"%CD%\workflow_manager.py\" run \"Antigravity Status Check\"" /sc daily /st 09:00 /f >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Status diário configurado - executa às 9h
) else (
    echo ❌ Erro ao configurar status diário
)

REM Backup diário (2h da manhã)
echo [3/4] Configurando backup diário...
schtasks /create /tn "Antigravity Backup Daily" /tr "python \"%CD%\workflow_manager.py\" run \"Antigravity Backup\"" /sc daily /st 02:00 /f >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Backup diário configurado - executa às 2h
) else (
    echo ❌ Erro ao configurar backup diário
)

REM Sincronização horária
echo [4/4] Configurando sincronização horária...
schtasks /create /tn "Antigravity Sync Hourly" /tr "python \"%CD%\workflow_manager.py\" run \"Antigravity Sync\"" /sc hourly /f >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Sincronização horária configurada
) else (
    echo ❌ Erro ao configurar sincronização
)

echo.
echo ========================================
echo  VERIFICANDO TAREFAS CRIADAS
echo ========================================
echo.

echo Tarefas Antigravity configuradas:
schtasks /query /tn "Antigravity*" /fo table 2>nul | findstr "Antigravity"

echo.
echo ========================================
echo  COMANDOS ÚTEIS
echo ========================================
echo.
echo Para listar todas as tarefas:
echo   schtasks /query /tn "Antigravity*"
echo.
echo Para executar manualmente:
echo   schtasks /run /tn "Antigravity Monitor"
echo.
echo Para remover uma tarefa:
echo   schtasks /delete /tn "Antigravity Monitor" /f
echo.
echo Para remover todas as tarefas Antigravity:
echo   for /f "tokens=1" %%i in ('schtasks /query /tn "Antigravity*" /fo list ^| findstr "TaskName"') do schtasks /delete /tn %%i /f
echo.

pause