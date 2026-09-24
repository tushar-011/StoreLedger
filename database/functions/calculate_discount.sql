USE storeledger;

DROP FUNCTION IF EXISTS calculate_discount;

DELIMITER //

CREATE FUNCTION calculate_discount(
    bill_amount DECIMAL(10,2)
)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN

    DECLARE discount_amount DECIMAL(10,2);

    IF bill_amount >= 10000 THEN

        SET discount_amount = bill_amount * 0.15;

    ELSEIF bill_amount >= 5000 THEN

        SET discount_amount = bill_amount * 0.10;

    ELSEIF bill_amount >= 1000 THEN

        SET discount_amount = bill_amount * 0.05;

    ELSE

        SET discount_amount = 0;

    END IF;

    RETURN discount_amount;

END //

DELIMITER ;