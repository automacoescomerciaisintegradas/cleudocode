#!/bin/bash
set -e

echo "🔧 Configurando Quota Project para Stitch..."

# Passo 1: Login no gcloud (se necessário)
echo ""
echo "📝 Verificando autenticação..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "Fazendo login no gcloud..."
    gcloud auth login
fi

# Passo 2: Listar projetos disponíveis
echo ""
echo "📋 Projetos disponíveis:"
gcloud projects list

# Passo 3: Configurar quota project
echo ""
read -p "Digite o PROJECT_ID para usar como quota project (ou pressione Enter para criar novo): " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    # Criar novo projeto
    PROJECT_ID="cleudocode-stitch-$(date +%s)"
    echo "Criando projeto: $PROJECT_ID"
    gcloud projects create $PROJECT_ID --name="CleudoCode Stitch"
    echo "✅ Projeto criado!"
    
    # Aguardar propagação
    echo "Aguardando propagação do projeto..."
    sleep 5
fi

# Configurar como projeto padrão
echo ""
echo "Configurando projeto padrão..."
gcloud config set project $PROJECT_ID

# Configurar quota project para ADC
echo ""
echo "Configurando quota project para ADC..."
gcloud auth application-default set-quota-project $PROJECT_ID

# Habilitar Stitch API
echo ""
echo "Habilitando Stitch API..."
gcloud services enable stitch.googleapis.com --project=$PROJECT_ID

echo ""
echo "✅ Configuração concluída!"
echo ""
echo "📋 Resumo:"
echo "  - Projeto: $PROJECT_ID"
echo "  - Quota Project configurado: ✅"
echo "  - Stitch API habilitada: ✅"
echo ""
echo "Agora você pode usar: python3 test_stitch_oauth.py"
