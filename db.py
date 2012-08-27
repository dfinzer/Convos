import MySQLdb
import MySQLdb.cursors

DATABASE = "convos"
PASSWORD = "convos"

db = MySQLdb.connect(db=DATABASE, passwd=PASSWORD, cursorclass=MySQLdb.cursors.DictCursor)

# Users:
# Inserts a new user with pending registration status and specified verification code into the table.
def insertUserFromFacebookData(facebookData, verificationCode):
  cursor = db.cursor()
  
  # TODO: check if the necessary user data is actually there.
  # Insert a new user if one with the specified fb_uid does not already exist.
  cursor.execute("""INSERT INTO user (name, first_name, last_name, email, locale, username, gender, \
    fb_uid, fb_verified, registration_status, verification_code) \
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", \
    (facebookData["name"], \
    facebookData["first_name"], \
    facebookData["last_name"], \
    facebookData["email"], \
    facebookData["locale"], \
    facebookData["username"], \
    facebookData["gender"], \
    facebookData["id"], \
    facebookData["verified"], \
    "pending", \
    verificationCode))
  db.commit()

# Gets a user with the specified id.
def getUserFromFacebookUid(facebookUid):
  cursor = db.cursor()
  cursor.execute("""SELECT * FROM user WHERE fb_uid = %s""", (facebookUid))
  return cursor.fetchone()
  
# Gets a user with the specified verification code (assumes this user is pending registration).
def getUserFromVerificationCode(verificationCode):
  cursor = db.cursor()
  cursor.execute("""SELECT * FROM user WHERE verification_code = %s AND registration_status = 'pending'""", (verificationCode))
  return cursor.fetchone()
  
# Gets a user with the specified phone number.
def getUserFromPhoneNumber(phoneNumber):
  cursor = db.cursor()
  print phoneNumber
  cursor.execute("""SELECT * FROM user WHERE phone_number = %s""", (phoneNumber))
  return cursor.fetchone()
  
# Associates the specified user account with the phone number.
def registerUserWithPhoneNumber(userId, phoneNumber):
  cursor = db.cursor()
  cursor.execute("""UPDATE user SET phone_number = %s, registration_status = 'registered' WHERE id = %s""", \
    (phoneNumber, userId))
    
# Conversations:
def getMatchForUser(userId):
  cursor = db.cursor()
  cursor.execute("""SELECT * FROM user WHERE id NOT IN (SELECT user_one_id FROM conversation WHERE user_two_id = %s) \
    AND id NOT IN (SELECT user_two_id FROM conversation WHERE user_one_id = %s)""", (userId, userId))
  return cursor.fetchone()
  
# Inserts a new conversation with the two specified user id's.
def insertConversation(userOneId, userTwoId):
  cursor = db.cursor()