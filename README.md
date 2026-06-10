# Cleudocode Agent Harness

Cleudocode e um `agent harness` para tarefas de engenharia de software. O modelo fica desacoplado do runtime; o harness entrega loop de execucao, ferramentas, contexto e controles operacionais.

## O que existe aqui

- `cleudocode`: runtime principal do agente
- `browser-harness`: ferramenta opcional para automacao web via Chrome/CDP
- `docs/AGENT_HARNESS_VPS_SETUP.md`: guia manual completo
- `install_vps.sh`: instalador idempotente para VPS

## Quick Start na VPS

Clone o repositorio e rode o instalador:

```bash
git clone https://github.com/automacoescomerciaisintegradas/cleudocode.git
cd cleudocode
bash install_vps.sh
```

Exemplo com provider ja definido:

```bash
DEFAULT_PROVIDER=openrouter \
OPENROUTER_API_KEY=SUA_CHAVE \
DEFAULT_MODEL=SEU_MODELO_OPENROUTER \
bash install_vps.sh
```

Se quiser pular o browser tool:

```bash
INSTALL_BROWSER_HARNESS=0 bash install_vps.sh
```

## O que o instalador faz

- instala dependencias basicas de sistema via `apt-get`
- clona ou atualiza este repositorio
- cria `venv` e instala o pacote com `pip install -e .`
- instala `browser-harness` com `uv`, se habilitado
- registra `browser-harness` em `~/.cleudocode/skills/browser-harness`
- grava configuracao no `.env` do projeto via `cleudocode config set`

## Depois da instalacao

```bash
source venv/bin/activate
cleudocode doctor
cleudocode skills
cleudocode setup
```

## Documentacao

- Guia manual: [docs/AGENT_HARNESS_VPS_SETUP.md](docs/AGENT_HARNESS_VPS_SETUP.md)
- CLI: [CLI_README.md](CLI_README.md)
- Producao legada: [README_PRODUCAO.md](README_PRODUCAO.md)

## Observacoes

- O comando `cleudocode config set` grava no `.env` da raiz do repositorio atual.
- O `browser-harness` so precisa de `BROWSER_USE_API_KEY` se voce for usar browser remoto/cloud.
- Para Chrome local, siga o fluxo de remote debugging do proprio `browser-harness`.
