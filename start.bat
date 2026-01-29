@echo off
echo ==========================================
echo    INICIANDO LLM P2P CHAT SYSTEM 🚀
echo ==========================================
echo.
echo 1. Ativando Ambiente Virtual...
call venv\Scripts\activate

echo 2. Verificando Dependencias...
pip install -q chromadb pypdf beautifulsoup4

echo 3. Iniciando Servidor Streamlit...
echo.
echo    Acesse: http://localhost:8501
echo.
streamlit run web_app.py
pause
