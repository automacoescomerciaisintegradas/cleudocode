# Design: Cleudocode CLI Reorg (Groups + Renames)

**Date:** 2026-04-13
**Author:** Codex
**Status:** Approved

## Purpose
Reorganize and rename Cleudocode CLI commands for consistency and clarity, using grouped subcommands and English naming, with intentional breaking changes (no aliases).

## Goals
- Group commands by domain using Click subcommand groups.
- Rename commands and flags to English, consistent style.
- Preserve behavior; change only CLI routing, help text, and UX.
- Update CLI documentation with a clear migration table (old -> new).

## Scope
### In Scope
- Reorganize commands into groups/subcommands.
- Rename commands/options and adjust help text.
- Update `README_CLI.md` and `CLI_README.md` for the new structure.

### Out of Scope
- Backend/gateway behavior changes.
- New features beyond CLI UX.
- Backward-compatible aliases.

## Design
### Architecture
- Keep `cli/main.py` as the router.
- Introduce top-level groups and map existing commands into group subcommands.
- Keep command implementations intact; only entrypoints change.

Proposed command tree:

```
cleudocode
  system   start|stop|status|health|doctor|update|reset|uninstall|logs|completion
  config   show|get|set|unset|init|onboard|configure|setup
  agent    run|chat|message|sessions|memory
  agents   <existing subcommands>
  gateway  <existing subcommands>
  security approvals|sandbox|acp|status
  channels telegram|whatsapp|shopee|webhooks|devices|pairing
  ops      cron|hooks|dns|directory|node|nodes
  ui       dashboard|tui|browser
  ext      plugins|skills|models|docs
```

### Data Flow
1) User calls `cleudocode <group> <subcommand>`.
2) Click router dispatches to the mapped handler.
3) Handler calls existing logic (core/orchestrator/subprocess).
4) Output is printed to terminal (Rich/print).

### Interfaces (Old -> New)
System:
- `start` -> `system start`
- `stop` -> `system stop`
- `status` -> `system status`
- `health` -> `system health`
- `doctor` -> `system doctor`
- `update` -> `system update`
- `reset` -> `system reset`
- `uninstall` -> `system uninstall`
- `logs` -> `system logs`
- `completion` -> `system completion`
- `system` -> `system events`

Config:
- `config` -> `config show`
- `config get` -> `config get`
- `config set` -> `config set`
- `config unset` -> `config unset`
- `init` -> `config init`
- `onboard` -> `config onboard`
- `configure` -> `config configure`
- `setup` -> `config setup`

Agent:
- `agent` -> `agent run`
- `chat` -> `agent chat`
- `message` -> `agent message`
- `sessions` -> `agent sessions`
- `memory` -> `agent memory`

Security:
- `approvals` -> `security approvals`
- `sandbox` -> `security sandbox`
- `acp` -> `security acp`

Channels:
- `telegram` -> `channels telegram`
- `whatsapp` -> `channels whatsapp`
- `shopee` -> `channels shopee`
- `webhooks` -> `channels webhooks`
- `devices` -> `channels devices`
- `pairing` -> `channels pairing`

Ops:
- `cron` -> `ops cron`
- `hooks` -> `ops hooks`
- `dns` -> `ops dns`
- `directory` -> `ops directory`
- `node` -> `ops node`
- `nodes` -> `ops nodes`

UI:
- `dashboard` -> `ui dashboard`
- `tui` -> `ui tui`
- `browser` -> `ui browser`

Extensions:
- `plugins` -> `ext plugins`
- `skills` -> `ext skills`
- `models` -> `ext models`
- `docs` -> `ext docs`

Gateway/Agents:
- `gateway` -> `gateway <existing>`
- `daemon` -> `gateway daemon`
- `agents` -> `agents <existing>`

## Alternatives Considered
1. Registry-based command auto-generation: more robust but higher complexity now.
2. CLI v2 entrypoint: more flexibility but costly and duplicative.

## Testing Strategy
- `cleudocode --help` shows the new groups.
- `cleudocode <group> --help` lists expected subcommands.
- Smoke test critical commands: `system start/stop/status`, `config show`, `agent run/chat`.
- Run `python run_all_tests.py` only if already part of the project’s normal workflow.

## Risks
- Breaking scripts due to renames (mitigate with migration table in docs).
- Hidden commands in code not covered by the mapping (mitigate by scanning `cli/`).

## Open Questions
- Confirm all command definitions across `cli/` for full coverage during implementation.
