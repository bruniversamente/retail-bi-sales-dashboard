# Medidas DAX sugeridas

As medidas abaixo foram pensadas para o modelo no Power BI após carregar as tabelas analíticas do projeto.

## Medidas comerciais

```DAX
Receita Bruta =
CALCULATE(
    SUM(fact_sales[gross_revenue]),
    fact_sales[order_status] = "Delivered"
)
```

```DAX
Receita Líquida =
CALCULATE(
    SUM(fact_sales[net_revenue]),
    fact_sales[order_status] = "Delivered"
)
```

```DAX
COGS =
CALCULATE(
    SUM(fact_sales[cogs]),
    fact_sales[order_status] = "Delivered"
)
```

```DAX
Margem Bruta =
CALCULATE(
    SUM(fact_sales[gross_margin]),
    fact_sales[order_status] = "Delivered"
)
```

```DAX
Margem % =
DIVIDE([Margem Bruta], [Receita Líquida])
```

```DAX
Pedidos Entregues =
CALCULATE(
    DISTINCTCOUNT(fact_sales[order_id]),
    fact_sales[order_status] = "Delivered"
)
```

```DAX
Ticket Médio =
DIVIDE([Receita Líquida], [Pedidos Entregues])
```

```DAX
Unidades Vendidas =
CALCULATE(
    SUM(fact_sales[quantity]),
    fact_sales[order_status] = "Delivered"
)
```

## Medidas de metas

```DAX
Meta Receita =
SUM(fact_targets[revenue_target])
```

```DAX
Aderencia Meta Receita =
DIVIDE([Receita Líquida], [Meta Receita])
```

```DAX
Desvio Meta Receita =
[Receita Líquida] - [Meta Receita]
```

## Medidas de suporte

```DAX
Desconto Médio =
AVERAGE(fact_sales[discount_pct])
```

```DAX
Receita Líquida M-1 =
CALCULATE(
    [Receita Líquida],
    DATEADD(dim_calendar[date], -1, MONTH)
)
```

```DAX
Crescimento Receita MoM =
DIVIDE([Receita Líquida] - [Receita Líquida M-1], [Receita Líquida M-1])
```

## Observacao

Para o cálculo de crescimento mensal, recomenda-se criar uma tabela calendário (`dim_calendar`) no Power BI e relacionar com a data do pedido.

Pedidos cancelados devem ficar fora das medidas executivas de receita, margem e unidades vendidas. Eles podem aparecer em uma página de qualidade dos dados como receita potencial excluída.
