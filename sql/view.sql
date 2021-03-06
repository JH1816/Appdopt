CREATE OR REPLACE VIEW pending_transactions AS
SELECT p.post_id, p.pet, p.breed, p.age_of_pet, p.price, p.description, p.title, p.gender, 
location, t.date_of_sale, t.seller_username, t.buyer_username, t.stat, su.phone_number as seller_phone_num,
bu.phone_number as buyer_phone_num
FROM posts p
NATURAL JOIN transactions t
inner join users su on su.username = t.seller_username
inner join users bu on bu.username = t.buyer_username;