# 🧪 Guia de Testes - Cleudocodebot

## 📋 Visão Geral

Este diretório contém scripts de teste para validar as principais funcionalidades do Cleudocodebot:

- **🔒 Sandbox Security** - Validação do sistema de segurança
- **Cleudocode Lobster Workflow** - Teste do motor de workflows
- **🎙️ Voice Integration** - Validação de TTS/STT

---

## 🚀 Execução Rápida

### Executar TODOS os testes

```bash
python run_all_tests.py
```

### Executar testes individuais

```bash
# Testar Sandbox
python test_sandbox_quick.py

# Testar Lobster Workflow
python test_lobster_quick.py

# Testar Voice Integration
python test_whisper_quick.py
```

---

## 📦 Pré-requisitos

### Dependências Python

```bash
pip install rich
```

### Para testes de Voice

```bash
pip install openai-whisper TTS pydub
```

### FFmpeg (para Voice)

**Windows:**
```powershell
choco install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

---

## 🔒 Teste de Sandbox (`test_sandbox_quick.py`)

### O que é testado

1. ✅ Comando permitido (echo)
2. ❌ Comando bloqueado (rm -rf)
3. ❌ Caracteres perigosos (&&, ||, ;)
4. ✅ Escrita de arquivo
5. ✅ Leitura de arquivo
6. ❌ Path traversal (../)
7. ✅ Listar diretório
8. ⏱️ Timeout de comando
9. ❌ Arquivo muito grande
10. ✅ Sobrescrever arquivo

### Execução

```bash
python test_sandbox_quick.py
```

### Resultado esperado

```
🔒 TESTE DO SISTEMA DE SANDBOX

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                              Resultados dos Testes                              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ✅ Comando Permitido      │ PASSOU │ echo executado com sucesso                │
│ ✅ Comando Bloqueado      │ PASSOU │ rm bloqueado corretamente                 │
│ ✅ Caracteres Perigosos   │ PASSOU │ Caractere && bloqueado                    │
│ ✅ Escrita de Arquivo     │ PASSOU │ Arquivo criado: sandbox/test.txt          │
│ ✅ Leitura de Arquivo     │ PASSOU │ 42 caracteres lidos                       │
│ ✅ Path Traversal         │ PASSOU │ Acesso fora do sandbox bloqueado          │
│ ✅ Listar Diretório       │ PASSOU │ 3 itens encontrados                       │
│ ✅ Timeout                │ PASSOU │ Comando bloqueado ou timeout funcionou    │
│ ✅ Arquivo Grande         │ PASSOU │ Arquivo grande bloqueado                  │
│ ✅ Sobrescrever           │ PASSOU │ Arquivo sobrescrito corretamente          │
└───────────────────────────┴────────┴───────────────────────────────────────────┘

🎉 TODOS OS TESTES PASSARAM!
```

---

## Cleudocode Teste de Lobster Workflow (`test_lobster_quick.py`)

### O que é testado

1. ✅ Criação de workflow YAML
2. ✅ Carregamento de workflows
3. ✅ Interpolação de variáveis (Jinja2)
4. ✅ Execução de steps sequenciais
5. ✅ Geração de arquivos
6. ✅ Integração com skills

### Execução

```bash
python test_lobster_quick.py
```

### Resultado esperado

```
Cleudocode TESTE DO LOBSTER WORKFLOW ENGINE

Workflows Disponíveis:
  • Teste Rápido (v1.0) - 4 steps

Executando Workflow 'Teste Rápido'...

📊 RESULTADOS DA EXECUÇÃO

✅ Workflow executado com sucesso!

Workflow: Teste Rápido
Steps executados: 4/4

Detalhes dos Steps:

✅ Step 1: Criar diretório de teste
   Arquivo: test_lobster_output/

✅ Step 2: Escrever arquivo de teste
   Arquivo: test_lobster_output/test_20260127_190000.txt

✅ Step 3: Listar arquivos criados
   Output: test_20260127_190000.txt

✅ Step 4: Ler arquivo criado
   Content: 123 caracteres

