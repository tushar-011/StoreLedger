USE storeledger;

DROP PROCEDURE IF EXISTS add_reward_points;

DELIMITER //

CREATE PROCEDURE add_reward_points(
    IN p_customer_id INT,
    IN p_bill_amount DECIMAL(10,2)
)
BEGIN

    DECLARE points_to_add INT;

    IF p_customer_id IS NOT NULL THEN

        SET points_to_add =
            calculate_reward_points(p_bill_amount);

        UPDATE customers
        SET reward_points =
            reward_points + points_to_add
        WHERE customer_id = p_customer_id;

    END IF;

END //

DELIMITER ;