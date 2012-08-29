import MySQLdb
import MySQLdb.cursors

DATABASE = "convos"
PASSWORD = "convos"

db = MySQLdb.connect(db=DATABASE, passwd=PASSWORD, cursorclass=MySQLdb.cursors.DictCursor)
cursor = db.cursor()

## Helper methods.
# Gets the value of a key for a dictionary if it exists, otherwise returns alt.
def getValueOrAlt(dict, key, alt):
  return dict[key] if key in dict else alt

# Gets the value of a dict if it exists, otherwise 'NULL'.
def getValueOrNull(dict, key):
  return getValueOrAlt(dict, key, "NULL")

# Turns facebook data into a convenient list.
def userDataListFromFacebookData(facebookData):
  if "location" in facebookData:
    location = facebookData["location"]
    facebookData["location_id"] = location["id"]
    facebookData["location_name"] = location["name"]
  
  return (getValueOrNull(facebookData, "name"), \
    getValueOrNull(facebookData, "first_name"), \
    getValueOrNull(facebookData, "last_name"), \
    getValueOrNull(facebookData, "email"), \
    getValueOrNull(facebookData, "locale"), \
    getValueOrNull(facebookData, "username"), \
    getValueOrNull(facebookData, "gender"), \
    getValueOrNull(facebookData, "id"), \
    getValueOrAlt(facebookData, "verified", 0),
    getValueOrNull(facebookData, "location_id"), \
    getValueOrNull(facebookData, "location_name"), \
    getValueOrNull(facebookData, "birthday"))
    
## Users:
# Generates a unique verification code.
def generateUniqueVerificationCode():
  cursor.execute("""SELECT verification_code FROM user WHERE registration_status = 'pending' ORDER BY verification_code DESC""")
  lastVerificationCode = cursor.fetchone()
  if lastVerificationCode:
    code = int(lastVerificationCode["verification_code"]) + 1
  else:
    code = 1000
  return code

# Inserts a new user with pending registration status and specified verification code into the table.
def insertUserFromFacebookData(facebookData, verificationCode):  
  # Insert a new user if one with the specified fb_uid does not already exist.
  cursor.execute("""INSERT INTO user (name, first_name, last_name, email, locale, username, gender, \
    fb_uid, fb_verified, location_id, location_name, birthday, registration_status, verification_code, paused) \
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)""", \
    userDataListFromFacebookData(facebookData) + ("pending", verificationCode))

# Updates Facebook data for the user with the specified user id.
def updateUserFromFacebookData(userId, facebookData):
  cursor.execute("""UPDATE user SET \
    name = %s, \
    first_name = %s, \
    last_name = %s, \
    email = %s, \
    locale = %s, \
    username = %s, \
    gender = %s, \
    fb_uid = %s, \
    fb_verified = %s, \
    location_id = %s, \
    location_name = %s, \
    birthday = %s \
    WHERE id = %s""", userDataListFromFacebookData(facebookData) + (userId,))

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

# Pausing/unpausing user.
def pauseUser(userId):
  cursor.execute("""UPDATE user SET paused = 1 WHERE id = %s""", (userId))

def unpauseUser(userId):
  cursor.execute("""UPDATE user SET paused = 0 WHERE id = %s""", (userId))

## Conversations:
def getMatchForUser(userId):
  # Get all users that haven't been matched with this user and aren't currently in 'in-progress' conversations.
  cursor.execute("""SELECT * FROM user WHERE id NOT IN (SELECT user_one_id FROM conversation WHERE user_two_id = %s OR in_progress = 1) \
    AND id NOT IN (SELECT user_two_id FROM conversation WHERE user_one_id = %s OR in_progress = 1) \
    AND registration_status = 'registered'
    AND id != %s
    AND paused = 0""", (userId, userId, userId))
  return cursor.fetchone()
  
# Inserts a new conversation with the two specified user id's.
def insertConversation(userOneId, userTwoId):
  cursor.execute("""INSERT INTO conversation (user_one_id, user_two_id, in_progress) VALUES (%s, %s, 1)""", \
    (userOneId, userTwoId))

# Gets the current in-progress conversation for the user.
def getCurrentConversationForUser(userId):
  cursor.execute("""SELECT * FROM conversation WHERE (user_one_id = %s OR user_two_id = %s) AND in_progress = 1""", (userId, userId))
  return cursor.fetchone()

# Ends any in-progress conversations for the user.
def endConversation(conversationId):
  cursor.execute("""UPDATE conversation SET in_progress = 0 WHERE id = %s""", (conversationId))
  
## Messages:
def insertMessageForConversation(conversationId, fromUserId, body):
  cursor.execute("""INSERT INTO message (conversation_id, from_user_id, body) VALUES (%s, %s, %s)""", (conversationId, fromUserId, body))