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

CREATE OR REPLACE FUNCTION initialise()
RETURNS TRIGGER
LANGUAGE PLPGSQL
AS
$$
BEGIN
	INSERT INTO ratings (username)
	values (NEW.username);
  
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION rate_transaction()
RETURNS TRIGGER
LANGUAGE PLPGSQL
AS
$$
BEGIN
  IF NEW.ratings <> OLD.ratings THEN
	UPDATE ratings
	SET total_rating = total_rating + NEW.ratings, counts = counts + 1
	WHERE username = NEW.seller_username;
	END IF;
  
  RETURN NEW;
END;
$$;