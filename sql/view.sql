CREATE OR REPLACE VIEW ratings AS
SELECT first_name, last_name, email, username, phone_number, password, type, COALESCE(sum_of_ratings/NULLIF(total_number_of_rating, 0), 0) AS rating
FROM users;