# Production Deployment for CleudoCode

## Python Setup (Recommended for Local/Server)
1. Ensure Python 3.10+ is installed.
2. Run the production setup script:
   ```bash
   python agent-browser/scripts/setup_production.py
   ```

## Docker Deployment (Recomendado para Cloud)
Use o arquivo `Dockerfile.production` para criar sua imagem. Ele já vem com todas as dependências do Playwright pré-instaladas.

```bash
docker build -t cleudocode-prod -f Dockerfile.production .
docker run -p 8501:8501 cleudocode-prod
```

## CI/CD com GitHub Actions
O arquivo `.github/workflows/main.yml` automatiza:
1. Instalação do Python e dependências.
2. Instalação do navegador Chromium no servidor de build.
3. (Opcional) Build e Push da imagem para o Docker Hub.

## Environment Variables
Ensure the following are set in your production environment:
- `AGENT_BROWSER_SESSION=prod_session`
- `PLAYWRIGHT_BROWSERS_PATH=0` (to keep browsers inside the container)
