# Plano de Melhorias para o Ambiente Docker do CleudoCode

Este documento descreve uma série de melhorias para a arquitetura Docker do projeto CleudoCode, inspiradas em práticas de mercado para sistemas baseados em agentes. O objetivo é aumentar a segurança, modularidade, e eficiência do ambiente de desenvolvimento e produção.

## 1. Visão Geral da Nova Arquitetura

A principal mudança é a introdução de um serviço "sandbox" dedicado para a execução de agentes. A arquitetura será composta por:

1.  **Serviço Principal (`cleudocode`):** Responsável pela interface do usuário (Streamlit), gerenciamento de estado e orquestração de tarefas.
2.  **Serviço de Agente (`agent-sandbox`):** Um contêiner isolado e sem privilégios que recebe tarefas do serviço principal, executa o código do agente e retorna o resultado. Ele não terá portas expostas e sua única comunicação com o exterior será através de um volume compartilhado ou um sistema de mensageria.
3.  **Rede Docker:** Uma rede privada para a comunicação entre os serviços.

## 2. Plano de Implementação

### Tarefa 1: Isolar a Execução de Agentes com um Sandbox

**Objetivo:** Proteger o serviço principal e o sistema hospedeiro de códigos potencialmente inseguros executados pelos agentes.

**Passos:**

1.  **Criar um novo `Dockerfile.sandbox`:** Este arquivo definirá um ambiente mínimo para o agente, contendo apenas as dependências necessárias para a execução das tarefas.
2.  **Atualizar o `docker-compose.yml`:**
    *   Adicionar um novo serviço chamado `agent-sandbox` que utilizará o `Dockerfile.sandbox`.
    *   Este serviço não terá portas expostas.
    *   Configurar um volume compartilhado (ex: `./sandbox_io`) para a comunicação entre o serviço `cleudocode` e o `agent-sandbox`. O serviço principal escreverá as "tarefas" neste volume, e o sandbox lerá, executará e escreverá o "resultado" de volta.

### Tarefa 2: Otimizar o `Dockerfile` Principal

**Objetivo:** Melhorar o tempo de build e diminuir o tamanho da imagem Docker.

**Passos:**

1.  **Otimizar o cache de camadas:** Em vez de usar `COPY . .`, copiaremos explicitamente apenas os diretórios e arquivos necessários para a aplicação (`app.py`, `web_app.py`, os diretórios `core`, `skills`, etc.).
2.  **Utilizar um arquivo `.dockerignore` mais robusto:** Garantir que arquivos como `.git`, `venv`, `__pycache__`, `.pytest_cache` e `node_modules` não sejam copiados para o contexto de build.

### Tarefa 3: Criar um Script de Setup Unificado

**Objetivo:** Simplificar e automatizar o processo de configuração e inicialização do ambiente.

**Passos:**

1.  **Criar um script `setup.bat` (ou `setup.sh`):**
    *   Verificar se o Docker está em execução.
    *   Criar os diretórios necessários (`exports`, `uploads`, etc.) se não existirem.
    *   Copiar `.env.example` para `.env` se o `.env` não existir.
    *   Executar `docker-compose build` para construir as imagens.
    *   Executar `docker-compose up -d` para iniciar os serviços.

## 3. Próximos Passos (Implementação)

A seguir, apresento as alterações de código propostas para os arquivos.

1.  **Criar `Dockerfile.sandbox`**.
2.  **Modificar `docker-compose.yml`**.
3.  **Modificar `Dockerfile`**.

Vamos começar a implementação.
