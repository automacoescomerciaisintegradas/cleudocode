---
description: Design System Intelligence Pro (ui-ux-pro-max)
---

```
design-system/
├── MASTER.md                # Fonte global de verdade (tokens + regras + padrões)
├── RULES.md                 # Regras de raciocínio (indústria, conversão, acessibilidade)
├── TOKENS.md                # Design tokens (cores, tipografia, spacing, radius, shadows)
├── UX-GUIDELINES.md         # 99 UX guidelines normalizadas
├── STACKS/
│   ├── html-tailwind.md
│   ├── react.md
│   ├── nextjs.md
│   ├── shadcn.md
│   └── mobile.md
└── pages/
    ├── dashboard.md
    ├── checkout.md
    ├── landing.md
    └── auth.md
```

Isso transforma o `ui-ux-pro-max` em um **motor de decisão + memória persistente + hierarquia de overrides**.

---

# MASTER.md (Padrão Global Integrado)

Este MASTER consolida seu README + a Skill que criamos:

```md
# DESIGN SYSTEM MASTER — UI/UX PRO MAX

SYSTEM: ui-ux-pro-max
ROLE: AI-powered design intelligence + automated design system generation
VERSION: 2.0

---

## CORE CAPABILITIES

- 50+ UI Styles
- 97+ Color Palettes
- 57 Font Pairings
- 99 UX Guidelines
- 25 Chart Types
- 9 Technology Stacks
- Priority-based recommendations
- Hierarchical override system

---

## GLOBAL DESIGN FLOW (MANDATORY)

1. Analyze Product + Industry + Keywords
2. Generate Design System (--design-system)
3. Apply Reasoning Rules
4. Persist Master + Page Overrides
5. Apply Stack-Specific Guidelines
6. Validate with Pre-Delivery Checklist

---

## DEFAULT DECISION ENGINE

IF request involves UI/UX:
  REQUIRE --design-system

IF industry detected:
  APPLY industry-specific style + palette rules

IF goal == conversion:
  APPLY hero-centric + social proof patterns

IF premium OR luxury:
  USE serif headlines
  INCREASE whitespace
  RESTRICT accent colors

IF dashboard OR data-heavy:
  PRIORITIZE readability
  OVERRIDE serif to sans-serif

---

## PATTERN SYSTEM (GLOBAL)

Available Patterns:
- Hero-Centric + Social Proof
- Feature-Driven SaaS
- Pricing-First
- Authority/Expertise
- Conversion-Optimized Funnel
- Dashboard/Data-Centric
- Marketplace Grid
- Portfolio Editorial

---

## STYLE ENGINE (GLOBAL)

Styles Database:
- Soft UI Evolution
- Minimal Pro
- Glassmorphism
- Brutalism
- Corporate Clean
- Luxury Editorial
- Neo-Morphism
- Material-Inspired
- Dark Premium
- Playful Gradient
(… up to 50+)

---

## ACCESSIBILITY & QUALITY GATES (NON-NEGOTIABLE)

- WCAG AA minimum
- Keyboard navigation
- Focus states visible
- prefers-reduced-motion respected
- Contrast ≥ 4.5:1
```

---

# RULES.md (Motor de Raciocínio Formal)

Transforma seu CSV lógico em governança explícita:

```md
# DESIGN REASONING RULES

IF industry == healthcare OR wellness:
  DISALLOW harsh contrast
  DISALLOW aggressive animation
  REQUIRE calm palette

IF industry == fintech:
  PRIORITIZE trust colors (blue/neutral)
  AVOID playful gradients

IF product == dashboard:
  PRIORITIZE data density + readability
  OVERRIDE serif typography

IF product == landing:
  ENFORCE hero + CTA above fold
  REQUIRE testimonials if B2C

IF stack == html-tailwind:
  ENFORCE utility-first patterns
  REQUIRE responsive utilities

IF accessibility == required:
  BLOCK low-opacity glass
  BLOCK low-contrast text
```

---

# TOKENS.md (Design Tokens Normalizados)

```md
# DESIGN TOKENS

## COLORS
--color-primary
--color-secondary
--color-accent
--color-bg
--color-text

## TYPOGRAPHY
--font-heading
--font-body
--font-mono

## SPACING
--space-xs
--space-sm
--space-md
--space-lg
--space-xl

## RADIUS
--radius-sm
--radius-md
--radius-lg

## SHADOWS
--shadow-soft
--shadow-md
--shadow-lg
```

---

# Integração Direta com seu Workflow CLI

Seu README vira a **camada de orquestração**, e o Design System vira a **camada de memória + governança**.

### Fluxo Final Profissional

```bash
# 1. Geração do Design System
python3 .shared/ui-ux-pro-max/scripts/search.py \
  "beauty spa wellness service elegant" \
  --design-system \
  --persist \
  -p "Serenity Spa"

# 2. Cria:
design-system/MASTER.md
design-system/pages/landing.md
```

### Hierarquia de Resolução (como agente deve pensar)

1. Verifica `design-system/pages/{page}.md`
2. Aplica overrides
3. Herda tudo do `MASTER.md`
4. Aplica `STACK/{stack}.md`
5. Valida com checklist global

