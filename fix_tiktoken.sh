#!/bin/bash

# Script para corrigir o erro "Missing tiktoken_bg.wasm" no bundle do qwen-code
# Autor: Engenheiro de Prompt Sênior (Antigravity)

echo "🔍 Iniciando correção do tiktoken_bg.wasm..."

# Definição de caminhos
GLOBAL_NODE_MODULES="/root/.nvm/versions/node/v22.22.0/lib/node_modules"
QWEN_BUNDLE_PATH="$GLOBAL_NODE_MODULES/qwen-code/bundle"

# 1. Tentar localizar o arquivo tiktoken_bg.wasm em qualquer lugar nos módulos globais
echo "🎯 Procurando tiktoken_bg.wasm nos módulos globais..."
TIKTOKEN_WASM=$(find "$GLOBAL_NODE_MODULES" -name "tiktoken_bg.wasm" | head -n 1)

if [ -z "$TIKTOKEN_WASM" ]; then
    echo "❌ Arquivo não encontrado globalmente. Instalando tiktoken localmente para obter o binário..."
    npm install tiktoken --no-save
    TIKTOKEN_WASM="./node_modules/tiktoken/tiktoken_bg.wasm"
fi

if [ -f "$TIKTOKEN_WASM" ]; then
    echo "✅ Arquivo encontrado em: $TIKTOKEN_WASM"
    echo "🚀 Copiando para o diretório do bundle: $QWEN_BUNDLE_PATH"
    
    # Garantir que o diretório de destino existe
    mkdir -p "$QWEN_BUNDLE_PATH"
    
    # Copiar o arquivo
    cp "$TIKTOKEN_WASM" "$QWEN_BUNDLE_PATH/"
    
    if [ -f "$QWEN_BUNDLE_PATH/tiktoken_bg.wasm" ]; then
        echo "🎉 Sucesso! O arquivo foi copiado."
        echo "Tente rodar o comando novamente."
    else
        echo "❌ Erro ao copiar o arquivo. Verifique se você tem permissões de root."
    fi
else
    echo "❌ Falha crítica: Não foi possível obter o tiktoken_bg.wasm."
    echo "Sugestão: Execute 'npm install -g tiktoken' e tente este script novamente."
fi
