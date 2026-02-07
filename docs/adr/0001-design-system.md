# ADR 0001: Cleudocode Gateway Design System

## Status
**Aceito** - 2026-02-07

## Contexto
O ecossistema Cleudocode necessita de uma interface de usuário (Gateway UI) profissional, coesa e moderna para gerenciar agentes e configurações. A "Automações Comerciais Integradas" definiu uma identidade visual específica que deve ser respeitada.

## Decisão
Adotamos o **Cleudocode Gateway Design System v1.0.0** como fonte única de verdade para estilos e componentes. A implementação técnica será via **CSS Variables** no Frontend React, garantindo consistência e facilidade de manutenção.

### Estrutura de Cores e Tipografia
- **Cor Primária:** `#E54D42` (Vermelho Vibrante)
- **Fundo:** `#F9FAFB` (Cinza muito claro) com Sidebar `#F3F4F6`.
- **Tipografia:**
  - UI: `Inter`, system-ui.
  - Código: `JetBrains Mono`, monospace.

## Definição Técnica (JSON Source)
```json
{
  "name": "cleudocode Gateway Design System",
  "version": "1.0.0",
  "author": "Automações Comerciais Integradas",
  "palette": {
    "primary": {
      "main": "#E54D42",
      "contrastText": "#FFFFFF"
    },
    "background": {
      "default": "#F9FAFB",
      "paper": "#FFFFFF",
      "sidebar": "#F3F4F6"
    },
    "text": {
      "primary": "#111827",
      "secondary": "#6B7280",
      "disabled": "#9CA3AF"
    },
    "status": {
      "success": "#10B981",
      "error": "#FEE2E2",
      "errorText": "#991B1B"
    },
    "border": "#E5E7EB"
  },
  "typography": {
    "fontFamily": {
      "sans": "Inter, system-ui, sans-serif",
      "mono": "JetBrains Mono, Fira Code, monospace"
    },
    "hierarchy": {
      "h1": { "size": "24px", "weight": "700" },
      "body": { "size": "14px", "weight": "400" },
      "label": { "size": "12px", "weight": "500" },
      "code": { "size": "13px", "lineHeight": "1.6" }
    }
  },
  "spacing": {
    "base": 4,
    "unit": "px",
    "margins": {
      "container": "24px",
      "cardPadding": "16px"
    }
  },
  "components": {
    "button": {
      "borderRadius": "6px",
      "padding": "8px 16px",
      "fontSize": "14px"
    },
    "card": {
      "borderRadius": "8px",
      "border": "1px solid #E5E7EB",
      "shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)"
    },
    "sidebar": {
      "width": "240px",
      "itemActive": {
        "bg": "#FEE2E2",
        "text": "#E54D42"
      }
    },
    "editor": {
      "bg": "#FFFFFF",
      "errorOverlay": {
        "bg": "rgba(254, 226, 226, 0.5)",
        "border": "#FCA5A5"
      }
    }
  }
}
```

## Consequências
1.  **Implementação:** O arquivo `frontend/src/index.css` deve refletir essas variáveis.
2.  **Componentes:** Novos componentes React devem utilizar essas variáveis para manter a consistência visual.
3.  **Manutenção:** Alterações no Design System devem ser refletidas nesta ADR e propagadas para o código.
