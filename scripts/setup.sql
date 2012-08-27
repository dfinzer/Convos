DROP USER 'devin'@'localhost';
CREATE USER 'devin'@'localhost' IDENTIFIED BY 'convos';
GRANT ALL PRIVILEGES ON *.* TO 'devin'@'localhost' WITH GRANT OPTION;
CREATE DATABASE convos;

CREATE TABLE  `convos`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR( 100 ),
  `first_name` VARCHAR ( 100 ),
  `last_name` VARCHAR ( 100 ),
  `email` VARCHAR ( 100 ),
  `locale` VARCHAR ( 100 ),
  `username` VARCHAR( 100 ),
  `gender` VARCHAR( 100 ),
  `fb_uid` VARCHAR( 100 ),
  `fb_verified` BOOLEAN,
  `registration_status` VARCHAR( 100 ) NOT NULL, -- Can be pending or registered.
  `verification_code` VARCHAR ( 100 ),
  `phone_number` VARCHAR ( 100 ),
  `paused` BOOLEAN,
  PRIMARY KEY (  `id` ),
  UNIQUE KEY (`fb_uid`)
) ENGINE = MYISAM;

CREATE TABLE `convos`.`conversation` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `user_one_id` INT NOT NULL,
  `user_two_id` INT NOT NULL,
  `in_progress` BOOLEAN,
  PRIMARY KEY (  `id` )
)

CREATE TABLE  `convos`.`message` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `conversation_id` INT NOT NULL,
  `from_user_id` INT NOT NULL,
  `body` VARCHAR (500) NOT NULL,
  PRIMARY KEY (  `id` )
) ENGINE = MYISAM;