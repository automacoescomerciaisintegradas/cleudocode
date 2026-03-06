# 🤗 Community Welcome Agent - Guia de Implementação

## Visão Geral

Este é um **assistente conversacional de acolhimento** projetado para atuar na linha de frente de comunidades de IA, aplicando a filosofia de que cada interação é uma oportunidade para criar uma conexão significativa.

### Funcionalidades

✅ **Acolhimento caloroso** - Saudação personalizada e humana  
✅ **Diagnóstico inteligente** - Detecta nível de conhecimento (Beginner/Intermediate/Advanced)  
✅ **Roteamento preciso** - Direciona para o recurso exato em até 3 mensagens  
✅ **Multi-plataforma** - Telegram, WhatsApp, Web Chat  
✅ **Memória de contexto** - Lembra do histórico do membro  

---

## 🚀 Quick Start

### 1. Teste Local (Imediato)

```bash
cd /root/cleudocode
python3 welcome_agent_chat.py
```

**Interação de exemplo:**
```
🤗 Olá! Seja bem-vindo à nossa comunidade de IA!
Fico feliz em ajudar você. Me conte: qual é sua necessidade hoje?

📨 Membro: Quero criar automações com IA mas não sei por onde começar

⏳ Processando...
📊 Nível detectado: BEGINNER

🤖 Welcome Agent: Que legal que você quer começar com automações de IA! 🎉
Vejo que você está iniciando nessa jornada. Vou te direcionar certinho!

📍 **Seu próximo passo:**

→ **Onboarding Guiado:** https://docs.cleudocode.com/iniciante
   - Tutorial passo a passo (15 min)
   - Exemplos práticos
   - Comunidade de iniciantes

💡 **Dica:** Comece pelo módulo 1 e depois volte se tiver dúvidas!

Quer que eu te acompanhe em algum ponto específico? Estou aqui! 😊
```

---

### 2. Telegram Bot (Produção)

#### Configuração

1. **Crie um bot no Telegram:**
   - Abra @BotFather no Telegram
   - Envie `/newbot`
   - Siga as instruções
   - Copie o token

2. **Adicione ao .env:**
   ```bash
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

3. **Instale dependências:**
   ```bash
   pip3 install python-telegram-bot
   ```

4. **Inicie o bot:**
   ```bash
   python3 telegram_welcome_bot.py
   ```

#### Comandos do Bot

| Comando | Descrição |
|---------|-----------|
| `/start` | Inicia acolhimento |
| `/help` | Mostra ajuda |
| `/status` | Mostra nível detectado |
| `/reset` | Reinicia conversa |

---

## 📋 Arquitetura

### Camada 1: Diretiva de Acolhimento

```
┌─────────────────────────────────────────┐
│         Membro envia mensagem           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  1. Saudação + Validação Empática       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  2. Diagnóstico (1-3 perguntas)         │
│     - Nível de conhecimento             │
│     - Necessidade específica            │
│     - Contexto/objetivo                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  3. Roteamento Preciso                  │
│     - 1 recurso exato (não múltiplo)    │
│     - Link direto                       │
│     - Próximos passos claros            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  4. Oferta de Follow-up                 │
│     - "Precisa de mais algo?"           │
│     - "Estou aqui se precisar!"         │
└─────────────────────────────────────────┘
```

### Matriz de Roteamento

| Nível | Características | Recurso Ideal |
|-------|----------------|---------------|
| **BEGINNER** | "O que é", "Como começar", nunca usou IA | Onboarding guiado, tutoriais, FAQ |
| **INTERMEDIATE** | "Como implementar X", já conhece conceitos | Documentação de API, templates, exemplos |
| **ADVANCED** | Otimização, arquitetura, sistemas complexos | Docs avançadas, engenharia direta, beta features |

---

## 🎯 Persona do Agente

O agente está definido em: `agents/welcome_agent.md`

### Princípios

✅ **SEJA:**
- Caloroso e humano (use emojis com moderação)
- Faça perguntas de diagnóstico ANTES de rotear
- Forneça links exatos (não "vá para a docs")
- Adapte linguagem ao nível detectado
- Mantenha respostas concisas (< 200 palavras)

❌ **NÃO SEJA:**
- Não despeje informação sem contexto
- Não use jargão com iniciantes
- Não roteie para múltiplos lugares (1 recurso ideal)
- Não faça o membro repetir-se
- Não soe robótico ou scriptado

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# .env

# Modelo LLM (Ollama)
WELCOME_MODEL=llama3:8b
OLLAMA_HOST=http://localhost:11434

# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui

# WhatsApp (futuro)
WHATSAPP_BASE_URL=http://localhost:8080
WHATSAPP_INSTANCE_NAME=default
```

### Modelos Recomendados

| Modelo | VRAM | Velocidade | Qualidade | Uso |
|--------|------|------------|-----------|-----|
| `llama3:8b` | 6GB | ⚡⚡⚡ | Boa | Produção (rápido) |
| `qwen2.5:14b` | 10GB | ⚡⚡ | Muito Boa | Balanceado |
| `mistral:7b` | 6GB | ⚡⚡⚡ | Boa | Alternativa |

---

## 📊 Monitoramento

### Logs de Interação

Cada interação é salva no histórico:

