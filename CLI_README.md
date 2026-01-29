# Cleudocode CLI

The Cleudocode CLI provides command-line access to various Cleudocodebot functionalities.

## Installation

To install the CLI globally, run:

```bash
pip install -e .
```

This will make the `cleudocode` command available system-wide.

## Commands

### Onboard

Run the onboarding wizard to configure Cleudocodebot:

```bash
cleudocode onboard
```

Options:
- `--force, -f`: Force reconfiguration even if already configured
- `--verbose, -v`: Show verbose output

### Status

Check the status of Cleudocodebot services:

```bash
cleudocode status
```

### Start

Start the Cleudocodebot daemon:

```bash
cleudocode start
```

### Stop

Stop the Cleudocodebot daemon:

```bash
cleudocode stop
```

### Config

Show current configuration:

```bash
cleudocode config
```

## Onboarding Process

The `cleudocode onboard` command will guide you through the following steps:

1. Create a `.env` configuration file with default values
2. Install project dependencies
3. Check Ollama configuration
4. Configure API keys and other settings
5. Display next steps

After running the onboarding process, you'll have a fully configured Cleudocodebot installation ready to use.