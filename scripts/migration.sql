ALTER TABLE conversation ADD user_one_twilio_number_id INT NOT NULL AFTER user_one_id;
ALTER TABLE conversation ADD user_two_twilio_number_id INT NOT NULL AFTER user_two_id;

ALTER TABLE sms_log ADD `twilio_number_id` INT NOT NULL AFTER phone_number;