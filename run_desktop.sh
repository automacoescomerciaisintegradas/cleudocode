#!/bin/bash
# AIDEV-NOTE: Helper script to launch the Cleudocode Desktop Client (Electron) from the workspace root

echo "=========================================="
echo "🖥️ Starting Cleudocode Desktop Client..."
echo "=========================================="

APP_DIR="/root/cleudocode/cleudocode-desktop"

if [ ! -d "$APP_DIR" ]; then
    echo "❌ Error: Desktop App directory ($APP_DIR) not found."
    echo "Please ensure the client module is generated properly."
    exit 1
fi

cd "$APP_DIR" || exit 1

# Check if node_modules exists, if not, try installing
if [ ! -d "node_modules" ]; then
    echo "📦 node_modules not found. Running npm install..."
    npm install
fi

echo "🚀 Launching Vite + Electron environment..."
# Running in the background to avoid blocking the shell if invoked from other scripts
# But if you run this manually in terminal, you probably want to see the logs.
npm run start
