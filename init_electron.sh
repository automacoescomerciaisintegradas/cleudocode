#!/bin/bash
cd /root/cleudocode
npx -y create-vite@latest cleudocode-desktop --template react
cd cleudocode-desktop
npm install
npm install -D electron concurrently cross-env wait-on
