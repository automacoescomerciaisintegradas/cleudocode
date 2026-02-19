# Guia de Instalação do Cleudocode

Este guia fornece instruções detalhadas para instalar e configurar o Cleudocode em diferentes ambientes: Windows, WSL e VPS.

## Sumário

1. [Instalação no Windows](#instalação-no-windows)
2. [Instalação no WSL](#instalação-no-wsl)
3. [Instalação em VPS](#instalação-em-vps)
4. [Configuração Inicial](#configuração-inicial)
5. [Execução](#execução)
6. [Solução de Problemas](#solução-de-problemas)

## Instalação no Windows

### Pré-requisitos

- Windows 10 ou superior (recomendado Windows 11)
- PowerShell como administrador
- Conexão com a internet

### Opção 1: Usando WSL (Recomendado)

O WSL (Windows Subsystem for Linux) oferece a melhor experiência para executar o Cleudocode no Windows.

#### Passo 1: Instale o WSL2

1. Abra o PowerShell como administrador
2. Execute o seguinte comando:
   ```powershell
   wsl --install
   ```

3. Reinicie seu computador quando solicitado

#### Passo 2: Configure o WSL2

1. Após a reinicialização, abra o WSL:
   ```bash
   wsl
   ```

2. Atualize o sistema:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. Siga as instruções da seção [Instalação no WSL](#instalação-no-wsl) abaixo

### Opção 2: Ambiente Nativo do Windows

#### Passo 1: Instale o Python

1. Acesse https://www.python.org/downloads/
2. Baixe a versão mais recente do Python 3.10 ou superior
3. Durante a instalação, marque a opção "Add Python to PATH"
4. Verifique a instalação:
   ```cmd
   python --version
   ```

#### Passo 2: Instale o Git

1. Acesse https://git-scm.com/download/win
2. Baixe e instale o Git para Windows
3. Verifique a instalação:
   ```cmd
   git --version
   ```

#### Passo 3: Clone o Repositório

1. Abra o Prompt de Comando ou PowerShell
2. Navegue até o diretório onde deseja instalar:
   ```cmd
   cd C:\Users\SeuUsuario\Documents
   ```

3. Clone o repositório:
   ```cmd
   git clone https://github.com/automacoescomerciaisintegradas/cleudocode.git
   cd cleudocode
   ```

#### Passo 4: Crie um Ambiente Virtual

```cmd
python -m venv venv
venv\Scripts\activate
```

#### Passo 5: Instale as Dependências

```cmd
pip install --upgrade pip
pip install flask flask-cors python-dotenv requests psutil pyyaml pypdf click colorama
```

## Instalação no WSL

### Passo 1: Atualize o Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### Passo 2: Instale as Dependências Básicas

```bash
sudo apt install python3 python3-pip python3-venv git curl wget -y
```

### Passo 3: Clone o Repositório

```bash
git clone https://github.com/automacoescomerciaisintegradas/cleudocode.git
cd cleudocode
```

### Passo 4: Crie um Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 5: Instale as Dependências

```bash
pip install --upgrade pip
pip install flask flask-cors python-dotenv requests psutil pyyaml pypdf click colorama
```

### Passo 6: Configure as Variáveis de Ambiente

```bash
cp .env.example .env
nano .env  # ou use seu editor preferido
```

## Instalação em VPS

### Passo 1: Conecte-se ao VPS

```bash
ssh usuario@seu-ip-do-vps
```

### Passo 2: Atualize o Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### Passo 3: Instale as Dependências

```bash
sudo apt install python3 python3-pip python3-venv git curl wget docker.io docker-compose -y
```

### Passo 4: Habilite e Inicie o Docker

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### Passo 5: Faça Logout e Login Novamente

```bash
exit
ssh usuario@seu-ip-do-vps
```

### Passo 6: Clone o Repositório

```bash
git clone https://github.com/automacoescomerciaisintegradas/cleudocode.git
cd cleudocode
```

### Passo 7: Crie um Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 8: Instale as Dependências

```bash
pip install --upgrade pip
pip install flask flask-cors python-dotenv requests psutil pyyaml pypdf click colorama
```

### Passo 9: Configure as Variáveis de Ambiente

```bash
cp .env.example .env
nano .env
```

### Passo 10: Configuração de Produção com PM2

```bash
# Instale o PM2 globalmente
npm install -g pm2

# Inicie a aplicação com PM2
pm2 start web_server.py --name cleudocode --interpreter python -- --host=0.0.0.0 --port=8501

# Salve a configuração do PM2
pm2 save

# Faça o PM2 iniciar automaticamente com o sistema
pm2 startup
```

## Configuração Inicial

### Configuração Automática

Use o script de setup automatizado:

```bash
# No diretório do projeto
chmod +x setup.sh
./setup.sh
```

### Configuração Manual

1. Copie o arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```

2. Edite o arquivo `.env` com suas credenciais:
   ```bash
   nano .env
   ```

3. Configure as seguintes variáveis:

   - `TELEGRAM_BOT_TOKEN`: Token do seu bot Telegram (@BotFather)
   - `TELEGRAM_USER_ID`: Seu ID do Telegram (@userinfobot)
   - `GOOGLE_API_KEY`: Chave da API do Google Gemini
   - `ANTHROPIC_API_KEY`: Chave da API da Anthropic (opcional)
   - `OPENAI_API_KEY`: Chave da API da OpenAI (opcional)
   - `OLLAMA_HOST`: URL do servidor Ollama (se estiver usando local)

## Execução

### Execução Local (Ambiente Virtual)

```bash
cd cleudocode
source venv/bin/activate  # Linux/WSL
# ou
venv\Scripts\activate     # Windows

# Execute o servidor web
PORT=8501 python web_server.py
```

### Execução com Docker (WSL/VPS)

```bash
cd cleudocode

# Construa e inicie os containers
docker compose up --build -d

# Verifique o status
docker compose ps

# Veja os logs
docker logs cleudocode-gateway
```

### Execução com CLI

```bash
# Iniciar o servidor
python cli/main.py start

# Abrir o dashboard
python cli/main.py dashboard

# Iniciar um chat interativo
python cli/main.py chat

# Verificar o status do sistema
python cli/main.py status
```

## Solução de Problemas

### Problemas Comuns

#### 1. Portas já em uso

- Verifique se não há outros processos usando as portas 8501, 8000, etc.
- Use `netstat -tuln` ou `lsof -i :porta` para verificar portas

#### 2. Permissões no Docker (Linux/VPS)

- Certifique-se de que seu usuário está no grupo docker:
  ```bash
  sudo usermod -aG docker $USER
  ```
- Faça logout/login novamente

#### 3. Dependências faltando

- Execute `pip install -r requirements.txt` novamente
- Verifique se está usando o ambiente virtual correto

#### 4. Variáveis de ambiente não reconhecidas

- Verifique se o arquivo `.env` está configurado corretamente
- Confirme que o `.env` está no diretório raiz do projeto

### Comandos de Diagnóstico

```bash
# Verifique o status do sistema
python cli/main.py doctor

# Verifique o status dos containers (se usando Docker)
docker compose ps

# Verifique os logs (se usando Docker)
docker logs cleudocode-gateway

# Verifique o status do PM2 (se usando PM2)
pm2 status
```

### Restauração

Se ocorrerem problemas graves, você pode restaurar o ambiente:

```bash
# Remova o ambiente virtual
rm -rf venv

# Recrie o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Reinstale as dependências
pip install --upgrade pip
pip install flask flask-cors python-dotenv requests psutil pyyaml pypdf click colorama
```

## Segurança

- Mantenha seu arquivo `.env` seguro e fora do controle de versão
- Use senhas fortes e renove chaves de API periodicamente
- Mantenha seu sistema e dependências atualizados
- Use firewall para restringir acesso às portas internas
- Configure o acesso SSH de forma segura em servidores VPS

## Atualização

Para atualizar para a versão mais recente:

```bash
# Salve alterações personalizadas (se houver)
git stash

# Atualize o repositório
git pull origin main

# Reinstale dependências (se necessário)
pip install -r requirements.txt

# Restaure alterações personalizadas (se houver)
git stash pop
```

---

© **Automações Comerciais Integradas! 2026** ⚙️ Todos os direitos reservados.
[contato@automacoescomerciais.com.br](mailto:contato@automacoescomerciais.com.br)
[GitHub Cleudocode](https://github.com/automacoescomerciaisintegradas/cleudocode)