🎉 TESTE CONCLUÍDO COM SUCESSO!
```

---

## 🎙️ Teste de Voice Integration (`test_whisper_quick.py`)

### O que é testado

1. ✅ Importação do Whisper STT
2. ✅ Carregamento do modelo Whisper
3. ✅ Importação do Coqui TTS
4. ✅ Carregamento do modelo TTS
5. ✅ Síntese de áudio
6. ✅ Voice Skill completa

### Execução

```bash
python test_whisper_quick.py
```

### Resultado esperado

```
🎙️ TESTE DE INTEGRAÇÃO DE VOZ

🎤 TESTE DO WHISPER (SPEECH-TO-TEXT)

Importando Whisper...
✅ Whisper importado com sucesso

Carregando modelo Whisper...
✅ Modelo Whisper carregado!

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                  Whisper STT                                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Modelo: base                                                                    │
│ Device: cpu                                                                     │
│ Status: Pronto para transcrição                                                │
└─────────────────────────────────────────────────────────────────────────────────┘

🔊 TESTE DO COQUI TTS (TEXT-TO-SPEECH)

Carregando modelo TTS...
✅ Modelo TTS carregado!

Testando síntese de voz...
✅ Áudio gerado com sucesso!

Arquivo: test_output.wav
Texto: Olá! Este é um teste de síntese de voz usando Coqui TTS.
Duração estimada: 3.5s

🔊 Reproduza o áudio: test_output.wav

📊 RESUMO DOS TESTES

✅ Whisper STT
✅ Coqui TTS
✅ Voice Skill

🎉 TODOS OS TESTES PASSARAM!
```

---

## 🎯 Script Mestre (`run_all_tests.py`)

Executa todos os testes em sequência e gera relatório consolidado.

### Execução

```bash
python run_all_tests.py
```

### Resultado esperado

```
🧪 CLEUDOCODEBOT - BATERIA COMPLETA DE TESTES

Este script executa todos os testes de validação:

1. 🔒 Sandbox Security
2. Cleudocode Lobster Workflow Engine
3. 🎙️ Voice Integration (Whisper + Coqui TTS)

▶️ Executando: 🔒 Sandbox Security
...
✅ 🔒 Sandbox Security concluído com sucesso

▶️ Executando: Cleudocode Lobster Workflow
...
✅ Cleudocode Lobster Workflow concluído com sucesso

▶️ Executando: 🎙️ Voice Integration
...
✅ 🎙️ Voice Integration concluído com sucesso

📊 RESUMO GERAL DOS TESTES

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                   Resultados                                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 🔒 Sandbox Security     │ ✅ PASSOU │ Sucesso                                   │
│ Cleudocode Lobster Workflow     │ ✅ PASSOU │ Sucesso                                   │
│ 🎙️ Voice Integration    │ ✅ PASSOU │ Sucesso                                   │
└─────────────────────────┴───────────┴───────────────────────────────────────────┘

🎉 TODOS OS TESTES PASSARAM!

✅ Total: 3
✅ Aprovados: 3
❌ Falhas: 0

O sistema está pronto para uso!
```

---

## 🐛 Troubleshooting

### Erro: "Module 'rich' not found"

```bash
pip install rich
```

### Erro: "Module 'whisper' not found"

```bash
pip install openai-whisper
```

### Erro: "Module 'TTS' not found"

```bash
pip install TTS
```

### Erro: "FFmpeg not found"

Instale FFmpeg no sistema (ver seção de pré-requisitos).

### Erro: "CUDA not available"

Os testes usam CPU por padrão. Se quiser usar GPU:

```python
# Editar test_whisper_quick.py
whisper = WhisperSTT(model_size="base", device="cuda")
tts = CoquiTTS(model_name="tts_models/pt/cv/vits", gpu=True)
```

---

## 📊 Interpretando Resultados

### ✅ Teste Passou

O componente está funcionando corretamente e pronto para uso.

### ❌ Teste Falhou

Verifique:
1. Dependências instaladas
2. Arquivos de código criados
3. Permissões de diretório
4. Logs de erro detalhados

### ⚠️ Aviso

Funcionalidade parcial ou configuração não ideal, mas não crítico.

---

## 📞 Suporte

Para problemas com os testes:

1. Verifique os logs detalhados de cada teste
2. Confirme que todas as dependências estão instaladas
3. Revise os arquivos de implementação
4. Consulte a documentação completa

---

**Última atualização**: 2026-01-27  
**Versão**: 1.0.0
