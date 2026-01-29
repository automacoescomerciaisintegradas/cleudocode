# Plano de Implementação: Arquitetura Gateway v2 e Daemon

## 1. Visão Geral
Este documento define o roteiro para implementar a arquitetura de "Gateway (Control Plane)" baseada em WebSocket (porta 18789) e o comando de instalação do daemon `onboard --install-daemon`.
O objetivo é centralizar a comunicação entre diferentes clientes (CLI, WebChat, Pi Agent, Apps Móveis) através de um barramento WebSocket unificado gerido pelo daemon do Cleudocodebot.

## 2. Arquitetura Proposta

### Componentes
1.  **Daemon Central (`run_daemon.py`)**:
    *   Núcleo do sistema (`CleudoDaemon`) que gerencia a vida útil dos gateways.
    *   Deve inicializar o novo **WebSocket Control Gateway**.
2.  **WebSocket Control Gateway (`gateways/websocket_gateway.py`)**:
    *   Servidor WebSocket ouvindo em `127.0.0.1:18789`.
    *   Protocolo RPC para comandos (e.g., `send_message`, `get_status`).
    *   Autenticação básica (Token/Chave via `.env`).
3.  **CLI (`cleudocodebot`)**:
    *   Novo comando: `onboard --install-daemon`.
    *   Função: Configurar a persistência do daemon no sistema operacional (Windows Service ou Inicialização Automática).

### Fluxo de Dados
[Cliente] <-> (WebSocket JSON-RPC) <-> [Gateway 18789] <-> [Daemon Router] <-> [Integrações (WhatsApp, etc)]

## 3. Roteiro de Implementação Passo a Passo

### Fase 1: Fundação do Gateway WebSocket
*Objetivo: Criar o servidor que aceita conexões dos clientes.*
1.  **Criar `gateways/websocket_control.py`**:
    *   Implementar classe `WebSocketControlGateway` herdando de uma interface base de gateway.
    *   Utilizar `websockets` ou `aiohttp` (assíncrono) para servir na porta 18789.
    *   Definir estrutura de mensagens JSON (e.g., `{"type": "command", "action": "send", "payload": ...}`).
2.  **Atualizar `run_daemon.py`**:
    *   Importar e instanciar `WebSocketControlGateway`.
    *   Adicioná-lo ao `daemon` durante o setup.

### Fase 2: Atualização da CLI e Onboarding
*Objetivo: Permitir que o usuário instale e gerencie o daemon facilmente.*
1.  **Atualizar `cli/main.py`**:
    *   Adicionar flag `--install-daemon` ao comando `onboard`.
    *   Exemplo: `@click.option('--install-daemon', is_flag=True, help='Instala o daemon como serviço de sistema')`
2.  **Atualizar `cli/onboard.py`**:
    *   Implementar lógica para `install_daemon()`:
        *   **Windows**: Criar um arquivo `.bat` de inicialização robusto e, opcionalmente, adicionar ao Registro de "Run" ou criar uma Tarefa Agendada via PowerShell.
        *   **Configuração**: Garantir que o `.env` tenha as configurações necessárias para o WebSocket (porta, token).

### Fase 3: Integração e Testes
*Objetivo: Validar se a arquitetura funciona conforme o diagrama.*
1.  **Teste de Conexão**:
    *   Criar script de teste `scripts/test_ws_connection.py` que conecta no `ws://127.0.0.1:18789` e envia um "ping".
2.  **Teste de Comando CLI**:
    *   Executar `cleudocodebot onboard --install-daemon --force`.
    *   Verificar se o daemon inicia corretamente após a instalação.

## 4. Dependências e Requisitos
*   Biblioteca `websockets` (adicionar ao `setup.py` se necessário).
*   Permissões de Administrador podem ser necessárias para `--install-daemon` no Windows (para tarefas agendadas).

## 5. Critérios de Aceite
*   [ ] O daemon escuta na porta 18789.
*   [ ] O comando `cleudocodebot onboard --install-daemon` executa sem erros.
*   [ ] Um cliente externo (ex: script Python simples) consegue conectar e trocar mensagens com o Gateway.
