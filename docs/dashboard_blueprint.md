# Blueprint do dashboard

Este documento descreve o dashboard executivo do projeto. A versão HTML gerada em `dashboard/retail_bi_sales_dashboard.html` funciona como preview revisável e a pasta `powerbi/` documenta as medidas para implementação em Power BI.

## Página 1 - Visão Executiva

Objetivo: permitir leitura rápida da performance comercial.

### Cards principais

- Receita líquida
- Margem bruta
- Margem percentual
- Pedidos entregues
- Ticket médio
- Aderencia a meta de receita

### Gráficos

1. Receita líquida por mês
2. Margem percentual por mês
3. Receita por canal
4. Receita e margem por categoria
5. Receita por estado
6. Tabela de produtos com receita, margem e quantidade

### Filtros

- Periodo
- Canal
- Categoria
- Estado
- Segmento de cliente

## Página 2 - Diagnostico de margem

Objetivo: identificar categorias ou canais que vendem bem, mas tem rentabilidade baixa.

### Gráficos

- Matriz de categoria e canal com margem percentual
- Gráfico de dispersão: receita líquida e margem percentual
- Ranking de categorias por margem bruta
- Tabela de produtos com desconto médio e margem

## Página 3 - Qualidade dos dados

Objetivo: apoiar governança e confiabilidade dos relatórios.

### Indicadores

- Pedidos sem itens
- Itens sem produto cadastrado
- Pedidos com cliente inexistente
- Descontos fora do intervalo esperado
- Pedidos cancelados com receita potencial

## Layout sugerido

A primeira versão deve ser simples e executiva: cards no topo, gráficos centrais e tabela detalhada no rodapé. O foco e clareza, leitura rápida e identificação de desvios.

## Versão entregue no repositório

A versão atual inclui:

- cards de receita líquida, margem bruta, margem percentual, pedidos, ticket médio e unidades;
- receita por canal;
- acompanhamento de metas por mês e canal;
- performance mensal;
- performance por categoria;
- gate de qualidade dos dados.

O dashboard usa dados exportados por `scripts/build_outputs.py` e não depende de serviço externo para abrir localmente.
