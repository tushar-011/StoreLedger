USE storeledger;

DROP TRIGGER IF EXISTS product_update_audit;

DELIMITER //

CREATE TRIGGER product_update_audit
AFTER UPDATE ON products
FOR EACH ROW
BEGIN

    INSERT INTO audit_log
    (
        table_name,
        operation,
        record_id,
        old_value,
        new_value
    )
    VALUES
    (
        'products',
        'UPDATE',
        OLD.product_id,

        CONCAT(
            'name=', OLD.product_name,
            ', price=', OLD.price,
            ', stock=', OLD.stock,
            ', minimum_stock=', OLD.minimum_stock
        ),

        CONCAT(
            'name=', NEW.product_name,
            ', price=', NEW.price,
            ', stock=', NEW.stock,
            ', minimum_stock=', NEW.minimum_stock
        )
    );

END //

DELIMITER ;