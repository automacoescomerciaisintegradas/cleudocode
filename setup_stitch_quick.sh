#!/bin/bash
set -e

echo "🔧 Configuração Rápida do Stitch MCP"
echo ""

# Criar projeto automaticamente
PROJECT_ID="cleudocode-stitch-$(date +%s)"

echo "📝 Criando projeto: $PROJECT_ID"
gcloud projects create $PROJECT_ID --name="CleudoCode Stitch" || {
    echo "⚠️ Erro ao criar projeto. Usando projeto padrão..."
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
    
    if [ -z "$PROJECT_ID" ]; then
        echo "❌ Nenhum projeto configurado. Configure manualmente:"
        echo "   gcloud config set project SEU_PROJECT_ID"
        exit 1
    fi
}

echo "✅ Projeto: $PROJECT_ID"

# Configurar como padrão
echo "📝 Configurando projeto padrão..."
gcloud config set project $PROJECT_ID

# Configurar quota project
echo "📝 Configurando quota project..."
gcloud auth application-default set-quota-project $PROJECT_ID

# Habilitar API
echo "📝 Habilitando Stitch API..."
gcloud services enable stitch.googleapis.com --project=$PROJECT_ID

echo ""
echo "✅ Configuração concluída!"
echo "   Projeto: $PROJECT_ID"
echo ""
echo "Teste com: python3 test_stitch_oauth.py"
