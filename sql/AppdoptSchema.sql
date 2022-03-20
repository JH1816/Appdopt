CREATE TABLE IF NOT EXISTS users(
	first_name VARCHAR(64) NOT NULL,
	last_name VARCHAR(64) NOT NULL,
	email VARCHAR(128) UNIQUE NOT NULL,
	username VARCHAR(50) PRIMARY KEY,
	phone_number VARCHAR(16) UNIQUE NOT NULL,
	password VARCHAR(50) NOT NULL
);
	
CREATE TABLE IF NOT EXISTS posts(
	post_id INTEGER PRIMARY KEY,
	username VARCHAR(50),
	pet VARCHAR(20) NOT NULL,
	breed VARCHAR(64) NOT NULL,
	date_of_post DATE NOT NULL,
	age_of_pet VARCHAR(16),
	price NUMERIC (10,2) NOT NULL CHECK(price >= 0),
	description VARCHAR(1200),
	title VARCHAR(128) NOT NULL,
	status VARCHAR(50) DEFAULT 'AVAILABLE',
	gender VARCHAR(6),
	FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE
	);
  
CREATE TABLE transactions(
	post_id INTEGER,
	date_of_sale DATE NOT NULL,
	seller_username VARCHAR(16) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
	buyer_username VARCHAR(16) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY (post_id, seller_username, buyer_username),
	FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE ON UPDATE CASCADE
);
