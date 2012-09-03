Setup on EC2:
To set up on EC2, follow the instructions at https://github.com/d5/docs/wiki/Installing-Flask-on-Amazon-EC2

You will also need to do the following:
1. yum install mysql-devel
2. Install everything in requirements.txt.
3. Set up static file serving correctly. (TODO: write down what I did for this.)
4. Convert the database to UTF-8.

Ending a conversation:
curl -X POST http://localhost:10080/api/end_conversation -d user_id=20 -d user_twilio_number_id=4

Converting database to UTF-8:
mysqldump -u$1 -p$2 -c -e --default-character-set=utf8 --single-transaction --skip-set-charset --add-drop-database -B $3 > dump.sql
sed 's/DEFAULT CHARACTER SET latin1/DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci/' <dump.sql | sed 's/DEFAULT CHARSET=latin1/DEFAULT CHARSET=utf8/' >dump-fixed.sql
mysql -u$1 -p$2 < dump-fixed.sql

Extra notes:s
convos12345 is a password for something.