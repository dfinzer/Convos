import argparse
import facebook
import json
import random
import twilio.twiml

from constants import *
from db import Database
from flask import Flask, request, session
from strings import *
from twilioClient import TwilioClient, TwilioTestClient

app = Flask(__name__)
app.secret_key = 'abcdefgh123456'

# Parse command line options
parser = argparse.ArgumentParser(description='Command line options for convos server.')
parser.add_argument('--debug', action="store_true", default=False, dest="debug")
args = parser.parse_args()
db = Database()

# Development configuration.
if args.debug:
  textingClient = TwilioTestClient(db)
  facebookAppId = PROD_FACEBOOK_ID
  facebookSecret = PROD_FACEBOOK_SECRET
# Prod configuration.
else:
  textingClient = TwilioClient(db)
  facebookAppId = DEBUG_FACEBOOK_ID
  facebookSecret = DEBUG_FACEBOOK_SECRET

  # Set up logging.
  import logging
  from logging.handlers import SMTPHandler
  
  fileHandler = logging.FileHandler('/var/tmp/convos.log')
  fileHandler.setLevel(logging.WARNING)
  app.logger.addHandler(fileHandler)
  
  # Set up email.
  from smtp import TlsSMTPHandler
  ADMINS = ['dfinzer2@gmail.com']
  mail_handler = TlsSMTPHandler(('email-smtp.us-east-1.amazonaws.com', 25), 'dfinzer2@gmail.com', \
    ADMINS, 'Convos Failed', credentials=('AKIAJVZYBPD2LLMWMDAA', 'Alwl4cvm2242mRq5r9h/2PgAfZ8FHJLTeAqTBO+R8CZP'))
  mail_handler.setLevel(logging.WARNING)
  app.logger.addHandler(mail_handler)

# Gets the other user id from a conversation.
def getOtherUserId(conversation, user):
  return conversation["user_two_id"] if conversation["user_one_id"] == user["id"]  \
    else conversation["user_one_id"]

# Generates an array of interests (strings) from a more complex array of Facebook data.
def interestArrayFromFacebookLikeData(facebookLikeData):
  interests = []
  for facebookInterest in FACEBOOK_INTERESTS:
    if facebookInterest in facebookLikeData:
      facebookLike = facebookLikeData[facebookInterest]
      if type(facebookLike) is unicode and len(facebookLike) > 0:
        interests += (facebookLike.split(", "))
      elif type(facebookLike) is list and len(facebookLike) > 0:
        likeNameList = []
        for like in facebookLike:
          if "name" in like:
            likeNameList.append(like["name"])
        interests += likeNameList
  return interests

def findMostRecentCollegeFromFacebookData(facebookData):
  maxYear = 0
  maxCollege = None
  college = None
  for education in facebookData["education"]:
    if "school" in education and "name" in education["school"] and "type" in education and education["type"] == "College":
      if "year" in education:
        year = education["year"]
        # Go for the most recent year.
        if "name" in year and year["name"].isdigit():
          currentYear = int(year["name"])
          if currentYear > maxYear:
            maxYear = currentYear
            maxCollege = education["school"]["name"]
      else:
        if not maxCollege:
          maxCollege = education["school"]["name"]
  if maxCollege:
    return maxCollege + ", " + str(maxYear) if maxYear != 0 else maxCollege
  return None

# Ends the specified conversation and gets a new match for the rejected partner.
def endConversationForUserAndGetNewMatchForPartner(user):
  conversation = db.getCurrentConversationForUser(user["id"])
  if conversation:
    oldMatchedUserId = getOtherUserId(conversation, user)
    db.endConversation(conversation["id"])
    
    # Get a new match for the rejected user.
    oldMatchedUser = db.getUserFromId(oldMatchedUserId)
    makeMatchAndNotify(oldMatchedUser, True)

