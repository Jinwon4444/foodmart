SET SESSION FOREIGN_KEY_CHECKS=0;

/* Drop Tables */

DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS orderitem;
DROP TABLE IF EXISTS orderinfo;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS user;




/* Create Tables */

CREATE TABLE cart
(
	userid varchar(50) NOT NULL,
	productsid varchar(50) NOT NULL,
	quantity int
);


CREATE TABLE orderinfo
(
	orderno int NOT NULL AUTO_INCREMENT,
	userid varchar(50) NOT NULL,
	orderdate datetime default now(),
	PRIMARY KEY (orderno)
);


CREATE TABLE orderitem
(
	productsid varchar(50) NOT NULL,
	quantity int,
	orderprice int,
	orderno int NOT NULL
);


CREATE TABLE products
(
	productsid varchar(50) NOT NULL,
	productsname varchar(100),
	description text,
	price int,
	class varchar(50),
	productdate date default (current_date),
	PRIMARY KEY (productsid)
);


CREATE TABLE user
(
	userid varchar(50) NOT NULL,
	userpw varchar(50),
	PRIMARY KEY (userid)
);



/* Create Foreign Keys */

ALTER TABLE orderitem
	ADD FOREIGN KEY (orderno)
	REFERENCES orderinfo (orderno)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE cart
	ADD FOREIGN KEY (productsid)
	REFERENCES products (productsid)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE cart
	ADD FOREIGN KEY (userid)
	REFERENCES user (userid)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT,

	ADD CONSTRAINT uq_cart_user_product -- 유니크 제약 조건 이름
	UNIQUE (userid, productsid)
;


ALTER TABLE orderinfo
	ADD FOREIGN KEY (userid)
	REFERENCES user (userid)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE orderitem
	ADD FOREIGN KEY (productsid)
	REFERENCES products (productsid)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;



