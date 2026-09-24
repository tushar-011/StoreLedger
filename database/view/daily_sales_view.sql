DROP VIEW IF EXISTS daily_sales_view;

CREATE VIEW daily_sales_view AS
SELECT
    DATE(order_date) AS sale_date,
    COUNT(order_id) AS total_orders,
    SUM(subtotal) AS subtotal,
    SUM(discount) AS total_discount,
    SUM(tax) AS total_tax,
    SUM(total_amount) AS total_revenue
FROM orders
WHERE status = 'completed'
GROUP BY DATE(order_date);