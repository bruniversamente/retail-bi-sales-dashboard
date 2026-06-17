-- Creates analytical tables from the synthetic CSV files.
-- Engine: DuckDB

CREATE OR REPLACE TABLE dim_orders AS
SELECT
    order_id,
    CAST(order_date AS DATE) AS order_date,
    customer_id,
    sales_channel,
    state,
    payment_method,
    order_status,
    CAST(shipping_days AS INTEGER) AS shipping_days,
    STRFTIME(CAST(order_date AS DATE), '%Y-%m') AS order_month
FROM read_csv_auto('data/sample_orders.csv');

CREATE OR REPLACE TABLE dim_products AS
SELECT
    product_id,
    category,
    subcategory,
    product_name
FROM read_csv_auto('data/sample_products.csv');

CREATE OR REPLACE TABLE dim_customers AS
SELECT
    customer_id,
    customer_segment,
    city,
    state,
    CAST(signup_date AS DATE) AS signup_date
FROM read_csv_auto('data/sample_customers.csv');

CREATE OR REPLACE TABLE fact_targets AS
SELECT
    target_month,
    sales_channel,
    CAST(revenue_target AS DOUBLE) AS revenue_target,
    CAST(margin_target_pct AS DOUBLE) AS margin_target_pct
FROM read_csv_auto('data/sample_targets.csv');

CREATE OR REPLACE TABLE fact_sales AS
SELECT
    item.order_item_id,
    item.order_id,
    item.product_id,
    orders.customer_id,
    orders.order_date,
    orders.order_month,
    orders.sales_channel,
    orders.state,
    orders.payment_method,
    orders.order_status,
    CAST(item.quantity AS INTEGER) AS quantity,
    CAST(item.unit_price AS DOUBLE) AS unit_price,
    CAST(item.unit_cost AS DOUBLE) AS unit_cost,
    CAST(item.discount_pct AS DOUBLE) AS discount_pct,
    ROUND(CAST(item.quantity AS DOUBLE) * CAST(item.unit_price AS DOUBLE), 2) AS gross_revenue,
    ROUND(CAST(item.quantity AS DOUBLE) * CAST(item.unit_price AS DOUBLE) * (1 - CAST(item.discount_pct AS DOUBLE)), 2) AS net_revenue,
    ROUND(CAST(item.quantity AS DOUBLE) * CAST(item.unit_cost AS DOUBLE), 2) AS cogs,
    ROUND(
        CAST(item.quantity AS DOUBLE) * CAST(item.unit_price AS DOUBLE) * (1 - CAST(item.discount_pct AS DOUBLE))
        - CAST(item.quantity AS DOUBLE) * CAST(item.unit_cost AS DOUBLE),
        2
    ) AS gross_margin
FROM read_csv_auto('data/sample_order_items.csv') AS item
LEFT JOIN dim_orders AS orders
    ON item.order_id = orders.order_id;

CREATE OR REPLACE VIEW vw_sales_enriched AS
SELECT
    sales.*,
    products.category,
    products.subcategory,
    products.product_name,
    customers.customer_segment,
    customers.city AS customer_city
FROM fact_sales AS sales
LEFT JOIN dim_products AS products
    ON sales.product_id = products.product_id
LEFT JOIN dim_customers AS customers
    ON sales.customer_id = customers.customer_id;
