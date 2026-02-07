#!/bin/bash
set -e

echo "🔧 Instalando Google Cloud SDK..."

# Adicionar repositório do Google Cloud SDK
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Importar chave GPG
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

# Atualizar e instalar
sudo apt-get update
sudo apt-get install -y google-cloud-cli

# Verificar instalação
gcloud --version

echo "✅ Google Cloud SDK instalado com sucesso!"
