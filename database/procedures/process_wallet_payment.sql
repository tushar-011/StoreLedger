USE storeledger;

DROP PROCEDURE IF EXISTS process_wallet_payment;

DELIMITER //

CREATE PROCEDURE process_wallet_payment(
    IN p_customer_id INT,
    IN p_amount DECIMAL(10,2),
    IN p_order_id INT
)
BEGIN

    DECLARE current_balance DECIMAL(10,2) DEFAULT NULL;
    DECLARE updated_balance DECIMAL(10,2);

    SELECT wallet_balance
    INTO current_balance
    FROM customers
    WHERE customer_id = p_customer_id
    FOR UPDATE;

    IF current_balance IS NULL THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid customer account.';

    END IF;

    IF p_amount <= 0 THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid wallet payment amount.';

    END IF;

    IF current_balance < p_amount THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient wallet balance.';

    END IF;

    SET updated_balance =
        current_balance - p_amount;

    UPDATE customers
    SET wallet_balance = updated_balance
    WHERE customer_id = p_customer_id;

    INSERT INTO wallet_transactions
    (
        customer_id,
        transaction_type,
        amount,
        balance_after,
        order_id
    )
    VALUES
    (
        p_customer_id,
        'PAYMENT',
        p_amount,
        updated_balance,
        p_order_id
    );

END //

DELIMITER ;