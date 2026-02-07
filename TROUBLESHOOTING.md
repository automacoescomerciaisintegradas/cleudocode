# 🔧 Solução de Problemas - Cleudocode

## Problema: Servidor Web Não Abriu

### Causa Identificada
O **Streamlit não estava instalado** no ambiente Python.

### Solução

#### Opção 1: Instalar Streamlit (Recomendado)

```bash
# Instalar Streamlit e dependências
pip install streamlit

# Aguardar instalação completar (pode demorar alguns minutos)
# Depois executar:
python cli/main.py dashboard
```

#### Opção 2: Usar ambiente virtual do projeto

Se o projeto já tem um ambiente virtual configurado:

```bash
# Ativar ambiente virtual
cd /root/cleudocode
source venv/bin/activate  # Linux
# ou
.\venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar dashboard
python cli/main.py dashboard
```

#### Opção 3: Executar Streamlit diretamente

```bash
# Navegar para o diretório
cd /root/cleudocode

# Executar Streamlit manualmente
streamlit run web_app.py --server.port 8501

# Abrir navegador em:
# http://localhost:8501
```

---

## Outros Problemas Comuns

### 1. Erro de Encoding (Windows)

**Sintoma**: `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solução**: Já corrigido no código. Se ainda ocorrer:

```bash
# Definir encoding UTF-8 antes de executar
set PYTHONIOENCODING=utf-8
python cli/main.py dashboard
```

### 2. Porta 8501 já em uso

**Sintoma**: `Address already in use`

**Solução**:

```bash
# Opção 1: Usar porta diferente
python cli/main.py dashboard --port 8502

# Opção 2: Matar processo na porta 8501
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux:
lsof -ti:8501 | xargs kill -9
```

### 3. Token não encontrado

**Sintoma**: Página de login aparece mas token não funciona

**Solução**:

```bash
# Verificar se token existe
cat ~/.cleudocode/.gateway_token  # Linux
type %USERPROFILE%\.cleudocode\.gateway_token  # Windows

# Se não existir, será criado automaticamente no próximo uso:
python cli/main.py dashboard
```

### 4. Ollama não conecta

**Sintoma**: `Falha ao conectar no Ollama`

**Solução**:

```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se não estiver, iniciar:
ollama serve

# Verificar modelo instalado
ollama list

# Instalar modelo se necessário
ollama pull qwen2.5-coder:7b
```

### 5. Módulos Python não encontrados

**Sintoma**: `ModuleNotFoundError: No module named 'X'`

**Solução**:

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Dependências específicas para OpenClaw-like:
pip install pyyaml streamlit rich click
```

---

## Checklist de Diagnóstico

Execute estes comandos para diagnosticar problemas:

```bash
# 1. Verificar Python
python --version
# Deve ser 3.10+

# 2. Verificar Streamlit
python -m streamlit --version
# Se der erro, instalar: pip install streamlit

# 3. Verificar estrutura
ls ~/.cleudocode/
# Deve mostrar: config.yaml, .gateway_token, workspace/, etc.

# 4. Verificar token
cat ~/.cleudocode/.gateway_token
# Deve mostrar um UUID

# 5. Verificar porta
netstat -ano | findstr :8501  # Windows
lsof -i:8501  # Linux
# Se vazio, porta está livre

# 6. Verificar Ollama
curl http://localhost:11434/api/tags
# Deve retornar JSON com modelos
```

---

## Logs de Debug

### Ver logs do Streamlit

```bash
# Logs ficam em:
~/.streamlit/logs/

# Ver último log:
tail -f ~/.streamlit/logs/streamlit.log
```

### Ver logs do Cleudocode

```bash
# Logs ficam em:
~/.cleudocode/logs/

# Listar logs:
ls -la ~/.cleudocode/logs/
```

---

## Instalação Limpa (Reset Completo)

Se nada funcionar, faça uma instalação limpa:

```bash
# 1. Remover configuração antiga
rm -rf ~/.cleudocode/

# 2. Reinstalar dependências
pip uninstall streamlit -y
pip install streamlit

# 3. Executar onboarding novamente
cd /root/cleudocode
python cli/main.py onboard

# 4. Iniciar dashboard
python cli/main.py dashboard
```

---

## Suporte

Se o problema persistir:

1. **Verificar logs** em `~/.cleudocode/logs/`
2. **Abrir issue** no GitHub: https://github.com/cleudocode/cleudocode/issues
3. **Contato direto**: WhatsApp +55 88 92156-7214

---

## Status Atual da Instalação

**Problema**: Streamlit está sendo instalado mas a instalação está demorando.

**Próximos passos**:
1. Aguardar instalação do Streamlit completar
2. Executar `python cli/main.py dashboard`
3. Acessar `http://localhost:8501?token=SEU_TOKEN`

**Token atual**: `63e8f07d-15e0-4695-a38c-0905d88cecf8`

**URL completa**: `http://localhost:8501?token=63e8f07d-15e0-4695-a38c-0905d88cecf8`
