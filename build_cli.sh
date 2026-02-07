#!/bin/bash
cd /root/cleudocode
if ! command -v npm &> /dev/null; then
    echo "npm could not be found. Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi
npm install
npm run build
echo "CLI Build Complete. Run with: node dist/cli/index.js"
