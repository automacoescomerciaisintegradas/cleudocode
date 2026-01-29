# run_iterations.ps1
# Executa iterações com Ollama via API HTTP (Windows-friendly)
# Usa .env para configuração (OLLAMA_HOST, DEEPSEEK_MODEL)

param(
    [Parameter(Mandatory = $true)]
    [int]$Iterations
)

# --- Carregar .env ---
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line -split "=", 2
            $key = $parts[0].Trim()
            $value = $parts[1].Trim().Trim('"').Trim("'")
            Set-Item "env:$key" $value -Force
        }
    }
}

# --- Fallbacks ---
$DEEPSEEK_MODEL = if ($env:DEEPSEEK_MODEL) { $env:DEEPSEEK_MODEL } else { "qwen2.5-coder:7b" }
$OLLAMA_HOST = if ($env:OLLAMA_HOST) { $env:OLLAMA_HOST } else { "http://localhost:11434" }

Write-Host "Using:" -ForegroundColor Cyan
Write-Host "  OLLAMA_HOST = $OLLAMA_HOST"
Write-Host "  DEEPSEEK_MODEL = $DEEPSEEK_MODEL"
Write-Host ""

# --- Verificar existência de features.json ---
$featuresPath = Join-Path $PSScriptRoot "features.json"
if (-not (Test-Path $featuresPath)) {
    Write-Host "Creating features.json..."
    '[]' | Out-File -FilePath $featuresPath -Encoding UTF8
}

# --- Loop de iterações ---
for ($i = 1; $i -le $Iterations; $i++) {
    Write-Host "=== Iteração $i / $Iterations [Modelo: $DEEPSEEK_MODEL] ===" -ForegroundColor Green
    Write-Host ""

    # Ler PRD.md (se existir)
    $prdPath = Join-Path $PSScriptRoot "docs\PRD.md"
    $prdContent = if (Test-Path $prdPath) { Get-Content $prdPath -Raw } else { "[Arquivo docs/PRD.md não encontrado]" }

    # Ler features.json
    $featuresContent = Get-Content $featuresPath -Raw

    # Montar prompt
    $prompt = @"
Aqui está o contexto atual do projeto:

=== ARQUIVO: docs/PRD.md ===
$prdContent

=== ARQUIVO: features.json ===
$featuresContent

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
"@

    # Enviar para Ollama via API
    $body = @{
        model     = $DEEPSEEK_MODEL
        prompt    = $prompt
        stream    = $false
        options   = @{ temperature = 0.1 }
    } | ConvertTo-Json

    try {
        Write-Host "Enviando requisição para $OLLAMA_HOST/api/generate..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "$OLLAMA_HOST/api/generate" -Method Post -Body $body -ContentType "application/json"
        $result = $response.response
    } catch {
        Write-Error "Falha na chamada para Ollama: $($_.Exception.Message)"
        $result = "ERROR: $($_.Exception.Message)"
    }

    Write-Host $result -ForegroundColor White

    if ($result -match '<promise>COMPLETE</promise>') {
        Write-Host "🎉 PRD concluído após $i iterações." -ForegroundColor Magenta
        exit 0
    }

    Start-Sleep -Seconds 1
}

Write-Host "⚠️ Número máximo de iterações atingido sem concluir PRD." -ForegroundColor Red
exit 1