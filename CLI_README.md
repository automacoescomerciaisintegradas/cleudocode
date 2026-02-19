# CLI do Cleudocode

O CLI (Interface de Linha de Comando) do Cleudocode fornece uma maneira eficiente de interagir com a plataforma a partir do terminal.

## Instalação

O CLI é parte integrante do projeto Cleudocode e pode ser acessado após a instalação completa do sistema.

### Instalação Automática

Use o script de setup para instalar automaticamente:

**No Linux/WSL:**
```bash
chmod +x setup.sh
./setup.sh
```

**No Windows:**
```cmd
setup.bat
```

### Instalação Manual

1. Clone o repositório:
   ```bash
   git clone https://github.com/automacoescomerciaisintegradas/cleudocode.git
   cd cleudocode
   ```

2. Crie um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/WSL
   # ou
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install flask flask-cors python-dotenv requests psutil pyyaml pypdf click colorama
   ```

## Comandos Disponíveis

### Comandos Principais

- `cleudocode init` - Inicia o assistente de configuração interativo
- `cleudocode setup` - Alias para o comando init
- `cleudocode start` - Inicia os serviços do Cleudocode
- `cleudocode stop` - Para os serviços do Cleudocode
- `cleudocode dashboard` - Abre o dashboard de controle
- `cleudocode chat` - Inicia um chat interativo com o sistema AI
- `cleudocode agent` - Interage com um agente específico
- `cleudocode status` - Mostra o status detalhado dos agentes e sistema
- `cleudocode doctor` - Executa verificações de saúde do sistema
- `cleudocode health` - Alias para o comando doctor

### Comandos de Gerenciamento

- `cleudocode plugins enable <nome>` - Habilita um plugin específico
- `cleudocode models auth login --provider <provedor>` - Faz login em provedores de modelo
- `cleudocode memory export` - Exporta a memória do sistema para uso em outras aplicações

### Comandos de Desenvolvedor

- `cleudocode acp` - Ferramentas de Protocolo de Controle de Agente
- `cleudocode agents` - Gerencia agentes isolados
- `cleudocode approvals` - Sistema de aprovações de execução
- `cleudocode cron` - Agendador de tarefas cron
- `cleudocode config` - Gerencia configurações (get/set/unset)
- `cleudocode daemon` - Serviço de gateway legado
- `cleudocode devices` - Gerenciamento de dispositivos e tokens
- `cleudocode directory` - Comandos de diretório
- `cleudocode dns` - Ferramentas de DNS
- `cleudocode docs` - Documentação
- `cleudocode hooks` - Ferramentas de hooks
- `cleudocode logs` - Visualiza logs do gateway
- `cleudocode node` - Controle de nó
- `cleudocode nodes` - Comandos de nós
- `cleudocode pairing` - Ferramentas de pareamento
- `cleudocode reset` - Redefine configurações locais
- `cleudocode sandbox` - Ferramentas de sandbox
- `cleudocode security` - Ferramentas de segurança
- `cleudocode sessions` - Lista sessões de conversa armazenadas
- `cleudocode skills` - Gerenciamento de habilidades
- `cleudocode system` - Eventos e presença do sistema
- `cleudocode tui` - Interface de terminal (em desenvolvimento)
- `cleudocode uninstall` - Desinstala o serviço de gateway
- `cleudocode update` - Atualizações de CLI
- `cleudocode webhooks` - Ferramentas de webhook

## Configuração Inicial

Após a instalação, execute o assistente de configuração:

```bash
python cli/main.py init
```

O assistente irá:
1. Criar o arquivo .env se não existir
2. Solicitar suas credenciais e configurações
3. Configurar os gateways de comunicação
4. Testar as conexões

## Variáveis de Ambiente

O CLI depende de várias variáveis de ambiente definidas no arquivo `.env`:

- `TELEGRAM_BOT_TOKEN` - Token do bot do Telegram
- `TELEGRAM_USER_ID` - ID do usuário autorizado no Telegram
- `GOOGLE_API_KEY` - Chave da API do Google Gemini
- `ANTHROPIC_API_KEY` - Chave da API da Anthropic (opcional)
- `OPENAI_API_KEY` - Chave da API da OpenAI (opcional)
- `OLLAMA_HOST` - URL do servidor Ollama local
- `WHATSAPP_API_TOKEN_INSTANCE` - Token da instância WhatsApp Evolution API
- `CLEUDOCODE_GATEWAY_TOKEN` - Token de autenticação do gateway

## Exemplos de Uso

### Iniciar o sistema
```bash
python cli/main.py start
```

### Iniciar um chat interativo
```bash
python cli/main.py chat
```

### Verificar o status do sistema
```bash
python cli/main.py status
```

### Executar diagnóstico
```bash
python cli/main.py doctor
```

### Habilitar um plugin
```bash
python cli/main.py plugins enable nome-do-plugin
```

## Solução de Problemas

Se encontrar problemas com o CLI:

1. Verifique se o ambiente virtual está ativado
2. Confirme que todas as dependências estão instaladas
3. Execute o comando `doctor` para verificações de saúde:
   ```bash
   python cli/main.py doctor
   ```

4. Verifique o arquivo `.env` para credenciais válidas

## Personalização

O CLI pode ser personalizado adicionando novos comandos. Para adicionar um novo comando:

1. Crie uma função no arquivo `cli/main.py` decorada com `@cli.command()`
2. Adicione os argumentos necessários com `@click.option()` ou `@click.argument()`
3. Implemente a lógica do comando na função

## Contribuição

Para contribuir com o CLI:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Adicione seu comando ou modificação
4. Teste cuidadosamente
5. Faça commit (`git commit -m 'Adiciona NovaFuncionalidade'`)
6. Faça push (`git push origin feature/NovaFuncionalidade`)
7. Abra um Pull Request

---

© **Automações Comerciais Integradas! 2026** ⚙️ Todos os direitos reservados.
[contato@automacoescomerciais.com.br](mailto:contato@automacoescomerciais.com.br)
[GitHub Cleudocode](https://github.com/automacoescomerciaisintegradas/cleudocode)