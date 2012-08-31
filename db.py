import MySQLdb
import MySQLdb.cursors

DATABASE = "convos"
PASSWORD = "convos"

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
    getValueOrNull(facebookData, "birthday"), \
    getValueOrNull(facebookData, "college"))
    
class Database():
  ## Connections.
  def openConnection(self):
    self.db = MySQLdb.connect(db=DATABASE, passwd=PASSWORD, cursorclass=MySQLdb.cursors.DictCursor)

  def closeConnection(self):
    self.db.close()

  ## Users:
  # Generates a unique verification code.
  def generateUniqueVerificationCode(self):
    cursor = self.db.cursor()
    cursor.execute("""SELECT verification_code FROM user WHERE registration_status = 'pending' ORDER BY verification_code DESC""")
    lastVerificationCode = cursor.fetchone()
    if lastVerificationCode:
      code = int(lastVerificationCode["verification_code"]) + 1
    else:
      code = 1000
    return code

  # Inserts a new user with pending registration status and specified verification code into the table.
  def insertUserFromFacebookData(self, facebookData, verificationCode):
    cursor = self.db.cursor()
  
    # Insert a new user if one with the specified fb_uid does not already exist.
    cursor.execute("""INSERT INTO user (name, first_name, last_name, email, locale, username, gender, \
      fb_uid, fb_verified, location_id, location_name, birthday, college, registration_status, verification_code, paused) \
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)""", \
      userDataListFromFacebookData(facebookData) + ("pending", verificationCode))
    cursor.close()

  # Updates Facebook data for the user with the specified user id.
  def updateUserFromFacebookData(self, userId, facebookData):
    cursor = self.db.cursor()
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
      birthday = %s, \
      college = %s \
      WHERE id = %s""", userDataListFromFacebookData(facebookData) + (userId,))
    cursor.close()

  def getUserFromId(self, userId):
    cursor = self.db.cursor()
    cursor.execute("""SELECT * FROM user WHERE id = %s""", (userId))
    return cursor.fetchone()

  # Gets a user with the specified Facebook uid.
  def getUserFromFacebookUid(self, facebookUid):
    cursor = self.db.cursor()
    cursor.execute("""SELECT * FROM user WHERE fb_uid = %s""", (facebookUid))
    return cursor.fetchone()
  
  # Gets a user with the specified verification code (assumes this user is pending registration).
  def getUserFromVerificationCode(self, verificationCode):
    cursor = self.db.cursor()
    cursor.execute("""SELECT * FROM user WHERE verification_code = %s AND registration_status = 'pending'""", (verificationCode))
    return cursor.fetchone()
  
  # Gets a user with the specified phone number.
  def getUserFromPhoneNumber(self, phoneNumber):
    cursor = self.db.cursor()
    cursor.execute("""SELECT * FROM user WHERE phone_number = %s""", (phoneNumber))
    return cursor.fetchone()
  
  # Associates the specified user account with the phone number.
  def registerUserWithPhoneNumber(self, userId, phoneNumber):
    cursor = self.db.cursor()
    cursor.execute("""UPDATE user SET phone_number = %s, registration_status = 'registered' WHERE id = %s""", \
      (phoneNumber, userId))
    cursor.close()

  # Pausing/unpausing user.
  def pauseUser(self, userId):
    cursor = self.db.cursor()
    cursor.execute("""UPDATE user SET paused = 1 WHERE id = %s""", (userId))
    cursor.close()

  def unpauseUser(self, userId):
    cursor = self.db.cursor()
    cursor.execute("""UPDATE user SET paused = 0 WHERE id = %s""", (userId))
    cursor.close()

  def userIsPaused(self, userId):
    cursor = self.db.cursor()
    cursor.execute("""SELECT paused FROM user WHERE id = %s""", (userId))
    return cursor.fetchone()["paused"]

  ## Interests:
  def insertInterestsIfNonexistent(self, interests):
    cursor = self.db.cursor()
    cursor.executemany("""INSERT IGNORE INTO interest (name) VALUES (%s)""", map(lambda i : (i), interests))
    cursor.close()
  
  def setUserInterests(self, userId, interests):
    cursor = self.db.cursor()
    if len(interests) > 0:
      self.insertInterestsIfNonexistent(interests)
    
      # TODO: this is a major hack, we shouldn't be appending raw strings.
      formatStrings = ["%s"] * len(interests)
      interestInFormatString = "(" + ",".join(formatStrings) + ")"
      cursor.execute("""INSERT IGNORE INTO user_interest (user_id, interest_id) SELECT user.id, interest.id \
        FROM user, interest WHERE user.id = %s AND interest.name IN """ + interestInFormatString, (userId,) + tuple(interests))

  def interestResultToList(self, interestResult):
    return map(lambda i : i["name"], interestResult)

  def getUserInterests(self, userId):
    cursor = self.db.cursor()
    cursor.execute("""SELECT interest.name FROM user_interest, interest \
      WHERE user_interest.user_id = %s AND interest.id = user_interest.interest_id""", (userId))
    interests = self.interestResultToList(cursor.fetchall())
    return interests

  def getCommonInterests(self, userOneId, userTwoId):
    cursor = self.db.cursor()
    cursor.execute("""SELECT interest.name FROM user_interest, interest \
      WHERE user_interest.user_id = %s AND interest.id = user_interest.interest_id
      AND interest.id IN (SELECT interest_id FROM user_interest WHERE user_id = %s)""",
      (userOneId, userTwoId))
    interests = self.interestResultToList(cursor.fetchall())
    return interests

  ## Conversations:
  # TODO: combine this method into one query.
  def getMatchForUser(self, userId):
    cursor = self.db.cursor()
    # First get users with shared interests
    cursor.execute("""CREATE TEMPORARY TABLE shared_interest_users \
      SELECT COUNT(*) AS count, user_id FROM user_interest LEFT JOIN user \
      ON user.id = user_interest.user_id WHERE interest_id IN (SELECT interest.id FROM user_interest, \
      interest WHERE user_interest.user_id = %s AND user_interest.interest_id = interest.id) GROUP BY user_id \
      ORDER BY count;""", (userId));
  
    # Get all users that haven't been matched with this user and aren't currently in 'in-progress' conversations.
    cursor.execute("""SELECT user.*, shared_interest_users.count FROM user \
      LEFT JOIN shared_interest_users ON shared_interest_users.user_id = user.id
      WHERE id NOT IN (SELECT user_one_id FROM conversation WHERE user_two_id = %s OR in_progress = 1) \
      AND id NOT IN (SELECT user_two_id FROM conversation WHERE user_one_id = %s OR in_progress = 1) \
      AND registration_status = 'registered' \
      AND id != %s \
      AND paused = 0 \
      ORDER BY shared_interest_users.count DESC; DROP TABLE shared_interest_users;""", (userId, userId, userId))
    match = cursor.fetchone()
    cursor.close()
    return match
  
  # Inserts a new conversation with the two specified user id's.
  def insertConversation(self, userOneId, userTwoId):
    cursor = self.db.cursor()
    cursor.execute("""INSERT INTO conversation (user_one_id, user_two_id, in_progress) VALUES (%s, %s, 1)""", \
      (userOneId, userTwoId))
    cursor.close()

  # Gets the current in-progress conversation for the user.
  def getCurrentConversationForUser(self, userId):
    cursor = self.db.cursor()
    cursor.execute("""SELECT * FROM conversation WHERE (user_one_id = %s OR user_two_id = %s) AND in_progress = 1""", (userId, userId))
    return cursor.fetchone()

  # Ends any in-progress conversations for the user.
  def endConversation(self, conversationId):
    cursor = self.db.cursor()
    cursor.execute("""UPDATE conversation SET in_progress = 0 WHERE id = %s""", (conversationId))
    cursor.close()
  
  ## Messages:
  def insertMessageForConversation(self, conversationId, fromUserId, body):
    cursor = self.db.cursor()
    cursor.execute("""INSERT INTO message (conversation_id, from_user_id, body) VALUES (%s, %s, %s)""", (conversationId, fromUserId, body))
    cursor.close()
  
  ## Logging:
  def logMessage(self, phoneNumber, body, outbound):
    cursor = self.db.cursor()
    cursor.execute("""INSERT INTO sms_log (phone_number, body, outbound) VALUES (%s, %s, %s)""", (phoneNumber, body, outbound))
    cursor.close()
    
  def logClickedFacebookLogin(self, data):
    cursor = self.db.cursor()
    cursor.execute("""INSERT INTO clicked_facebook_login_log (ip, user_agent) VALUES (%s, %s)""", \
      (data["ip"], data["user_agent"]));
    cursor.close()
    
  def logVisitedPage(self, data):
    cursor = self.db.cursor()
    cursor.execute("""INSERT INTO visited_page_log (ip, user_agent, name) VALUES (%s, %s, %s)""", \
      (data["ip"], data["user_agent"], data["name"]));
    cursor.close()