USE storeledger;

DROP VIEW IF EXISTS low_stock_view;

CREATE VIEW low_stock_view AS
SELECT
    p.product_id,
    p.product_name,
    c.category_name,
    p.stock,
    p.minimum_stock,
    (p.minimum_stock - p.stock) AS shortage
FROM products p
LEFT JOIN categories c
    ON p.category_id = c.category_id
WHERE p.stock <= p.minimum_stock;