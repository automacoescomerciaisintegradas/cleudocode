# AGENTS.md - Cleudocode

Minimal operating guide for AI coding agents in the Cleudocode repository.

## Codex Adapter Scope
- This file is the Codex-facing adapter for this repository.
- Shared project knowledge must stay in shared folders such as:
  - `docs/`
  - `references/`
  - `templates/`
  - `scripts/`
- Claude-specific adapter files live under `.claude/`.
- Codex-specific adapter files live under `.codex/` and `.codex/agents/`.

## Before Implementing
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.

## Code Changes
- Minimum code that solves the problem. No speculative features.
- No abstractions for single-use code.
- Surgical edits: touch only what the task requires.
- Match existing style (Python/Rich for CLI, Flask/Streamlit for Web).
- Remove imports/variables YOUR changes made unused; don't touch pre-existing dead code.

## Verification
- Transform tasks into verifiable goals with clear success criteria.
- For multi-step tasks, state a brief plan with verification checkpoints.

## Scope
- Solve issues with the smallest context read.
- Keep changes scoped to one command family or module group.
- Read at most 3 files first:
  - the owning handler/module (e.g., `cli/main.py`, `web_server.py`)
  - one shared helper used by that handler (e.g., `core/config_manager.py`)
  - one downstream integration file if needed
- Expand only when contracts cross module boundaries.

## Architecture

- **CLI (`cli/main.py`)**: Entry point for command-line operations.
  - Subcommands: `init`, `onboard`, `plugins`, `models`, `start`.
  - Plugins logic: Managed via `.env` (`ENABLED_PLUGINS`).
- **Core (`core/`)**: Business logic and shared components.
  - `auth_middleware.py`: Authentication logic.
  - `config_manager.py`: Configuration handling.
  - `llm_providers.py`: LLM integration.
- **Web Server (`web_server.py`)**: Flask backend API.
- **Frontend (`web_app.py`, `streamlit_app.py`)**: Streamlit dashboard.
- **OAuth (`oauth_listener.py`)**: Helper for authentication flows.

## Routing
- Keep `cli/main.py` as a router for CLI commands.
- Put command logic in handler modules inside `cli/` or `core/`:
  - `cli/gateway_command.py`: Managed via `cli/gateway_command.py`.
  - `cli/init_command.py`: Managed via `cli/init_command.py`.

## Hard Rules

- **Use `core/config_manager.py`** to handle `.env` reads/writes. Do not parse `.env` manually unless bootstrapping.
- **Use `check=True`** with `subprocess.run` unless failure is expected.
- **Do not hardcode** API keys or tokens; use `.env`.
- **Verify platform** specific paths (Windows vs Linux) where applicable (`os.name == 'nt'`).

## Key Files
- CLI: `cli/main.py`
- Configuration: `.env`, `core/config_manager.py`
- Auth: `oauth_listener.py`, `core/auth_middleware.py`
- Plugins: `plugins/` (if extended), `cli/main.py` (enable logic)
- Dashboard: `web_server.py`, `web_app.py`

## Capability Source Of Truth

- Supported LLM providers specific logic resides in `core/llm_providers.py`.
- Plugin enablement is tracked in `.env` variable `ENABLED_PLUGINS`.

## Testing
- Unit tests under `tests/` or colocated if preferred.
- Run generic tests: `python run_all_tests.py`.
- Run specific module tests: `python -m unittest tests/test_module.py`.

## Local Commands

- Run CLI: `python cli/main.py <command>` OR `cleudocode <command>` (if installed)
- Start Dashboard: `cleudocode dashboard`
- Enable Plugin: `cleudocode plugins enable <name>`
- Verify Health: `cleudocode doctor`


