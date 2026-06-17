-- KPI queries for the retail BI dashboard.
-- Run after sql/01_create_schema_duckdb.sql.

-- 1. Executive KPI summary
SELECT
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_margin), 2) AS gross_margin,
    ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin_pct,
    COUNT(DISTINCT order_id) AS delivered_orders,
    ROUND(SUM(net_revenue) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS average_ticket,
    SUM(quantity) AS units_sold
FROM vw_sales_enriched
WHERE order_status = 'Delivered';

-- 2. Monthly performance
SELECT
    order_month,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_margin), 2) AS gross_margin,
    ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin_pct,
    COUNT(DISTINCT order_id) AS delivered_orders
FROM vw_sales_enriched
WHERE order_status = 'Delivered'
GROUP BY order_month
ORDER BY order_month;

-- 3. Performance by channel
SELECT
    sales_channel,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_margin), 2) AS gross_margin,
    ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin_pct,
    COUNT(DISTINCT order_id) AS delivered_orders
FROM vw_sales_enriched
WHERE order_status = 'Delivered'
GROUP BY sales_channel
ORDER BY net_revenue DESC;

-- 4. Performance by category
SELECT
    category,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_margin), 2) AS gross_margin,
    ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin_pct,
    SUM(quantity) AS units_sold
FROM vw_sales_enriched
WHERE order_status = 'Delivered'
GROUP BY category
ORDER BY net_revenue DESC;

-- 5. Revenue target tracking by month and channel
WITH realized AS (
    SELECT
        order_month AS target_month,
        sales_channel,
        ROUND(SUM(net_revenue), 2) AS realized_revenue,
        ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS realized_margin_pct
    FROM vw_sales_enriched
    WHERE order_status = 'Delivered'
    GROUP BY order_month, sales_channel
)
SELECT
    targets.target_month,
    targets.sales_channel,
    targets.revenue_target,
    COALESCE(realized.realized_revenue, 0) AS realized_revenue,
    ROUND(COALESCE(realized.realized_revenue, 0) / NULLIF(targets.revenue_target, 0), 4) AS revenue_target_attainment,
    targets.margin_target_pct,
    realized.realized_margin_pct
FROM fact_targets AS targets
LEFT JOIN realized
    ON targets.target_month = realized.target_month
    AND targets.sales_channel = realized.sales_channel
ORDER BY targets.target_month, targets.sales_channel;

-- 6. Product ranking
SELECT
    product_name,
    category,
    SUM(quantity) AS units_sold,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_margin), 2) AS gross_margin,
    ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin_pct
FROM vw_sales_enriched
WHERE order_status = 'Delivered'
GROUP BY product_name, category
ORDER BY net_revenue DESC;
