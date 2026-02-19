# Cleudocode
### The AI that actually does things.

**Cleudocode** é a sua ferramenta exclusiva para gerenciamento de projetos, criação de sistemas e execução de tarefas reais. Tudo operando de forma local, privada e com 100% de controle nas suas mãos.

Você envia mensagens. O Cleudocode executa. Texto, fotos, documentos, voz. Ele lembra das sessões, faz check-ins proativos e roda em background.

**Desenvolvido por [Automações Comerciais Integradas! 2026](https://youtube.com/@CurtirComentarCompartinhar)** | [Comunidade AI Productivity Hub](https://cleudocode.automacoescomerciais.com.br/comunidade)

```
Você ──▶ Telegram ──▶ Relay ──▶ Cleudocode CLI ──▶ Resposta (Execução Real)
                                     │
                               Supabase (Memória Local)
```

## O Que Você Recebe

- **Execução Real**: Gerencia projetos e cria sistemas via CLI.
- **Relay Exclusivo**: Suas mensagens do Telegram enviadas direto para o motor Cleudocode.
- **Memória Semântica**: Busca inteligente sobre o histórico via Supabase.
- **Voz**: Transcrição de áudio via Gemini ou Whisper local.
- **Privacidade Total**: Runa em ambiente local sob seu comando.

## Instalação e Uso

### Instalação no Windows

#### Opção 1: Usando WSL (Recomendado)

1. **Instale o WSL2**:
   ```powershell
   wsl --install
   ```

2. **Atualize para WSL2** (caso ainda não esteja):
   ```powershell
   wsl --set-default-version 2
   ```

3. **Abra o WSL e siga as instruções do ambiente Linux** (abaixo).

#### Opção 2: Ambiente Nativo do Windows

1. **Instale o Python 3.10+**:
   - Baixe em https://www.python.org/downloads/
   - Marque "Add Python to PATH" durante a instalação

2. **Instale o Git**:
   - Baixe em https://git-scm.com/download/win

3. **Clone o repositório**:
   ```cmd
   git clone https://github.com/automacoescomerciaisintegradas/cleudocode.git
   cd cleudocode
   ```

4. **Crie um ambiente virtual**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Instale as dependências**:
   ```cmd
   pip install --upgrade pip
   pip install -r requirements.txt
   # Ou instale manualmente:
   pip install flask flask-cors python-dotenv requests psutil pyyaml pypdf
   ```

### Instalação no WSL (Linux Subsystem for Windows)

1. **Atualize o sistema**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Instale dependências básicas**:
   ```bash
   sudo apt install python3 python3-pip python3-venv git curl wget -y
   ```

3. **Clone o repositório**:
   ```bash
   git clone https://github.com/automacoescomerciaisintegradas/cleudocode.git
   cd cleudocode
   ```

4. **Crie um ambiente virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Instale as dependências**:
   ```bash
   pip install --upgrade pip
   pip install flask flask-cors python-dotenv requests psutil pyyaml pypdf
   ```

6. **Configure as variáveis de ambiente**:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   nano .env
   ```

### Instalação em VPS (Ubuntu/Debian)

1. **Conecte-se ao seu servidor VPS** via SSH:
   ```bash
   ssh usuario@seu-ip-do-vps
   ```

2. **Atualize o sistema**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Instale dependências necessárias**:
   ```bash
   sudo apt install python3 python3-pip python3-venv git curl wget docker.io docker-compose -y
   ```

4. **Habilite e inicie o Docker**:
   ```bash
   sudo systemctl enable docker
   sudo systemctl start docker
   sudo usermod -aG docker $USER
   ```

5. **Faça logout e login novamente** para que as permissões do Docker sejam aplicadas:
   ```bash
   exit
   # Conecte-se novamente ao servidor
   ssh usuario@seu-ip-do-vps
   ```

6. **Clone o repositório**:
   ```bash
   git clone https://github.com/automacoescomerciaisintegradas/cleudocode.git
   cd cleudocode
   ```

7. **Crie um ambiente virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

8. **Instale as dependências**:
   ```bash
   pip install --upgrade pip
   pip install flask flask-cors python-dotenv requests psutil pyyaml pypdf
   ```

9. **Configure as variáveis de ambiente**:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   nano .env
   ```

## Configuração Inicial

### Configuração Automática (Todos os Ambientes)

```bash
cd cleudocode
# Ative o ambiente virtual se necessário
source venv/bin/activate  # Linux/WSL
# ou
venv\Scripts\activate     # Windows

# Execute o script de setup
python cli/main.py init
# ou
python cli/main.py onboard
```

### Configuração Manual

1. **Copie o arquivo .env.example para .env**:
   ```bash
   cp .env.example .env
   ```

2. **Edite o arquivo .env** com suas credenciais:
   ```bash
   nano .env
   ```
   
   Configure as seguintes variáveis:
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

# Ou use o CLI
python cli/main.py start
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

### Execução com PM2 (Produção em VPS)

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

## Comandos Principais

```bash
# Iniciar o servidor
python cli/main.py start

# Abrir o dashboard
python cli/main.py dashboard

# Executar um agente
python cli/main.py agent --message "Sua mensagem aqui"

# Iniciar um chat interativo
python cli/main.py chat

# Verificar o status do sistema
python cli/main.py status

# Executar o diagnóstico
python cli/main.py doctor

# Iniciar o setup
python cli/main.py init
```

## Configuração de Gateways

### Telegram
1. Crie um bot com [@BotFather](https://t.me/BotFather) no Telegram
2. Obtenha o token do bot
3. Adicione ao seu `.env` como `TELEGRAM_BOT_TOKEN`
4. Obtenha seu ID de usuário com [@userinfobot](https://t.me/userinfobot)
5. Adicione ao seu `.env` como `TELEGRAM_USER_ID`

### WhatsApp (Evolution API)
1. Configure uma instância Evolution API
2. Obtenha o token da instância
3. Configure as variáveis `WHATSAPP_BASE_URL`, `WHATSAPP_API_TOKEN_INSTANCE` e `WHATSAPP_INSTANCE_NAME` no `.env`

## Solução de Problemas

### Problemas Comuns

1. **Portas já em uso**:
   - Verifique se não há outros processos usando as portas 8501, 8000, etc.
   - Use `netstat -tuln` ou `lsof -i :porta` para verificar portas

2. **Permissões no Docker (Linux/VPS)**:
   - Certifique-se de que seu usuário está no grupo docker: `sudo usermod -aG docker $USER`
   - Faça logout/login novamente

3. **Dependências faltando**:
   - Execute `pip install -r requirements.txt` novamente
   - Verifique se está usando o ambiente virtual correto

4. **Variáveis de ambiente não reconhecidas**:
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

## Segurança

- Mantenha seu arquivo `.env` seguro e fora do controle de versão
- Use senhas fortes e renove chaves de API periodicamente
- Mantenha seu sistema e dependências atualizados
- Use firewall para restringir acesso às portas internas

## Contribuição

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Faça commit de suas alterações (`git commit -m 'Add NovaFeature'`)
4. Faça push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

© **Automações Comerciais Integradas! 2026** ⚙️ Todos os direitos reservados.
[contato@automacoescomerciais.com.br](mailto:contato@automacoescomerciais.com.br)
[GitHub Cleudocode](https://github.com/automacoescomerciaisintegradas/cleudocode)