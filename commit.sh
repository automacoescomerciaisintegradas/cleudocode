#!/bin/bash

# Script de Commit Automatizado do Cleudocode
# Autor: Automações Comerciais Integradas
# Versão: 1.0

echo "==========================================="
echo "  CLEUDOCODE - Script de Commit Automatizado"
echo "==========================================="

# Verifica se estamos em um repositório git
if [ ! -d ".git" ]; then
    echo "❌ Erro: Não estamos em um repositório git"
    exit 1
fi

# Mostra o status atual
echo "📁 Status atual do repositório:"
git status --short

# Pergunta pelo tipo de commit
echo ""
echo "📝 Tipo de commit:"
echo "1) feat - Nova funcionalidade"
echo "2) fix - Correção de bug"
echo "3) docs - Documentação"
echo "4) style - Estilo/formato"
echo "5) refactor - Refatoração"
echo "6) perf - Performance"
echo "7) test - Testes"
echo "8) chore - Tarefas auxiliares"
echo "9) revert - Reverter alterações"
echo ""

read -p "Escolha (1-9): " type_choice

case $type_choice in
    1) TYPE="feat";;
    2) TYPE="fix";;
    3) TYPE="docs";;
    4) TYPE="style";;
    5) TYPE="refactor";;
    6) TYPE="perf";;
    7) TYPE="test";;
    8) TYPE="chore";;
    9) TYPE="revert";;
    *) echo "❌ Opção inválida"; exit 1;;
esac

# Pergunta pelo escopo (opcional)
read -p "📦 Escopo (opcional, ex: cli, web, api, readme): " SCOPE

# Pergunta pela mensagem
read -p "💬 Mensagem curta e descritiva: " SUBJECT

# Monta o commit
if [ -z "$SCOPE" ]; then
    COMMIT_MSG="$TYPE: $SUBJECT"
else
    COMMIT_MSG="$TYPE($SCOPE): $SUBJECT"
fi

echo ""
echo "🔄 Adicionando arquivos modificados..."

# Pergunta se quer adicionar todos os arquivos ou selecionar manualmente
echo "Deseja adicionar todos os arquivos modificados?"
read -p "(s para sim, n para selecionar manualmente): " add_choice

if [[ $add_choice =~ ^[Ss]$ ]]; then
    # Adiciona todos os arquivos modificados
    git add .
    echo "✅ Todos os arquivos modificados foram adicionados"
else
    # Mostra arquivos modificados e permite seleção
    echo "Arquivos modificados encontrados:"
    git status --porcelain | grep -E '^.[AMDRCU?!]' | nl
    
    echo "Digite os números dos arquivos que deseja adicionar (separados por espaço), ou 'all' para todos:"
    read -r file_choice
    
    if [ "$file_choice" = "all" ]; then
        git add .
    else
        # Processa a seleção de arquivos
        git status --porcelain | grep -E '^.[AMDRCU?!]' | sed -n "$file_choice"p | while read -r line; do
            file=$(echo "$line" | cut -c4-)
            git add "$file"
            echo "✅ Arquivo adicionado: $file"
        done
    fi
fi

echo ""
echo "📋 Mensagem do commit será: $COMMIT_MSG"
echo ""
read -p "Confirmar commit? (s/n): " confirm

if [[ $confirm =~ ^[Ss]$ ]]; then
    # Faz o commit
    git commit -m "$COMMIT_MSG"
    
    echo ""
    echo "🎉 Commit realizado com sucesso!"
    echo "📝 Mensagem: $COMMIT_MSG"
    
    # Pergunta se deseja fazer push
    read -p "Deseja fazer push para o repositório remoto? (s/n): " push_choice
    if [[ $push_choice =~ ^[Ss]$ ]]; then
        echo "📤 Realizando push..."
        git push origin "$(git branch --show-current)"
        echo "✅ Push concluído!"
    else
        echo "ℹ️  Lembre-se de fazer 'git push' para enviar as alterações"
    fi
else
    echo "❌ Commit cancelado"
fi

echo ""
echo "✨ Operação concluída!"