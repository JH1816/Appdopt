CREATE OR REPLACE FUNCTION change_ratings()
RETURNS TRIGGER
LANGUAGE PLPGSQL
AS
$$
BEGIN
  IF NEW.counts <> OLD.counts THEN
	UPDATE users
	SET rating = NEW.total_rating/NEW.counts
	WHERE username = NEW.username;
	END IF;
  
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION get_rating(user_name varchar)  
	RETURNS TABLE( 
    first_name VARCHAR(64),
	last_name VARCHAR(64),
	email VARCHAR(128),
	username VARCHAR(50),
	phone_number INTEGER,
	password VARCHAR(50),
	type VARCHAR,
	rating INTEGER
	) 
LANGUAGE SQL
AS $$ 
    SELECT first_name, last_name, email, username, phone_number, password, type, COALESCE(sum_of_ratings/NULLIF(total_number_of_rating, 0), 0) AS rating
	FROM users
 	WHERE username = user_name; 
$$; 

