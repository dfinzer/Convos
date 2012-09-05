ALTER TABLE conversation ADD user_one_twilio_number_id INT NOT NULL AFTER user_one_id;
ALTER TABLE conversation ADD user_two_twilio_number_id INT NOT NULL AFTER user_two_id;

ALTER TABLE sms_log ADD `twilio_number_id` INT NOT NULL AFTER phone_number;

# Change interest key for utf-8 support.
ALTER TABLE interest CHANGE name name VARCHAR(200);
ALTER TABLE interest MODIFY name VARCHAR(200) CHARACTER SET utf8;

ALTER TABLE user ADD `interested_in` VARCHAR( 10 ) AFTER college;
