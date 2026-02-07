---
name: weather
description: Obtém previsão do tempo atual e forecast (sem API key necessária).
homepage: https://wttr.in/:help
metadata:
  cleudocode:
    emoji: "🌤️"
    category: "utilities"
    requires:
      bins: ["curl"]
    install: []
---

# Weather Skill

Dois serviços gratuitos, sem necessidade de API keys.

## wttr.in (primário)

### Uso Rápido

```bash
curl -s "wttr.in/SaoPaulo?format=3"
# Output: São Paulo: ⛅️ +25°C
```

### Formato Compacto

```bash
curl -s "wttr.in/SaoPaulo?format=%l:+%c+%t+%h+%w"
# Output: São Paulo: ⛅️ +25°C 71% ↙5km/h
```

### Forecast Completo

```bash
curl -s "wttr.in/SaoPaulo?T"
```

### Códigos de Formato

| Código | Descrição |
|--------|-----------|
| `%c` | Condição (emoji) |
| `%t` | Temperatura |
| `%h` | Umidade |
| `%w` | Vento |
| `%l` | Localização |
| `%m` | Fase da lua |

### Dicas

- Codifique espaços na URL: `wttr.in/Rio+de+Janeiro`
- Códigos de aeroporto: `wttr.in/GRU`
- Unidades: `?m` (métrico) `?u` (USCS)
- Apenas hoje: `?1` · Apenas agora: `?0`
- PNG: `curl -s "wttr.in/Berlin.png" -o /tmp/weather.png`

## Open-Meteo (fallback, JSON)

Gratuito, sem chave, bom para uso programático:

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=-23.55&longitude=-46.63&current_weather=true"
```

Encontre coordenadas para uma cidade, depois consulte. Retorna JSON com temp, windspeed, weathercode.

**Docs:** https://open-meteo.com/en/docs

## Exemplos de Uso no Cleudocode

```python
# Consulta rápida
weather action:current location:"São Paulo"

# Forecast de 3 dias
weather action:forecast location:"Rio de Janeiro" days:3

# Formato JSON
weather action:current location:"Brasilia" format:json
```

## Notas

- Limitação de rate: ~1 req/s recomendado
- Para localizações específicas, use coordenadas
- Cache local recomendado para consultas frequentes
