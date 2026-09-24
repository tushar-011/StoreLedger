USE storeledger;

DROP PROCEDURE IF EXISTS process_order_item;

DELIMITER //

CREATE PROCEDURE process_order_item(
    IN p_product_id INT,
    IN p_quantity INT
)
BEGIN

    DECLARE current_stock INT DEFAULT NULL;
    DECLARE current_product_name VARCHAR(150);

    SELECT
        product_name,
        stock
    INTO
        current_product_name,
        current_stock
    FROM products
    WHERE product_id = p_product_id
    FOR UPDATE;

    IF current_stock IS NULL THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product not found.';

    END IF;

    IF p_quantity <= 0 THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid quantity. Quantity must be greater than zero.';

    END IF;

    IF current_stock < p_quantity THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient stock for selected product.';

    END IF;

    UPDATE products
    SET stock = stock - p_quantity
    WHERE product_id = p_product_id;

END //

DELIMITER ;