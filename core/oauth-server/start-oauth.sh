#!/bin/bash
# Script de Instalação e Execução do OAuth Server

cd core/oauth-server

echo "📦 Instalando dependências do OAuth Server..."
npm install

echo "🚀 Iniciando Servidor de OAuth..."
npm start
