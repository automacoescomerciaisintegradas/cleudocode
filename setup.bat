@echo off
REM Script de Setup Automático para Cleudocode no Windows
REM Autor: Automações Comerciais Integradas
REM Versão: 1.0

echo ===========================================
echo   CLEUDOCODE - Setup Automático (Windows)
echo ===========================================

REM Verifica se o Python está instalado
echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python não encontrado!
    echo Por favor, instale o Python 3.10+ e verifique se está adicionado ao PATH.
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo OK: Python encontrado
)

REM Verifica se o Git está instalado
echo Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Git não encontrado!
    echo Por favor, instale o Git para Windows.
    echo Baixe em: https://git-scm.com/download/win
    pause
    exit /b 1
) else (
    echo OK: Git encontrado
)

REM Cria ambiente virtual
echo Criando ambiente virtual...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao criar ambiente virtual
        pause
        exit /b 1
    )
)

REM Ativa ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualiza pip
echo Atualizando pip...
python -m pip install --upgrade pip

REM Instala dependências
echo Instalando dependencias...
pip install flask flask-cors python-dotenv requests psutil pyyaml pypdf click colorama

if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)

REM Verifica se o arquivo .env existe
if not exist ".env" (
    echo Configurando arquivo .env...
    if exist ".env.example" (
        copy .env.example .env
        echo OK: Arquivo .env criado a partir do .env.example
    ) else (
        echo AVISO: Arquivo .env.example nao encontrado, criando .env basico...
        echo. 2>.env
        echo # Configuracao Cleudocode Telegram Relay >> .env
        echo. >> .env
        echo # --- TELEGRAM --- >> .env
        echo # Obtenha com o @BotFather no Telegram >> .env
        echo TELEGRAM_BOT_TOKEN= >> .env
        echo # Obtenha com o @userinfobot ou @IDBot >> .env
        echo TELEGRAM_USER_ID= >> .env
        echo. >> .env
        echo # --- PERSONALIZACAO --- >> .env
        echo USER_NAME=Seu Nome >> .env
        echo USER_TIMEZONE=America/Sao_Paulo >> .env
        echo. >> .env
        echo # --- TRANSCRICAO DE VOZ E LLM --- >> .env
        echo # "gemini" ou "local" >> .env
        echo VOICE_PROVIDER=gemini >> .env
        echo GEMINI_API_KEY= >> .env
        echo LLM_MODEL=gemini-2.0-flash >> .env
        echo. >> .env
        echo # --- OLLAMA SERVER CONFIGURATION (opcional) --- >> .env
        echo OLLAMA_HOST=http://localhost:11434 >> .env
        echo DEEPSEEK_MODEL=llama3:8b >> .env
        echo. >> .env
        echo # Gateway Token (usado para autenticacao) >> .env
        echo CLEUDOCODE_GATEWAY_TOKEN=cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce >> .env
        echo. >> .env
        echo # WhatsApp (Evolution API) >> .env
        echo WHATSAPP_API_TOKEN_INSTANCE= >> .env
        echo. >> .env
        echo # AI API Keys (opcional - para fallback) >> .env
        echo ANTHROPIC_API_KEY= >> .env
        echo OPENAI_API_KEY= >> .env
        echo GROQ_API_KEY= >> .env
    )
    echo AVISO: Configure seu .env com credenciais validas!
)

echo.
echo ###########################################
echo # INSTALACAO CONCLUIDA COM SUCESSO!       #
echo ###########################################
echo.
echo Para executar o Cleudocode:
echo 1. Abra o Command Prompt ou PowerShell
echo 2. Navegue ate o diretorio do projeto
echo 3. Execute: venv\Scripts\activate.bat
echo 4. Execute: python web_server.py
echo.
echo Ou use o CLI:
echo python cli\main.py start
echo.
pause