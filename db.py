import MySQLdb
import MySQLdb.cursors

DATABASE = "convos"
PASSWORD = "convos"

db = MySQLdb.connect(db=DATABASE, passwd=PASSWORD, cursorclass=MySQLdb.cursors.DictCursor)
cursor = db.cursor()

# Gets the value of a key for a dictionary if it exists, otherwise returns NULL.
def getValueOrNull(dict, key):
  return dict[key] if key in dict else "NULL"

## Users:
# Inserts a new user with pending registration status and specified verification code into the table.
def insertUserFromFacebookData(facebookData, verificationCode):  
  # TODO: check if the necessary user data is actually there.
  # Insert a new user if one with the specified fb_uid does not already exist.
  cursor.execute("""INSERT INTO user (name, first_name, last_name, email, locale, username, gender, \
    fb_uid, fb_verified, registration_status, verification_code) \
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", \
    (getValueOrNull(facebookData, "name"), \
    getValueOrNull(facebookData, "first_name"), \
    getValueOrNull(facebookData, "last_name"), \
    getValueOrNull(facebookData, "email"), \
    getValueOrNull(facebookData, "locale"), \
    getValueOrNull(facebookData, "username"), \
    getValueOrNull(facebookData, "gender"), \
    getValueOrNull(facebookData, "id"), \
    getValueOrNull(facebookData, "verified"), \
    "pending", \
    verificationCode))
  db.commit()

def getUserFromId(userId):
  cursor.execute("""SELECT * FROM user WHERE id = %s""", (userId))
  return cursor.fetchone()

# Gets a user with the specified Facebook uid.
def getUserFromFacebookUid(facebookUid):
  cursor.execute("""SELECT * FROM user WHERE fb_uid = %s""", (facebookUid))
  return cursor.fetchone()
  
# Gets a user with the specified verification code (assumes this user is pending registration).
def getUserFromVerificationCode(verificationCode):
  cursor.execute("""SELECT * FROM user WHERE verification_code = %s AND registration_status = 'pending'""", (verificationCode))
  return cursor.fetchone()
  
# Gets a user with the specified phone number.
def getUserFromPhoneNumber(phoneNumber):
  cursor.execute("""SELECT * FROM user WHERE phone_number = %s""", (phoneNumber))
  return cursor.fetchone()
  
# Associates the specified user account with the phone number.
def registerUserWithPhoneNumber(userId, phoneNumber):
  cursor.execute("""UPDATE user SET phone_number = %s, registration_status = 'registered' WHERE id = %s""", \
    (phoneNumber, userId))
      
## Conversations:
def getMatchForUser(userId):
  # Get all users that haven't been matched with this user and aren't currently in 'in-progress' conversations.
  cursor.execute("""SELECT * FROM user WHERE id NOT IN (SELECT user_one_id FROM conversation WHERE user_two_id = %s OR in_progress = True) \
    AND id NOT IN (SELECT user_two_id FROM conversation WHERE user_one_id = %s OR in_progress = True) \
    AND registration_status = 'registered'
    AND id != %s""", (userId, userId, userId))
  return cursor.fetchone()
  
# Inserts a new conversation with the two specified user id's.
def insertConversation(userOneId, userTwoId):
  cursor.execute("""INSERT INTO conversation (user_one_id, user_two_id, in_progress) VALUES (%s, %s, True)""", \
    (userOneId, userTwoId))

# Gets the current in-progress conversation for the user.
def getCurrentConversationForUser(userId):
  cursor.execute("""SELECT * FROM conversation WHERE (user_one_id = %s OR user_two_id = %s) AND in_progress = True""", (userId, userId))
  return cursor.fetchone()

# Ends any in-progress conversations for the user.
def endCurrentConversationForUser(userId):
  cursor.execute("""UPDATE conversation SET in_progress = False WHERE user_one_id = %s OR user_two_id = %s \
    AND in_progress = True""", (userId, userId))
  
## Messages:
def insertMessageForConversation(conversationId, fromUserId, body):
  cursor.execute("""INSERT INTO message (conversation_id, from_user_id, body) VALUES (%s, %s, %s)""", (conversationId, fromUserId, body))
  