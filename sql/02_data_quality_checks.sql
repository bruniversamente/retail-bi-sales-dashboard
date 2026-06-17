-- Data quality checks for the retail BI model.
-- Run after sql/01_create_schema_duckdb.sql.

-- 1. Orders without items
SELECT
    orders.order_id,
    orders.order_date,
    orders.sales_channel
FROM dim_orders AS orders
LEFT JOIN fact_sales AS sales
    ON orders.order_id = sales.order_id
WHERE sales.order_item_id IS NULL;

-- 2. Items without a valid product
SELECT
    sales.order_item_id,
    sales.order_id,
    sales.product_id
FROM fact_sales AS sales
LEFT JOIN dim_products AS products
    ON sales.product_id = products.product_id
WHERE products.product_id IS NULL;

-- 3. Orders without a valid customer
SELECT
    orders.order_id,
    orders.customer_id
FROM dim_orders AS orders
LEFT JOIN dim_customers AS customers
    ON orders.customer_id = customers.customer_id
WHERE customers.customer_id IS NULL;

-- 4. Discounts outside the expected range
SELECT
    order_item_id,
    order_id,
    product_id,
    discount_pct
FROM fact_sales
WHERE discount_pct < 0 OR discount_pct > 1;

-- 5. Negative or zero price/cost values
SELECT
    order_item_id,
    order_id,
    product_id,
    unit_price,
    unit_cost
FROM fact_sales
WHERE unit_price <= 0 OR unit_cost <= 0;

-- 6. Cancelled orders with potential revenue
SELECT
    order_id,
    order_status,
    ROUND(SUM(net_revenue), 2) AS potential_net_revenue
FROM fact_sales
WHERE order_status = 'Cancelled'
GROUP BY order_id, order_status;

-- 7. Row count summary
SELECT 'dim_orders' AS table_name, COUNT(*) AS row_count FROM dim_orders
UNION ALL
SELECT 'fact_sales', COUNT(*) FROM fact_sales
UNION ALL
SELECT 'dim_products', COUNT(*) FROM dim_products
UNION ALL
SELECT 'dim_customers', COUNT(*) FROM dim_customers
UNION ALL
SELECT 'fact_targets', COUNT(*) FROM fact_targets;
