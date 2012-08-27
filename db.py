import MySQLdb
import MySQLdb.cursors

DATABASE = "convos"
PASSWORD = "convos"

db = MySQLdb.connect(db=DATABASE, passwd=PASSWORD, cursorclass=MySQLdb.cursors.DictCursor)

# Inserts a new user with pending registration status into the table.
def insertUserFromFacebookData(facebookData):
  cursor = db.cursor()
  
  # TODO: check if the necessary user data is actually there.
  # Insert a new user if one with the specified fb_uid does not already exist.
  cursor.execute("""INSERT INTO user (name, first_name, last_name, email, locale, username, gender, fb_uid, fb_verified, registration_status) \
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", \
    (facebookData["name"], \
    facebookData["first_name"], \
    facebookData["last_name"], \
    facebookData["email"], \
    facebookData["locale"], \
    facebookData["username"], \
    facebookData["gender"], \
    facebookData["id"], \
    facebookData["verified"], \
    "pending"))
  db.commit()

# Gets a user with the specified id.
def getUserFromFacebookUid(facebookUid):
  cursor = db.cursor()
  cursor.execute("""SELECT * FROM user WHERE fb_uid = %s""", (facebookUid))
  return cursor.fetchone()