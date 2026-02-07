@echo off
setlocal

:: =================================================================
:: Script de Setup para o Ambiente Docker do CleudoCode
:: =================================================================
echo.
echo [CLEUDOCODE SETUP] Iniciando configuracao do ambiente...
echo.

:: -----------------------------------------------------------------
:: 1. Verificar se o Docker esta em execucao
:: -----------------------------------------------------------------
echo [INFO] Verificando se o Docker esta em execucao...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] O Docker nao parece estar em execucao. Por favor, inicie o Docker Desktop e tente novamente.
    goto:eof
)
echo [OK] Docker detectado.

:: -----------------------------------------------------------------
:: 2. Criar diretorios necessarios
:: -----------------------------------------------------------------
echo [INFO] Verificando e criando diretorios de dados...
if not exist "exports" ( mkdir exports && echo [OK] Diretorio 'exports' criado. )
if not exist "uploads" ( mkdir uploads && echo [OK] Diretorio 'uploads' criado. )
if not exist "memory_db" ( mkdir memory_db && echo [OK] Diretorio 'memory_db' criado. )
if not exist "sandbox_io" ( mkdir sandbox_io && echo [OK] Diretorio 'sandbox_io' criado. )
echo [OK] Diretorios de dados verificados.


:: -----------------------------------------------------------------
:: 3. Criar arquivo .env
:: -----------------------------------------------------------------
echo [INFO] Verificando arquivo de ambiente .env...
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Arquivo .env nao encontrado. Copiando de .env.example...
        copy .env.example .env >nul
        echo [OK] Arquivo .env criado. Por favor, revise e ajuste as variaveis em .env se necessario.
    ) else (
        echo [AVISO] .env.example nao encontrado. Pulando a criacao do .env.
    )
) else (
    echo [OK] Arquivo .env ja existe.
)


:: -----------------------------------------------------------------
:: 4. Construir e iniciar os conteineres Docker
:: -----------------------------------------------------------------
echo [INFO] Construindo as imagens Docker (isso pode levar alguns minutos na primeira vez)...
docker-compose build
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao construir as imagens Docker. Verifique os logs acima.
    goto:eof
)

echo [INFO] Iniciando os servicos com Docker Compose...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao iniciar os servicos. Verifique os logs com 'docker-compose logs'.
    goto:eof
)

echo.
echo [SUCESSO] O ambiente CleudoCode foi iniciado!
echo.
echo   - A aplicacao principal esta disponivel em: http://localhost:8501
echo   - Para parar o ambiente, execute: docker-compose down
echo.

endlocal
