# Blueprint do dashboard

Este documento descreve a proposta de dashboard em Power BI para o projeto.

## Pagina 1 - Visao Executiva

Objetivo: permitir leitura rapida da performance comercial.

### Cards principais

- Receita liquida
- Margem bruta
- Margem percentual
- Pedidos entregues
- Ticket medio
- Aderencia a meta de receita

### Graficos

1. Receita liquida por mes
2. Margem percentual por mes
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

## Pagina 2 - Diagnostico de margem

Objetivo: identificar categorias ou canais que vendem bem, mas tem rentabilidade baixa.

### Graficos

- Matriz de categoria e canal com margem percentual
- Grafico de dispersao: receita liquida e margem percentual
- Ranking de categorias por margem bruta
- Tabela de produtos com desconto medio e margem

## Pagina 3 - Qualidade dos dados

Objetivo: apoiar governanca e confiabilidade dos relatorios.

### Indicadores

- Pedidos sem itens
- Itens sem produto cadastrado
- Pedidos com cliente inexistente
- Descontos fora do intervalo esperado
- Pedidos cancelados com receita potencial

## Layout sugerido

A primeira versao deve ser simples e executiva: cards no topo, graficos centrais e tabela detalhada no rodape. O foco e clareza, leitura rapida e identificacao de desvios.
