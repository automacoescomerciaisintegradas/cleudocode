#!/bin/bash

# Tenta carregar variáveis do arquivo .env
if [ -f .env ]; then
  # Exporta variáveis ignorando linhas comentadas
  export $(grep -v '^#' .env | xargs)
fi

# Garante que as variáveis essenciais estejam definidas (Fallback)
: "${DEEPSEEK_MODEL:=qwen2.5-coder:7b}"
: "${OLLAMA_HOST:=http://144.91.118.78:11434}"

set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Uso: $0 <numero_de_iteracoes>"
  exit 1
fi

ITERATIONS="$1"

# Garante existência do arquivo de features
if [ ! -f features.json ]; then
  echo "[]" > features.json
fi

for ((i=1; i<=ITERATIONS; i++)); do
  echo ""
  echo "=== Iteração $i / $ITERATIONS [Modelo: $DEEPSEEK_MODEL] ==="
  echo ""

  # Injeta Conteúdo Real dos Arquivos no Prompt (Simulando comportamento de @arquivo)
  PRD_CONTENT="[Arquivo não encontrado]"
  if [ -f "docs/PRD.md" ]; then PRD_CONTENT=$(cat docs/PRD.md); fi
  
  FEATURES_CONTENT=$(cat features.json)

  PROMPT="
Aqui está o contexto atual do projeto:

=== ARQUIVO: docs/PRD.md ===
$PRD_CONTENT

=== ARQUIVO: features.json ===
$FEATURES_CONTENT

=== SUA TAREFA ===
1. Identifique a tarefa aberta de maior prioridade e implemente-a.
2. Antes de **qualquer commit**, execute TODAS as verificações:
   a. TypeScript: npm run typecheck — deve passar sem erros
   b. Lint: npm run lint — zero violações
   c. Testes: npm test — todos passando
   d. Build: npm run build — sem falhas
   e. Checagem visual: npm run dev e confirmar UI funcional ponta a ponta
3. Se QUALQUER etapa falhar:
   - Não faça commit
   - Corrija imediatamente
   - Repita o ciclo até tudo estar limpo
4. Após sucesso:
   - Atualize PRD.md
   - Acrescente progresso ao features.json
   - Gere commit
5. Quando o PRD estiver concluído, retorne **exatamente**
   <promise>COMPLETE</promise>
"

  # Executa o comando via Ollama CLI
  # Nota: Requer 'ollama' instalado no PATH local do cliente
  result=$(ollama run "$DEEPSEEK_MODEL" "$PROMPT" 2>&1 || true)

  echo "$result"

  if [[ "$result" == *"<promise>COMPLETE</promise>"* ]]; then
    echo "🎉 PRD concluído após $i iterações."
    exit 0
  fi
done

echo "⚠️ Número máximo de iterações atingido sem concluir PRD."
exit 1
