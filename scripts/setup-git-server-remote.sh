#!/usr/bin/env bash

set -Eeuo pipefail

###############################################################################
# setup-git-server-remote.sh
#
# Runs scripts/setup-git-server.sh on a remote host as root via SSH.
#
# Usage:
#   bash scripts/setup-git-server-remote.sh
#   bash scripts/setup-git-server-remote.sh --host 185.190.143.17 --admin-user devops --create-admin
#   bash scripts/setup-git-server-remote.sh --pubkey-file ~/.ssh/id_ed25519.pub
###############################################################################

HOST="185.190.143.17"
PORT="22"
IDENTITY_FILE=""
ROOT_USER="root"
ADMIN_USER="devops"
CREATE_ADMIN="false"
PUBKEY=""
PUBKEY_FILE=""

log() {
  printf '[setup-git-server-remote] %s\n' "$*"
}

die() {
  printf '[setup-git-server-remote][ERROR] %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  bash scripts/setup-git-server-remote.sh [options]

Options:
  --host <ip_or_dns>      SSH host (default: 185.190.143.17)
  --port <port>           SSH port (default: 22)
  --identity-file <path>  SSH private key file
  --root-user <name>      SSH user for remote execution (default: root)
  --admin-user <name>     Admin user on remote host (default: devops)
  --create-admin          Create admin user if missing
  --pubkey <key>          Public key content to add into /home/git/.ssh/authorized_keys
  --pubkey-file <path>    File with public key content
  -h, --help              Show this help
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --host)
        [[ $# -ge 2 ]] || die "--host requires a value"
        HOST="$2"
        shift 2
        ;;
      --port)
        [[ $# -ge 2 ]] || die "--port requires a value"
        PORT="$2"
        shift 2
        ;;
      --identity-file)
        [[ $# -ge 2 ]] || die "--identity-file requires a value"
        IDENTITY_FILE="$2"
        shift 2
        ;;
      --root-user)
        [[ $# -ge 2 ]] || die "--root-user requires a value"
        ROOT_USER="$2"
        shift 2
        ;;
      --admin-user)
        [[ $# -ge 2 ]] || die "--admin-user requires a value"
        ADMIN_USER="$2"
        shift 2
        ;;
      --create-admin)
        CREATE_ADMIN="true"
        shift
        ;;
      --pubkey)
        [[ $# -ge 2 ]] || die "--pubkey requires a value"
        PUBKEY="$2"
        shift 2
        ;;
      --pubkey-file)
        [[ $# -ge 2 ]] || die "--pubkey-file requires a value"
        PUBKEY_FILE="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "Unknown argument: $1"
        ;;
    esac
  done
}

load_pubkey() {
  if [[ -n "${PUBKEY_FILE}" ]]; then
    [[ -f "${PUBKEY_FILE}" ]] || die "Public key file not found: ${PUBKEY_FILE}"
    PUBKEY="$(<"${PUBKEY_FILE}")"
  fi
}

main() {
  parse_args "$@"
  load_pubkey

  command -v ssh >/dev/null 2>&1 || die "Missing command: ssh"

  local script_path
  script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/setup-git-server.sh"
  [[ -f "${script_path}" ]] || die "Missing local script: ${script_path}"

  local -a remote_args
  remote_args+=(--admin-user "${ADMIN_USER}")
  if [[ "${CREATE_ADMIN}" == "true" ]]; then
    remote_args+=(--create-admin)
  fi
  if [[ -n "${PUBKEY}" ]]; then
    remote_args+=(--pubkey "${PUBKEY}")
  fi

  local -a ssh_args
  ssh_args+=(-p "${PORT}")
  ssh_args+=(-o BatchMode=yes)
  ssh_args+=(-o ConnectTimeout=20)
  if [[ -n "${IDENTITY_FILE}" ]]; then
    ssh_args+=(-i "${IDENTITY_FILE}")
  fi

  local remote_cmd
  remote_cmd="bash -s -- $(printf '%q ' "${remote_args[@]}")"

  log "Running remote setup on ${ROOT_USER}@${HOST}:${PORT}"
  ssh "${ssh_args[@]}" "${ROOT_USER}@${HOST}" "${remote_cmd}" < "${script_path}"
  log "Remote setup finished"
}

main "$@"
