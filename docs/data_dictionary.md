# Dicionário de dados

## `sample_orders.csv`

| Campo | Descrição |
|---|---|
| `order_id` | Identificador único do pedido. |
| `order_date` | Data de criação do pedido. |
| `customer_id` | Identificador do cliente. |
| `sales_channel` | Canal de venda: E-commerce, Store ou Marketplace. |
| `state` | Unidade federativa de entrega/venda. |
| `payment_method` | Forma de pagamento. |
| `order_status` | Status do pedido. |
| `shipping_days` | Tempo de entrega em dias. |

## `sample_order_items.csv`

| Campo | Descrição |
|---|---|
| `order_item_id` | Identificador único do item. |
| `order_id` | Pedido relacionado. |
| `product_id` | Produto vendido. |
| `quantity` | Quantidade vendida. |
| `unit_price` | Preço unitário de venda. |
| `unit_cost` | Custo unitário do produto. |
| `discount_pct` | Percentual de desconto aplicado ao item. |

## `sample_products.csv`

| Campo | Descrição |
|---|---|
| `product_id` | Identificador do produto. |
| `category` | Categoria comercial. |
| `subcategory` | Subcategoria comercial. |
| `product_name` | Nome do produto. |

## `sample_customers.csv`

| Campo | Descrição |
|---|---|
| `customer_id` | Identificador do cliente. |
| `customer_segment` | Segmento do cliente: New ou Recurring. |
| `city` | Cidade do cliente. |
| `state` | UF do cliente. |
| `signup_date` | Data de cadastro. |

## `sample_targets.csv`

| Campo | Descrição |
|---|---|
| `target_month` | Mês da meta no formato `YYYY-MM`. |
| `sales_channel` | Canal de venda. |
| `revenue_target` | Meta de receita líquida. |
| `margin_target_pct` | Meta de margem percentual. |
