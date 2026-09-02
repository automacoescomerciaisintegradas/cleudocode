# CRONS E DISPAROS — Ofertas Shopee (WhatsApp + Telegram)

Documentação do esquema de disparos automáticos do projeto **cleudocode**.
Última revisão: **31/08/2026** — após banimento do número de WhatsApp causado por
volume/frequência de envio em massa.

---

## 1. Objetivo

Enviar ofertas da Shopee (com imagem gerada) para o **grupo do WhatsApp** e
**grupo do Telegram**, além de campanhas em massa para contatos privados
(Evolution API), de forma **automática e com volume seguro** para não derrubar a
conta do WhatsApp.

---

## 2. Controle "bot_gate" (LIGA/DESLIGA global)

Tudo passa por uma **flag em arquivo** `.bot_on`:

| Modo | Comando | Efeito |
|---|---|---|
| Ligar | `bash /root/cleudocode/scripts/bot_gate.sh on` | Cria `./.bot_on` → disparos liberados |
| Desligar | `bash /root/cleudocode/scripts/bot_gate.sh off` | Remove `./.bot_on` → disparos bloqueados |
| Ver estado | `bash /root/cleudocode/scripts/bot_gate.sh` | Mostra `ON` ou `OFF` |

> **Regra de ouro:** as rotinas (`rotina_ofertas.sh`, `disparo_campanha_ofertas.py`)
> **não disparam** se a flag `.bot_on` não existir. Dessa forma dá para pausar tudo
> com um único comando, sem mexer no crontab.

Log das mudanças de estado: `logs/bot_gate.log`.

---

## 3. Crons atuais

Verifique sempre com `crontab -l`.

| Cron | Frequência | O que faz |
|---|---|---|
| `rotate_secrets.py` | dia 1 de cada mês, 03:00 | Rotaciona segredos |
| `enviar-mensagem-aviso-imagem.js` | seg–sex 20:00 e sáb 11:59 | Aviso/divulgação da comunidade |
| `disparo_campanha_ofertas.py` | **REMOVA** (cron removida 31/08) | **Envio em massa para números privados — DESATIVADO** (causa de banimento) |
| `rotina_ofertas.sh` | **12:00 e 19:00** (era 8x/dia) | Sorteia produto+template, gera card e envia **só p/ grupos/comunidades autorizados** |

### Janelas do `bot_gate` (liberam só nos minutos dos disparos)

| Janela | Frequência | Ação |
|---|---|---|
| 11:45 / 18:45 | todos os dias | `bot_gate on` (prepara rotina das 12h/19h) |
| 12:20 / 19:20 | todos os dias | `bot_gate off` |

### Resumo de volume atual (após banimento)

| Tipo | Antes | Agora |
|---|---|---|
| Campanha em massa (privados) | todos os dias · 50 contatos | **REMOVIDA** — não envia mais p/ números privados |
| Rotina do grupo | 8x/dia | **2x/dia** (12h e 19h) |

---

## 4. Configuração anti-ban (`.env`)

Chaves usadas pelos disparos:

```dotenv
# Controle do disparo em massa
DELAY_SEGUNDOS=30        # espera entre mensagens — 30s p/ reduzir risco
MAX_DISPATCH=10          # máx de contatos por execução — reduziu de 50
PRODUTO_OFERTA=Smartwatch lançamento com GPS e NFC
```

- Arquivo de contatos: `telefones_contatos.csv` (colunas `nome`,`telefone`).
- Hoje o CSV tem ~1.896 linhas — a campanha percorre a lista limitada por `MAX_DISPATCH`.
- Altere esses valores no `.env` e ajuste o cron conforme necessário.

---

## 5. Como os scripts funcionam

### `rotina_ofertas.sh`
1. Só roda se a flag `.bot_on` existir (senão, loga "rotina bloqueada (bot OFF)").
2. Sorteia um template de `templates/card_*.html`.
3. Chama `gerador_ofertas_imagem.py --template "$TEMPLATE" --skip-grok`
   (rápido, sem passar pelo limite do Grok).
4. Envia o card gerado para **todos os grupos/comunidades autorizados** (WhatsApp
   `WHATSAPP_TARGET_NUMBER` — apenas `@g.us`/`@newsletter`/`@lid`) e para o canal
   **Telegram** (`TELEGRAM_SHOPEE_GROUP`), logando em `logs/gerador_ofertas.log`.

### `disparo_campanha_ofertas.py` — ⛔ desativado (envio privado)
- **Não envia mais para números privados.** A cron foi removida e o CSV de contatos
  (`telefones_contatos.csv`) foi renomeado para `telefones_contatos.csv.bak.disabled`.
- O script hoje recusa qualquer destino que não seja grupo (`@g.us`/`@newsletter`/`@lid`),
  e só aceita `WHATSAPP_TARGET_NUMBER`.

> ⚠️ **Você foi banido do WhatsApp justamente por disparo em massa para números
> privados** (47/50 enviados num dia, 8s de intervalo, todos os dias). Regra vigente:
> **envio somente para grupos/comunidades autorizados, jamais para números privados.**

### 🔐 Comunidades autorizadas

Os destinos de oferta (WhatsApp) ficam em `WHATSAPP_TARGET_NUMBER` no `.env` e
**podem conter somente grupos**: `@g.us`, `@newsletter`, `@lid`.

```dotenv
WHATSAPP_TARGET_NUMBER=120363233646051433@g.us,120363400374739099@g.us,
  120363315911301132@g.us,120363303322478556@newsletter,120363306948488101@g.us,
  120363266064963949@g.us,7649437450420@lid,120363401055015181@g.us,
  120363408349493210@g.us,120363409789699048@g.us
WHATSAPP_SHOPEE_GROUP=120363408349493210@g.us   # grupo fixo das ofertas (Comunidade Principal)
TELEGRAM_SHOPEE_GROUP=-1002795748070           # canal Telegram oficial das ofertas
```

> Nunca adicione números privados (`55889...@s.whatsapp.net` / `8 dígitos@c.us`) nessa lista —
> isso causa banimento.

---

## 6. Logs úteis

| Log | Conteúdo |
|---|---|
| `logs/gerador_ofertas.log` | Execuções da rotina do grupo (card, envios) |
| `logs/cron_ofertas.log` | Execuções da campanha em massa |
| `logs/bot_gate.log` | Liga/desliga do bot |

---

## 7. Procedimento pós-banimento (recomendado)

1. **NÃO relique o bot** (`bot_gate on`) até o número ser liberado pelo WhatsApp.
   Aguarde, tipicamente, 1 a 14 dias, e diminua ainda mais o volume nessas janelas
   iniciais (ex.: `MAX_DISPATCH=3`, delay 60s, rotina 1x/dia).
2. Para disparos futuros, **prefira grupo/canal** em vez de mensagens privadas.
3. Ajuste frequência em `crontab -l` conforme o comportamento do número.

---

## 8. Como religar/desligar manualmente

```bash
# Desligar tudo (recomendado enquanto o número se recupera)
bash /root/cleudocode/scripts/bot_gate.sh off

# Ligar quando liberar
bash /root/cleudocode/scripts/bot_gate.sh on

# Disparar a rotina do grupo agora (manual)
cd /root/cleudocode && bash rotina_ofertas.sh
```