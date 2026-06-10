#!/usr/bin/env bash

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/automacoescomerciaisintegradas/cleudocode.git}"
BRANCH="${BRANCH:-main}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/cleudocode}"
VENV_DIR="${VENV_DIR:-$INSTALL_DIR/venv}"
BROWSER_HARNESS_DIR="${BROWSER_HARNESS_DIR:-$HOME/browser-harness}"
INSTALL_BROWSER_HARNESS="${INSTALL_BROWSER_HARNESS:-1}"
INSTALL_SYSTEM_DEPS="${INSTALL_SYSTEM_DEPS:-1}"
RUN_SMOKE_TESTS="${RUN_SMOKE_TESTS:-1}"

DEFAULT_PROVIDER="${DEFAULT_PROVIDER:-}"
DEFAULT_MODEL="${DEFAULT_MODEL:-}"
OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}"
OPENROUTER_MODEL="${OPENROUTER_MODEL:-}"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
OPENAI_MODEL="${OPENAI_MODEL:-}"
OLLAMA_MODEL="${OLLAMA_MODEL:-}"
OLLAMA_HOST="${OLLAMA_HOST:-}"
BROWSER_USE_API_KEY="${BROWSER_USE_API_KEY:-}"

export PATH="$HOME/.local/bin:$PATH"

APT_PACKAGES=(
  git
  curl
  python3
  python3-pip
  python3-venv
)

log() {
  printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1
}

run_as_root() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  elif need_cmd sudo; then
    sudo "$@"
  else
    log "Comando requer privilegios e sudo nao esta disponivel: $*"
    exit 1
  fi
}

install_system_deps() {
  if [[ "${INSTALL_SYSTEM_DEPS}" != "1" ]]; then
    log "Pulando dependencias de sistema."
    return
  fi

  if ! need_cmd apt-get; then
    log "apt-get nao encontrado. Instale manualmente: ${APT_PACKAGES[*]}"
    return
  fi

  log "Instalando dependencias de sistema..."
  run_as_root apt-get update
  run_as_root apt-get install -y "${APT_PACKAGES[@]}"
}

ensure_repo() {
  if [[ -d "${INSTALL_DIR}/.git" ]]; then
    log "Atualizando repositorio existente em ${INSTALL_DIR}..."
    git -C "${INSTALL_DIR}" fetch --all --prune
    git -C "${INSTALL_DIR}" checkout "${BRANCH}"
    git -C "${INSTALL_DIR}" pull --ff-only origin "${BRANCH}"
  else
    log "Clonando repositorio em ${INSTALL_DIR}..."
    git clone --branch "${BRANCH}" "${REPO_URL}" "${INSTALL_DIR}"
  fi
}

ensure_venv() {
  log "Criando ou reutilizando ambiente virtual..."
  python3 -m venv "${VENV_DIR}"

  # shellcheck disable=SC1090
  source "${VENV_DIR}/bin/activate"

  python -m pip install --upgrade pip

  if [[ -f "${INSTALL_DIR}/requirements.txt" ]]; then
    python -m pip install -r "${INSTALL_DIR}/requirements.txt"
  fi

  python -m pip install -e "${INSTALL_DIR}"
}

ensure_uv() {
  if need_cmd uv; then
    return
  fi

  log "Instalando uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
}

ensure_browser_harness() {
  if [[ "${INSTALL_BROWSER_HARNESS}" != "1" ]]; then
    log "Pulando browser-harness."
    return
  fi

  ensure_uv

  if [[ -d "${BROWSER_HARNESS_DIR}/.git" ]]; then
    log "Atualizando browser-harness em ${BROWSER_HARNESS_DIR}..."
    git -C "${BROWSER_HARNESS_DIR}" pull --ff-only
  else
    log "Clonando browser-harness em ${BROWSER_HARNESS_DIR}..."
    git clone https://github.com/browser-use/browser-harness "${BROWSER_HARNESS_DIR}"
  fi

  log "Instalando browser-harness em modo editavel..."
  uv tool install -e "${BROWSER_HARNESS_DIR}"

  log "Registrando browser-harness como skill externa..."
  mkdir -p "$HOME/.cleudocode/skills/browser-harness"
  ln -sf "${BROWSER_HARNESS_DIR}/SKILL.md" "$HOME/.cleudocode/skills/browser-harness/SKILL.md"
  ln -sf "${BROWSER_HARNESS_DIR}/install.md" "$HOME/.cleudocode/skills/browser-harness/install.md"
  ln -sf "${BROWSER_HARNESS_DIR}/interaction-skills" "$HOME/.cleudocode/skills/browser-harness/interaction-skills"
  ln -sf "${BROWSER_HARNESS_DIR}/agent-workspace" "$HOME/.cleudocode/skills/browser-harness/agent-workspace"
}

