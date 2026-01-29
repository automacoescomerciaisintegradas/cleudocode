# PRD - Sistema de Créditos e Precificação (Inspirado no Intelyze)

## 1. Visão Geral do Produto
O objetivo é criar um sistema de créditos "Pay-as-you-go" (pague pelo uso) integrado à automação local, onde cada ação (postagem, resposta, consulta) consome um valor específico de um saldo pré-carregado.

## 2. Modelagem Financeira (Benchmark Intelyze)
Baseado na análise técnica do modal, estes são os custos unitários que devemos implementar:

| Ação | Custo Estimado (BRL) |
| :--- | :--- |
| Publicação no Instagram | R$ 0,27 |
| Resposta "EU QUERO" Pública | R$ 0,09 |
| Resposta "EU QUERO" Privada | R$ 0,09 |
| Envio para Telegram | R$ 0,09 |
| Consulta Shopee (50 produtos) | R$ 0,09 |
| Envio para WooCommerce | R$ 0,27 |

## 3. Planos de Recarga
O sistema deve aceitar recargas fixas para gerar saldo de créditos:
- **Starter**: R$ 197
- **Professional**: R$ 499 (Recomendado)
- **Scale**: R$ 999
- **Enterprise**: R$ 1.999

## 4. Requisitos Funcionais (Automáticos)
1. **Consumo em Tempo Real**: A cada execução da automação, o sistema deve verificar se há saldo suficiente antes de disparar a API (Instagram/Shopee).
2. **Histórico de Uso**: Log detalhado de cada débito (Data, Ação, Valor, Saldo Restante).
3. **Notificação de Saldo Baixo**: Alerta visual no app quando o saldo estiver abaixo de 10% do valor da última recarga.

## 5. Interface Sugerida (Layout)
- **Tema**: Dark Mode (Background: `#0d1117`, Text: `#ffffff`).
- **Cards de Preço**: Bordas com gradiente roxo/azul para destacar planos profissionais.
- **Seletor Dinâmico**: Um dropdown (similar ao `@e14`) para simular custos antes da execução.

## 6. Integração Técnica para a Automação Local
Para adaptar sua automação local, use o seguinte mapeamento de seletores (CSS) encontrados:
- **Seletor de Planos**: `#precos` ou `.pricing-select`
- **Tabela de Custos**: `.cost-table` ou `.modal-body select`
