# Medidas DAX sugeridas

As medidas abaixo foram pensadas para o modelo no Power BI após carregar as tabelas analíticas do projeto.

## Medidas comerciais

```DAX
Receita Bruta =
SUM(fact_sales[gross_revenue])
```

```DAX
Receita Liquida =
SUM(fact_sales[net_revenue])
```

```DAX
COGS =
SUM(fact_sales[cogs])
```

```DAX
Margem Bruta =
SUM(fact_sales[gross_margin])
```

```DAX
Margem % =
DIVIDE([Margem Bruta], [Receita Liquida])
```

```DAX
Pedidos Entregues =
CALCULATE(
    DISTINCTCOUNT(fact_sales[order_id]),
    fact_sales[order_status] = "Delivered"
)
```

```DAX
Ticket Medio =
DIVIDE([Receita Liquida], [Pedidos Entregues])
```

```DAX
Unidades Vendidas =
SUM(fact_sales[quantity])
```

## Medidas de metas

```DAX
Meta Receita =
SUM(fact_targets[revenue_target])
```

```DAX
Aderencia Meta Receita =
DIVIDE([Receita Liquida], [Meta Receita])
```

```DAX
Desvio Meta Receita =
[Receita Liquida] - [Meta Receita]
```

## Medidas de suporte

```DAX
Desconto Medio =
AVERAGE(fact_sales[discount_pct])
```

```DAX
Receita Liquida M-1 =
CALCULATE(
    [Receita Liquida],
    DATEADD(dim_calendar[date], -1, MONTH)
)
```

```DAX
Crescimento Receita MoM =
DIVIDE([Receita Liquida] - [Receita Liquida M-1], [Receita Liquida M-1])
```

## Observacao

Para o calculo de crescimento mensal, recomenda-se criar uma tabela calendario (`dim_calendar`) no Power BI e relacionar com a data do pedido.
