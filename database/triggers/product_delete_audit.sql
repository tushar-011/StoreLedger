DROP TRIGGER IF EXISTS product_delete_audit;

DELIMITER //

CREATE TRIGGER product_delete_audit
BEFORE DELETE ON products
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
        'DELETE',
        OLD.product_id,

        CONCAT(
            'name=', OLD.product_name,
            ', price=', OLD.price,
            ', stock=', OLD.stock
        ),

        NULL
    );

END //

DELIMITER ;