```python
user_contexts[user_id] = {
    "name": "Maria",
    "knowledge_level": "INTERMEDIATE",
    "history": [
        {"member": "...", "agent": "..."},
        ...
    ]
}
```

### Métricas Sugeridas

- ⏱️ **Tempo médio de resposta** (alvo: < 3s)
- 💬 **Mensagens por resolução** (alvo: ≤ 3)
- 🎯 **Taxa de roteamento correto** (alvo: > 85%)
- 😊 **Satisfação do membro** (pesquisa opcional)

---

## 🔄 Integração com Squad de Agentes

Este Welcome Agent é o **ponto de entrada** para o CleudoCode:

```
Membro → Welcome Agent → Especialistas
         (Camada 1)      (Camada 2+)
                         ├── @dev
                         ├── @support
                         ├── @commercial
                         └── @human (escalamento)
```

### Escalamento

Para casos complexos, use:

```python
# Encaminha para agente especializado
from orchestrator import orchestrator

result = orchestrator.receive_message({
    "text": mensagem_do_membro,
    "from": "telegram",
    "targeted_agent": "@dev"  # ou @support, @commercial
})
```

---

## 🧪 Testes

### Teste Rápido

```bash
# 1. Inicie o chat local
python3 welcome_agent_chat.py

# 2. Simule diferentes níveis:

# Iniciante:
"Quero aprender IA mas não sei nada"

# Intermediário:
"Como crio uma API com Flask?"

# Avançado:
"Qual a melhor arquitetura para escalar webhooks?"
```

### Teste de Diagnóstico

```bash
python3 -c "
from welcome_agent_chat import diagnose_knowledge_level

tests = [
    'O que é IA?',
    'Como implemento autenticação JWT?',
    'Qual melhor estratégia de cache para Redis cluster?'
]

for t in tests:
    level = diagnose_knowledge_level(t)
    print(f'{t[:40]}... → {level}')
"
```

---

## 📱 Exemplos de Respostas

### Cenário 1: Iniciante

**Membro:** "Oi, quero criar automações mas nunca usei IA"

**Welcome Agent:**
```
Olá! 👋 Que legal que você quer começar com automações de IA!

Fico muito feliz em te ajudar nessa jornada! 🎉

Para te direcionar da melhor forma, me conta:
1. Você já programou antes ou está começando do zero absoluto?
2. Tem algum projeto específico em mente ou quer explorar possibilidades?

Assim que você responder, já te encaminho para o recurso exato! 🚀
```

### Cenário 2: Intermediário

**Membro:** "Preciso integrar WhatsApp com meu sistema"

**Welcome Agent:**
```
Ótimo! Vejo que você já tem familiaridade com integrações. 🔧

📍 **Recurso ideal para você:**

→ **Documentação WhatsApp:** https://docs.cleudocode.com/whatsapp
   - Setup da Evolution API
   - Exemplo de webhook
   - Tempo estimado: 10 min

🔧 **Atalho:** Use o template `/start-whatsapp` que já tem a estrutura!

Precisa de ajuda com algum detalhe da implementação? Só chamar! 🚀
```

### Cenário 3: Avançado

**Membro:** "Qual melhor abordagem para escalar webhooks com 10k req/s?"

**Welcome Agent:**
```
Excelente pergunta! 🎯 Sua questão sobre arquitetura de webhooks em alta escala mostra que você já está em nível avançado.

📍 **Recursos especializados:**

→ **Arquitetura de Webhooks:** https://docs.cleudocode.com/arquitetura/webhooks
→ **Case Similar:** [link para discussão]
→ **Engenharia Direta:** @engineer-contact

🎯 **Sugestão:** Dada a complexidade, recomendo uma call técnica. Posso agendar?

À disposição para detalhes! 💪
```

---

## 🛠️ Troubleshooting

### Problema: Bot não responde no Telegram

**Solução:**
```bash
# Verifique o token
echo $TELEGRAM_BOT_TOKEN

# Teste conexão com API Telegram
curl https://api.telegram.org/bot<SEU_TOKEN>/getMe

# Reinicie o bot
pkill -f telegram_welcome_bot.py
python3 telegram_welcome_bot.py
```

### Problema: Diagnóstico incorreto

**Solução:**
- Ajuste o prompt em `diagnose_knowledge_level()`
- Use modelo mais capaz (ex: `qwen2.5:14b`)
- Adicione mais exemplos de treino

### Problema: Respostas muito longas

**Solução:**
- Reduza `temperature` no `chat_with_llm()` (0.5-0.7)
- Adicione instrução explícita: "Mantenha sob 150 palavras"
- Use modelo mais conciso

---

## 📚 Próximos Passos

1. ✅ **Teste local** - `python3 welcome_agent_chat.py`
2. 🔧 **Configure Telegram** - Crie bot via @BotFather
3. 🚀 **Deploy produção** - Execute `telegram_welcome_bot.py`
4. 📊 **Monitore métricas** - Ajuste com base em feedback
5. 🔄 **Integre especialistas** - Conecte com @dev, @support

---

## 🎉 Missão Cumprida

**Objetivo:** Todo membro deve se sentir ouvido, compreendido e equipado com o recurso exato em **até 3 trocas de mensagens**.

Boa sorte no acolhimento da sua comunidade! 🤗🚀