# Makes a new match and notifies the users. Pass true for partnerEndedMatch
# if the user's partner ended the match.
def makeMatchAndNotify(user, partnerEndedMatch, resp=None):
  userPhoneNumber = user["phone_number"]
  
  # Attempt to get a new match for the user.
  newMatchedUser = db.getMatchForUser(user["id"])
  
  # Case: we found a new match.
  if newMatchedUser:
    db.insertConversation(user["id"], newMatchedUser["id"])
    newMatchedUserInterests = db.getUserInterests(newMatchedUser["id"])
    commonInterests = db.getCommonInterests(user["id"], newMatchedUser["id"])
    if partnerEndedMatch:
      textingClient.sendPartnerEndedNewMatchMessage(userPhoneNumber, newMatchedUser, \
        newMatchedUserInterests, commonInterests)
    else:
      textingClient.sendNewMatchMessage(userPhoneNumber, newMatchedUser, \
        newMatchedUserInterests, commonInterests, resp)
        
    # Notify the matched user.
    textingClient.sendNewMatchMessage(newMatchedUser["phone_number"], user, db.getUserInterests(user["id"]), commonInterests)
  else:
    if partnerEndedMatch:
      textingClient.sendPartnerEndedFindingMatchMessage(userPhoneNumber)
    else:
      textingClient.sendFindingMatchMessage(userPhoneNumber, resp)

# Handle an instruction from the user. Includes getting matches, stopping conversations, and verifying accounts.
def handleInstruction(instruction, user, phoneNumber, resp):  
  # If there's a user, handle the instruction.
  if user:
    userId = user["id"]
    # Case: the user wants a new conversation.
    if instruction == "new":
      # Unpause the user.
      db.unpauseUser(userId)
      
      # If the user is currently in a conversation, end it.
      endConversationForUserAndGetNewMatchForPartner(user)

      # Get a new match for the user.
      makeMatchAndNotify(user, False, resp)
      
    # Case: the user wants to pause service.
    elif instruction == "pause":
      # End active conversations for this user.
      endConversationForUserAndGetNewMatchForPartner(user)
      
      # Pause this user.
      db.pauseUser(userId)
      textingClient.sendPauseMessage(phoneNumber, resp)
    
    # Case: unknown instruction
    else:
      textingClient.sendUnknownInstructionMessage(phoneNumber, resp)

# Handle an incoming message. Route the message to the appropriate user.
def handleMessage(body, user, resp):
  conversation = db.getCurrentConversationForUser(user["id"])
  if conversation:
    # Get the matched user.
    matchedUserId = getOtherUserId(conversation, user)
    matchedUser = db.getUserFromId(matchedUserId)
    matchedPhoneNumber = matchedUser["phone_number"]
    
    # Send the message via text.
    textingClient.sendPartnerMessage(matchedPhoneNumber, body)
    
    # Log the message in our own database.
    db.insertMessageForConversation(conversation["id"], user["id"], body)
  else:
    if db.userIsPaused(user["id"]):
      textingClient.sendNoConversationUnpauseMessage(user["phone_number"])
    else:
      textingClient.sendNoConversationMessage(user["phone_number"])

# Attempts to register an existing user with the specified verification code.
# Returns whether we were successful.
def registerUser(verificationCode, phoneNumber, twilioNumber):
  # Check that there exists an unregistered user with that verification code.
  existingUser = db.getUserFromVerificationCode(verificationCode)
  if existingUser:
    db.registerUserWithPhoneNumber(existingUser["id"], phoneNumber, twilioNumber)
    return True
  else:
    return False

# Handles incoming text messages.
@app.route("/api/message", methods=['POST'])
def message():
  db.openConnection()

  phoneNumber = request.values.get("From")
  twilioNumber = request.values.get("To")
  body = request.values.get("Body").strip()

  # Log the message.
  db.logMessage(phoneNumber, body, False)

  # Check if a user for this phone number exists in the database.
  user = db.getUserFromPhoneNumber(phoneNumber)

  # Initialize an appropriate twilio response.
  resp = twilio.twiml.Response()

  # Check if this is an instruction.
  if user:
    if body.startswith("#"):
      handleInstruction(body[1:], user, phoneNumber, resp)
    # Otherwise, we need to route this message.
    else:
      handleMessage(body, user, resp)
  # If there's no user and the instruction is a digit, it's a verification code. So try to register the user.
  elif body.isdigit():
    if registerUser(body, phoneNumber, twilioNumber):
      textingClient.sendWelcomeMessage(phoneNumber, resp)
    else:
      textingClient.sendIncorrectVerificationCodeMessage(phoneNumber, resp)
  else:
    textingClient.sendUnknownMessage(phoneNumber, resp)

  db.closeConnection()
  return str(resp)