set_config_if_present() {
  local key="$1"
  local value="$2"

  if [[ -n "${value}" ]]; then
    "${VENV_DIR}/bin/cleudocode" config set "${key}" "${value}"
  fi
}

configure_runtime() {
  log "Aplicando configuracao do harness..."
  cd "${INSTALL_DIR}"

  set_config_if_present "DEFAULT_PROVIDER" "${DEFAULT_PROVIDER}"
  set_config_if_present "OPENROUTER_API_KEY" "${OPENROUTER_API_KEY}"
  set_config_if_present "OPENROUTER_MODEL" "${OPENROUTER_MODEL}"
  set_config_if_present "ANTHROPIC_API_KEY" "${ANTHROPIC_API_KEY}"
  set_config_if_present "ANTHROPIC_MODEL" "${ANTHROPIC_MODEL}"
  set_config_if_present "OPENAI_API_KEY" "${OPENAI_API_KEY}"
  set_config_if_present "OPENAI_MODEL" "${OPENAI_MODEL}"
  set_config_if_present "OLLAMA_MODEL" "${OLLAMA_MODEL}"
  set_config_if_present "OLLAMA_HOST" "${OLLAMA_HOST}"
  set_config_if_present "BROWSER_USE_API_KEY" "${BROWSER_USE_API_KEY}"

  if [[ -n "${DEFAULT_MODEL}" ]]; then
    case "${DEFAULT_PROVIDER}" in
      openrouter) set_config_if_present "OPENROUTER_MODEL" "${DEFAULT_MODEL}" ;;
      anthropic) set_config_if_present "ANTHROPIC_MODEL" "${DEFAULT_MODEL}" ;;
      openai) set_config_if_present "OPENAI_MODEL" "${DEFAULT_MODEL}" ;;
      ollama) set_config_if_present "OLLAMA_MODEL" "${DEFAULT_MODEL}" ;;
    esac
  fi
}

run_smoke_tests() {
  if [[ "${RUN_SMOKE_TESTS}" != "1" ]]; then
    log "Pulando smoke tests."
    return
  fi

  log "Executando smoke tests..."
  cd "${INSTALL_DIR}"
  "${VENV_DIR}/bin/python" cli/main.py config --help >/dev/null
  "${VENV_DIR}/bin/cleudocode" skills >/dev/null || true

  if [[ "${INSTALL_BROWSER_HARNESS}" == "1" ]] && need_cmd browser-harness; then
    browser-harness --doctor >/dev/null || true
  fi
}

print_summary() {
  cat <<EOF

Instalacao concluida.

Repositorio:      ${INSTALL_DIR}
Virtualenv:       ${VENV_DIR}
Provider padrao:  ${DEFAULT_PROVIDER:-nao definido}
Browser harness:  $([[ "${INSTALL_BROWSER_HARNESS}" == "1" ]] && echo "instalado" || echo "desativado")

Proximos passos:
  1. source "${VENV_DIR}/bin/activate"
  2. cd "${INSTALL_DIR}"
  3. cleudocode doctor
  4. cleudocode skills
  5. cleudocode setup   # opcional, se voce quiser completar configuracao interativa

Documentacao:
  - ${INSTALL_DIR}/README.md
  - ${INSTALL_DIR}/docs/AGENT_HARNESS_VPS_SETUP.md

Exemplo com OpenRouter:
  DEFAULT_PROVIDER=openrouter \\
  OPENROUTER_API_KEY=... \\
  DEFAULT_MODEL=anthropic/claude-opus-4.1 \\
  bash install_vps.sh

EOF
}

main() {
  log "Iniciando setup do Cleudocode Agent Harness na VPS..."
  install_system_deps
  ensure_repo
  ensure_venv
  ensure_browser_harness
  configure_runtime
  run_smoke_tests
  print_summary
}

main "$@"
