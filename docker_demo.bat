@echo off
REM Script de demonstração para execução do Cleudocodebot com Docker no Windows

echo ===========================================
echo  DEMONSTRACAO: Cleudocodebot com Docker
echo ===========================================

echo.
echo 1. EXECUTAR O SISTEMA COMPLETO:
echo    docker compose -f docker-compose.full.yml up -d
echo.
echo    Acesse:
echo    - Interface web: http://localhost:8501
echo    - Dashboard: http://localhost:8502
echo    - API REST: http://localhost:5001
echo.

echo 2. EXECUTAR APENAS O DAEMON:
echo    docker compose -f docker-compose.daemon.yml up -d
echo.
echo    A API REST estara disponivel em: http://localhost:5001
echo.

echo 3. EXECUTAR EM AMBIENTE DE DESENVOLVIMENTO:
echo    docker compose -f docker-compose.yml up -d
echo.
echo    A interface web estara disponivel em: http://localhost:8501
echo.

echo 4. EXECUTAR EM AMBIENTE DE PRODUCAO (NUVEM):
echo    docker compose -f docker-compose.cloud.yml up -d
echo.

echo 5. VERIFICAR STATUS DOS CONTAINERS:
echo    docker compose -f docker-compose.full.yml ps
echo.

echo 6. VISUALIZAR LOGS:
echo    docker compose -f docker-compose.full.yml logs -f
echo.

echo 7. PARAR E REMOVER OS CONTAINERS:
echo    docker compose -f docker-compose.full.yml down
echo.

echo ===========================================
echo IMPORTANTE:
echo - Certifique-se de ter o Docker e Docker Compose instalados
echo - Configure as variaveis de ambiente no arquivo .env se necessario
echo - O sistema requer um servidor Ollama rodando (externo ou via compose)
echo ===========================================
pause