@app.route("/api/login", methods=['POST'])
def login():
  db.openConnection()
  
  user = facebook.get_user_from_cookie(request.cookies, facebookAppId, facebookSecret)
  
  # TODO: just check the user's session uid instead of going to Facebook every time.
  if user:
    graph = facebook.GraphAPI(user["access_token"])
    profile = graph.get_object("me")
    
    # Update the user's network and education data.
    facebookData = graph.fql("SELECT " + ",".join(FACEBOOK_INTERESTS) + ", education FROM user WHERE uid = me()")
    collegeString = findMostRecentCollegeFromFacebookData(facebookData[0])
    if collegeString:
      profile["college"] = collegeString
    
    # Check if this user already exists in the database.
    existingUser = db.getUserFromFacebookUid(user["uid"])
    if existingUser:
      # If the user hasn't registered yet, send back the verification code.
      if existingUser["registration_status"] == "pending":
        response = {"status": "pending", "verification_code": existingUser["verification_code"]}
      else:
        response = {"status": "registered"}
      
      # Update the user with his Facebook data.
      db.updateUserFromFacebookData(existingUser["id"], profile)
    else:
      # Create a new user, with registration status pending.
      verificationCode = str(db.generateUniqueVerificationCode())
      db.insertUserFromFacebookData(profile, verificationCode)
      response = {"status": "pending", "verification_code": verificationCode}
      existingUser = db.getUserFromFacebookUid(user["uid"])
    
    # Record the user interests in the database.
    interests = interestArrayFromFacebookLikeData(facebookData[0])
    db.setUserInterests(existingUser["id"], interests)
    
    # Set a session variable so we can keep track of this user.
    session["user_id"] = existingUser["id"]
  else:
    response = {"status": "error", "error": "Not yet logged in to Facebook."}
  db.closeConnection()
  return json.dumps(response)

@app.route("/api/registration_status", methods=['GET'])
def registrationStatus():
  db.openConnection()
  if "user_id" in session:
    user = db.getUserFromId(session["user_id"])
    response = {"status": user["registration_status"]}
  else:
    response = {"status": "nonexistent"}
  db.closeConnection()
  return json.dumps(response)
  
## Metrics
def genericResponse():
  return json.dumps({"status": "ok"})

def getRequestData():
  data = {"ip": request.remote_addr, "user_agent": request.headers["User-Agent"]}
  if "user_id" in session:
    data["user_id"] = session["user_id"]
  return data

# Log when the user clicks the Facebook login button.
@app.route("/api/log_clicked_facebook_login", methods=["POST"])
def logClickedFacebookLogin():
  data = getRequestData()
  db.openConnection()
  db.logClickedFacebookLogin(data)
  db.closeConnection()
  return genericResponse()

# Log when someone goes to index.html.
@app.route("/api/log_visited_page", methods=["POST"])
def logVisitedPage():
  data = getRequestData()
  data["name"] = request.values.get("name")

  db.openConnection()
  db.logVisitedPage(data)
  db.closeConnection()
  return genericResponse()
  
## Feedback/bug reports.
def getTextAndData():
  data = getRequestData()
  data["form_text"] = request.values.get("form_text")
  return data
  
@app.route("/api/feedback", methods=["POST"])
def feedback():
  db.openConnection()
  data = getTextAndData()
  db.insertFeedback(data)
  db.closeConnection()
  return genericResponse()
  
@app.route("/api/bug_report", methods=["POST"])
def bugReport():
  data = getTextAndData()
  db.openConnection()
  db.insertBugReport(data)
  db.closeConnection()
  return genericResponse()

if __name__ == "__main__":
  app.run(debug=True, port=10080)