USE storeledger;

DROP VIEW IF EXISTS expiry_products_view;

CREATE VIEW expiry_products_view AS
SELECT
    p.product_id,
    p.product_name,
    c.category_name,
    p.stock,
    p.expiry_date,
    DATEDIFF(p.expiry_date, CURDATE()) AS days_remaining,

    CASE
        WHEN p.expiry_date < CURDATE()
            THEN 'Expired'

        WHEN DATEDIFF(p.expiry_date, CURDATE()) <= 7
            THEN 'Critical'

        WHEN DATEDIFF(p.expiry_date, CURDATE()) <= 30
            THEN 'Expiring Soon'

        ELSE 'Safe'
    END AS expiry_status

FROM products p

LEFT JOIN categories c
    ON p.category_id = c.category_id

WHERE p.expiry_date IS NOT NULL;