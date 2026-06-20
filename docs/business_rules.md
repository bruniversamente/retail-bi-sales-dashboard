# Regras de negócio

## Escopo da análise

A análise considera uma operação de varejo com três canais de venda:

- E-commerce
- Loja física (`Store`)
- Marketplace

Os dados são sintéticos e simulam pedidos, itens vendidos, produtos, clientes e metas comerciais.

## Regras de cálculo

### Receita bruta

Valor total antes do desconto aplicado no item.

```text
receita_bruta = quantidade * preco_unitario
```

### Receita líquida

Valor total depois do desconto aplicado no item.

```text
receita_liquida = quantidade * preco_unitario * (1 - percentual_desconto)
```

### Custo dos produtos vendidos

```text
cogs = quantidade * custo_unitario
```

### Margem bruta

```text
margem_bruta = receita_liquida - cogs
```

### Margem percentual

```text
margem_percentual = margem_bruta / receita_liquida
```

### Ticket médio

```text
ticket_medio = receita_liquida / quantidade_de_pedidos_entregues
```

## Filtros de negócio

- Pedidos cancelados não devem compor KPIs comerciais finais.
- A receita e a margem devem ser calculadas no nível do item do pedido.
- As metas são avaliadas por mês e canal.
- A margem percentual deve ignorar divisões por zero.
- O dashboard executivo pode ser publicado somente quando não houver falhas críticas de qualidade.

## Qualidade dos dados

Falhas críticas bloqueiam publicação:

- pedidos sem itens;
- itens sem produto válido;
- pedidos sem cliente válido;
- descontos fora de 0 a 1;
- preços ou custos menores ou iguais a zero.

Warnings não bloqueiam publicação por si só, mas devem ser monitorados:

- pedidos cancelados com receita potencial.

Na execução atual, o status de publicação é `Approved`: zero falhas críticas e 256 warnings monitorados fora dos KPIs executivos.

## Perguntas respondidas pelo dashboard

- Qual foi o desempenho mensal de receita e margem?
- Quais canais e categorias concentram receita?
- Quais categorias têm boa venda, mas baixa rentabilidade?
- O resultado realizado ficou acima ou abaixo da meta?
- Há sinais de inconsistência nos dados antes da publicação dos relatórios?
