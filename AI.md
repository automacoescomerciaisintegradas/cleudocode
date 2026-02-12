# AI Project Context - Cleudocode & Antigravity Workflows

## 🎯 Project Context
This project, **Cleudocode**, is a specialized AI development environment and automation platform. It integrates with the **Antigravity** system (by Automações Comerciais Integradas) to provide automated workflows, monitoring, and deployment capabilities via the **Lobster Engine**.

## 🏗️ Architecture
- **Core**: Python-based CLI and gateway.
- **Workflow Engine**: **Lobster Engine** - a YAML/Lobster-based automation system.
- **Integration**: Connects to Telegram, WhatsApp (Evolution API), and local system services.
- **Port**: Typically runs on port `18900`.

## 📜 Conventions
- **Workflows**: Located in `skills/workflows/` with `.lobster` extension.
- **Scripts**: Main entry point for workflows is `workflow_manager.py`.
- **Reports**: Generated in the `reports/` directory.
- **Naming**: Use snake_case for scripts and descriptive names for workflows.

## 📖 Glossary
- **Lobster**: The internal engine for executing sequential automation steps.
- **Skill**: A modular capability (e.g., `shell`, `filesystem`, `telegram`) usable within workflows.
- **Gateway**: The interface for external communication (WhatsApp/Telegram).

## 🔌 Integrations
- **Evolution API**: For WhatsApp messaging.
- **Telegram Bot API**: For notifications and control.
- **Antigravity Gateway**: Local system service being monitored and managed.

## 🚫 Forbidden Patterns
- **Direct Shell Execution**: Avoid raw shell calls when a specific `skill` (like `filesystem`) exists.
- **Hardcoded Credentials**: Always use `.env` or the gateway token system.
- **Incompatible Commands**: Since the host is Windows (NT), ensure shell commands are compatible or use WSL wrappers if necessary.

## 🛠️ Infrastructure
- **Operating System**: Windows (Workspaces stored in WSL Ubuntu path).
- **Python**: Primary runtime for the orchestrator and workflow manager.
