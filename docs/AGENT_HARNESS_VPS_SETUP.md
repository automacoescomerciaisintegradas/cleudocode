# Agent Harness na VPS

Guia prático para usar este repositório como `agent harness` em uma VPS, com `browser-harness` como ferramenta opcional de navegador.

## Definição prática

Neste projeto, o `agent harness` é a camada de runtime que envolve o modelo e entrega quatro blocos operacionais:

- `Loop`: o agente recebe uma tarefa, observa, decide, age e reavalia.
- `Tools`: shell, leitura/escrita de arquivos e ferramentas externas como `browser-harness`.
- `Contexto`: repositório local, skills instaladas e configuração do provedor/modelo.
- `Controle`: configuração explícita, execução auditável no terminal e integração opcional com navegador separado.

Em termos de produto:

- `cleudocode` é o runtime principal do harness.
- `browser-harness` entra como ferramenta especializada para tarefas web.
- O modelo fica desacoplado do runtime; você pode trocar provider e modelo sem reescrever o harness.

## Premissas

- VPS Linux com `git`, `curl`, `python3` e `python3-venv`.
- Você quer rodar o harness a partir deste repositório, não via instalador externo de outro projeto.
- O arquivo `.env` será mantido na raiz do repositório.

## Instalação

### Caminho recomendado

Se você quer um setup rápido e repetível na VPS, use o script do repositório:

```bash
git clone https://github.com/automacoescomerciaisintegradas/cleudocode.git
cd cleudocode
bash install_vps.sh
```

Exemplo com provider/modelo definidos no próprio comando:

```bash
DEFAULT_PROVIDER=openrouter \
OPENROUTER_API_KEY=SUA_CHAVE \
DEFAULT_MODEL=SEU_MODELO_OPENROUTER \
bash install_vps.sh
```

O restante desta página descreve o fluxo manual equivalente.

O script `install_vps.sh` também tenta registrar `/usr/local/bin/cleudocode` quando executado com permissão suficiente, para o comando funcionar fora do shell ativado.

### 1. Preparar o runtime do Cleudocode

```bash
cd ~
git clone <URL_DO_SEU_REPOSITORIO_CLEUDOCODE> cleudocode
cd ~/cleudocode

python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Validação:

```bash
cleudocode --help
```

Observações:

- `pip install -e .` agora puxa as dependências do `requirements.txt`, então esse caminho manual instala também os módulos do gateway, dashboard e áudio.
- Se existir um `venv/` inválido trazido de outro host, remova-o antes e recrie com `python3 -m venv venv`.

### 2. Configurar o modelo

Se você quiser seguir o fluxo interativo:

```bash
cleudocode setup
```

Se preferir configuração objetiva por linha de comando, rode a partir da raiz do repositório:

```bash
cleudocode config set DEFAULT_PROVIDER openrouter
cleudocode config set OPENROUTER_API_KEY SUA_CHAVE
cleudocode config set OPENROUTER_MODEL SEU_MODELO_OPENROUTER
```

Inspeção rápida:

```bash
cleudocode config get DEFAULT_PROVIDER
cleudocode config get OPENROUTER_MODEL
```

Observação:

- `cleudocode config set` grava no `.env` do projeto atual.
- Se você executar o comando fora da raiz do repositório, vai alterar outro contexto de trabalho.

### 3. Instalar o Browser Harness

O `browser-harness` atual recomenda instalação editável com `uv tool install -e .`, mantendo o comando global e o checkout local editável.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env

cd ~
git clone https://github.com/browser-use/browser-harness
cd ~/browser-harness
uv tool install -e .
browser-harness --doctor
```

### 4. Registrar o Browser Harness como skill externa do Cleudocode

Este projeto descobre skills externas em `~/.cleudocode/skills/<nome>/`.

```bash
mkdir -p ~/.cleudocode/skills/browser-harness
ln -sf ~/browser-harness/SKILL.md ~/.cleudocode/skills/browser-harness/SKILL.md
ln -sf ~/browser-harness/install.md ~/.cleudocode/skills/browser-harness/install.md
ln -sf ~/browser-harness/interaction-skills ~/.cleudocode/skills/browser-harness/interaction-skills
ln -sf ~/browser-harness/agent-workspace ~/.cleudocode/skills/browser-harness/agent-workspace
```

Validação:

```bash
cleudocode skills
```

### 5. Configurar Browser Use Cloud, se necessário

Só é necessário para browser remoto/cloud. Para Chrome local com CDP, pule esta etapa.

```bash
cd ~/cleudocode
cleudocode config set BROWSER_USE_API_KEY SUA_CHAVE
```

Validação:

```bash
cleudocode config get BROWSER_USE_API_KEY
```

## Conexão com navegador

Você tem dois modos práticos:

### Modo local

Use o Chrome local com remote debugging habilitado. O fluxo canônico do `browser-harness` está em `install.md` do próprio projeto.

Teste mínimo:

```bash
browser-harness <<'PY'
print(page_info())
PY
```

Se falhar:

```bash
browser-harness --doctor
```

### Modo cloud

Se quiser rodar em VPS sem interface gráfica, use Browser Use Cloud com `BROWSER_USE_API_KEY`.

## Smoke test do harness

### Verificar runtime

```bash
cd ~/cleudocode
cleudocode doctor
cleudocode skills
```

### Verificar browser tool

```bash
browser-harness --doctor
```

### Verificar configuração do modelo

```bash
cleudocode config get DEFAULT_PROVIDER
cleudocode config get OPENROUTER_MODEL
```

## Como pensar a arquitetura

Se você quer que isso seja um `agent harness` de verdade, a separação prática fica assim:

- `Modelo`: OpenRouter, Anthropic, OpenAI, Ollama, etc.
- `Harness`: `cleudocode`
- `Ferramenta web`: `browser-harness`
- `Ambiente`: repositório, shell, arquivos, navegador
- `Controle`: verificações explícitas, contexto versionado e comandos auditáveis

## Diferenças em relação ao rascunho inicial

- Em vez de instalar um binário externo, este guia instala o `cleudocode` diretamente deste repositório com `pip install -e .`.
- O comando `cleudocode config set` é o caminho suportado para gravar segredos e parâmetros no `.env`.
- O registro de skill foi adaptado para `~/.cleudocode/skills`, que é o diretório que este projeto usa para skills externas.
- O fluxo do `browser-harness` foi atualizado para o modelo atual de instalação editável com `uv`.

## Próximo passo recomendado

Depois do setup, abra uma sessão do agente e teste uma tarefa curta e verificável, por exemplo:

- listar skills disponíveis
- ler um arquivo do repositório
- abrir uma página no navegador via `browser-harness`
- confirmar o resultado com saída de terminal ou screenshot
