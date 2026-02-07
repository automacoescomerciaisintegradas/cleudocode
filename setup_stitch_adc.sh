#!/bin/bash
set -e

echo "🔐 Configurando Google Cloud ADC para Stitch..."

# Passo 1: Autenticar com Google Cloud
echo ""
echo "📝 Passo 1: Autenticação com Google Cloud"
echo "Você será redirecionado para fazer login no navegador..."
gcloud auth application-default login

# Passo 2: Configurar projeto (você precisará fornecer o PROJECT_ID)
echo ""
echo "📝 Passo 2: Configurar Projeto"
read -p "Digite o ID do seu projeto Google Cloud (ou pressione Enter para criar um novo): " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "Criando novo projeto..."
    PROJECT_ID="cleudocode-$(date +%s)"
    gcloud projects create $PROJECT_ID --name="CleudoCode"
    echo "✅ Projeto criado: $PROJECT_ID"
fi

gcloud config set project $PROJECT_ID
echo "✅ Projeto configurado: $PROJECT_ID"

# Passo 3: Habilitar Stitch API
echo ""
echo "📝 Passo 3: Habilitando Stitch API..."
gcloud services enable stitch.googleapis.com --project=$PROJECT_ID
echo "✅ Stitch API habilitada!"

# Passo 4: Criar arquivo de configuração MCP
echo ""
echo "📝 Passo 4: Criando configuração MCP..."

MCP_CONFIG_DIR="/root/.cleudocode"
mkdir -p $MCP_CONFIG_DIR

cat > $MCP_CONFIG_DIR/mcp_stitch_config.json <<EOF
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": [
        "-y",
        "@google-labs/stitch-mcp-server"
      ],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "$PROJECT_ID"
      }
    }
  }
}
EOF

echo "✅ Configuração MCP criada em: $MCP_CONFIG_DIR/mcp_stitch_config.json"

# Passo 5: Verificar credenciais
echo ""
echo "📝 Passo 5: Verificando credenciais..."
gcloud auth application-default print-access-token > /dev/null && echo "✅ Credenciais ADC configuradas corretamente!"

echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "📋 Resumo:"
echo "  - Projeto: $PROJECT_ID"
echo "  - Credenciais ADC: ~/.config/gcloud/application_default_credentials.json"
echo "  - Config MCP: $MCP_CONFIG_DIR/mcp_stitch_config.json"
echo ""
echo "Para usar o Stitch MCP, adicione a configuração ao seu cliente MCP."
