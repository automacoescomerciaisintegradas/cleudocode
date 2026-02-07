@echo off
echo ========================================
echo  TESTANDO WORKFLOWS ANTIGRAVITY
echo ========================================
echo.

cd /d "%~dp0"

echo [INFO] Testando workflows do sistema Antigravity...
echo.

REM Teste 1: Workflow simples
echo [1/5] Testando workflow simples...
python workflow_manager.py run "Test Antigravity Simple"
if %errorlevel%==0 (
    echo ✅ Teste simples: SUCESSO
) else (
    echo ❌ Teste simples: FALHA
)
echo.

REM Teste 2: Listagem de workflows
echo [2/5] Verificando workflows disponíveis...
python workflow_manager.py list | findstr "Antigravity" >nul
if %errorlevel%==0 (
    echo ✅ Workflows Antigravity encontrados
) else (
    echo ❌ Workflows Antigravity não encontrados
)
echo.

REM Teste 3: Verificar diretório de relatórios
echo [3/5] Verificando diretório de relatórios...
if exist "reports\" (
    echo ✅ Diretório reports/ existe
    dir reports\*.txt >nul 2>&1
    if %errorlevel%==0 (
        echo ✅ Relatórios encontrados
    ) else (
        echo ⚠️ Nenhum relatório encontrado
    )
) else (
    echo ❌ Diretório reports/ não existe
)
echo.

REM Teste 4: Verificar dependências Python
echo [4/5] Verificando dependências Python...
python -c "import yaml, jinja2, requests; print('✅ Dependências OK')" 2>nul
if %errorlevel%==0 (
    echo ✅ Todas as dependências instaladas
) else (
    echo ❌ Dependências faltando
)
echo.

REM Teste 5: Status do sistema
echo [5/5] Verificando status do sistema...
if exist "workflow_manager.py" (
    echo ✅ Gerenciador de workflows presente
) else (
    echo ❌ Gerenciador de workflows não encontrado
)

if exist "skills\workflows\antigravity_*.lobster" (
    echo ✅ Workflows Antigravity presentes
) else (
    echo ❌ Workflows Antigravity não encontrados
)

echo.
echo ========================================
echo  RESUMO DOS TESTES
echo ========================================
echo.

echo Workflows Antigravity disponíveis:
python workflow_manager.py list | findstr "Antigravity"

echo.
echo Para executar um workflow específico:
echo   python workflow_manager.py run "Nome do Workflow"
echo.
echo Para ver detalhes de um workflow:
echo   python workflow_manager.py info "Nome do Workflow"
echo.

pause