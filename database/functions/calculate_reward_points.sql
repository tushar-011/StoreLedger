USE storeledger;

DROP FUNCTION IF EXISTS calculate_reward_points;

DELIMITER //

CREATE FUNCTION calculate_reward_points(
    bill_amount DECIMAL(10,2)
)
RETURNS INT
DETERMINISTIC
BEGIN

    DECLARE points INT;

    SET points = FLOOR(bill_amount / 100);

    RETURN points;

END //

DELIMITER ;