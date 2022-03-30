CREATE TRIGGER rating_system
AFTER UPDATE ON ratings
FOR EACH ROW
EXECUTE PROCEDURE change_ratings();

CREATE TRIGGER initialiser
AFTER INSERT ON users
FOR EACH ROW
EXECUTE PROCEDURE initialise();

CREATE TRIGGER transaction_to_rating
AFTER UPDATE ON transactions
FOR EACH ROW
EXECUTE PROCEDURE rate_transaction();