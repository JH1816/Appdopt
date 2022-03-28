CREATE TABLE IF NOT EXISTS users(
	first_name VARCHAR(64) NOT NULL,
	last_name VARCHAR(64) NOT NULL,
	email VARCHAR(128) UNIQUE NOT NULL CHECK (email LIKE '_%@_%._%'),
	username VARCHAR(50) PRIMARY KEY,
	phone_number INTEGER UNIQUE NOT NULL CHECK (phone_number BETWEEN 80000000 AND 99999999),
	password VARCHAR(50) NOT NULL,
	type VARCHAR NOT NULL DEFAULT 'user' CHECK(type = 'user' OR type = 'admin'),
	total_number_of_rating INTEGER NOT NULL DEFAULT(0) CHECK (total_number_of_rating>=0),
	sum_of_ratings INTEGER NOT NULL DEFAULT(0) CHECK (sum_of_ratings>=0)
);
	
CREATE TABLE IF NOT EXISTS posts(
	post_id INTEGER PRIMARY KEY,
	username VARCHAR(50),
	pet VARCHAR(20) NOT NULL,
	breed VARCHAR(64) NOT NULL,
	date_of_post DATE NOT NULL,
	age_of_pet INTEGER NOT NULL CHECK(age_of_pet >=0),
	price NUMERIC (10,2) NOT NULL CHECK(price >= 0),
	description VARCHAR(1200),
	title VARCHAR(128) NOT NULL,
	status VARCHAR(50) DEFAULT 'AVAILABLE',
	gender VARCHAR(6),
	location VARCHAR(64) NOT NULL,
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
