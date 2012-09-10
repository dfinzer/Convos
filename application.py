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

def getOtherUserTwilioNumberId(conversation, user):
  return conversation["user_two_twilio_number_id"] if conversation["user_one_id"] == user["id"] \
    else conversation["user_one_twilio_number_id"]

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

def getInterestedInStringFromFacebookData(facebookData):
  interestInString = ""
  if "meeting_sex" in facebookData:
    meetingSexArray = facebookData["meeting_sex"]
    if meetingSexArray:
      if "male" in meetingSexArray:
        interestInString += "M"
      if "female" in meetingSexArray:
        interestInString += "F"
      return interestInString
  return interestInString

# Ends the specified conversation and gets a new match for the rejected partner.
def endConversationForUserAndGetNewMatchForPartner(user, userTwilioNumber):
  conversation = db.getCurrentConversationForUser(user["id"], userTwilioNumber)
  if conversation:
    db.endConversation(conversation["id"])
    
    # Get a new match for the rejected user.
    oldMatchedUserId = getOtherUserId(conversation, user)
    oldMatchedUser = db.getUserFromId(oldMatchedUserId)
    oldMatchedUserTwilioNumberId = getOtherUserTwilioNumberId(conversation, user)
    oldMatchedUserTwilioNumber = db.getTwilioNumberFromId(oldMatchedUserTwilioNumberId)
    makeMatchAndNotify(oldMatchedUser, oldMatchedUserTwilioNumber, True)

# Makes a new match and notifies the users. Pass true for partnerEndedMatch
# if the user's partner ended the match.
def makeMatchAndNotify(user, userTwilioNumber, partnerEndedMatch, resp=None):
  userPhoneNumber = user["phone_number"]
  
  # Attempt to get a new match for the user.
  newMatchedUser = db.getMatchForUser(user)
  
  # Case: we found a new match.
  if newMatchedUser:
    # Get a twilio number for the match. If everything went well, this should exist.
    newMatchedUserTwilioNumber = db.getAvailableTwilioNumberForUser(newMatchedUser)
    
    # If we don't have an available twilio number for the matched user, something went wrong in the matching process.
    if not newMatchedUserTwilioNumber:
      app.logger.error("No matched twilio number for user with id %s, matched with %s" % (newMatchedUser["id"], user["id"]))
    
    db.insertConversation(user["id"], userTwilioNumber, newMatchedUser["id"], newMatchedUserTwilioNumber)
    newMatchedUserInterests = db.getUserInterests(newMatchedUser["id"])
    commonInterests = db.getCommonInterests(user["id"], newMatchedUser["id"])
    if partnerEndedMatch:
      textingClient.sendPartnerEndedNewMatchMessage(userPhoneNumber, userTwilioNumber, newMatchedUser, \
        newMatchedUserInterests, commonInterests)
    else:
      textingClient.sendNewMatchMessage(userPhoneNumber, userTwilioNumber, newMatchedUser, \
        newMatchedUserInterests, commonInterests, resp)
        
    # Notify the matched user.
    textingClient.sendNewMatchMessage(newMatchedUser["phone_number"], newMatchedUserTwilioNumber, user, \
      db.getUserInterests(user["id"]), commonInterests)
  else:
    if partnerEndedMatch:
      textingClient.sendPartnerEndedFindingMatchMessage(userPhoneNumber, userTwilioNumber)
    else:
      textingClient.sendFindingMatchMessage(userPhoneNumber, userTwilioNumber, resp)

# Handle an instruction from the user. Includes getting matches, stopping conversations, and verifying accounts.
def handleInstructionOrMessage(body, user, userTwilioNumber, phoneNumber, resp):  
  userId = user["id"]
  # Case: the user wants a new conversation.
  if body == "#new":
    # Unpause the user.
    db.unpauseUser(userId)
    
    conversation = db.getCurrentConversationForUser(user["id"], userTwilioNumber)
    if conversation:
      # Check if this user has an available twilio number.
      availableTwilioNumber = db.getAvailableTwilioNumberForUser(user)
      
      # If there's no available Twilio number, we need to find a new one.
      if not availableTwilioNumber:
        availableTwilioNumber = db.getNextAvailableTwilioNumberForUser(user)
      
      # If after everything we were able to find a twilio number, go ahead and make the match.
      if availableTwilioNumber:
        # Register the user with this twilio number if he isn't already registered.
        db.addTwilioNumberForUserIfNonexistent(user, availableTwilioNumber)
        
        makeMatchAndNotify(user, availableTwilioNumber, False, None)
      # Otherwise notify the user that there aren't any available twilio numbers, (max conversations.)
      else:
        textingClient.sendMaxConversationsMessage(phoneNumber, userTwilioNumber, resp)
    # If there's no current conversation, just make a match with this twilioNumber.
    else:
      makeMatchAndNotify(user, userTwilioNumber, False, resp)
    
  # Case: the user wants to end the current conversation on this number.
  elif body == "#end":
    # If the user is currently in a conversation, end it.
    endConversationForUserAndGetNewMatchForPartner(user, userTwilioNumber)
    
    # Get a new match for the user.
    makeMatchAndNotify(user, userTwilioNumber, False, resp)
    
  # Case: the user wants to pause service.
  elif body == "#pause":
    # End all active conversations for this user; that means we need to go through all of the user's twilio numbers
    # and pause and active conversations.
    for twilioNumber in db.getTwilioNumbersForUser(user):
      endConversationForUserAndGetNewMatchForPartner(user, twilioNumber)
    
    # Pause this user.
    db.pauseUser(userId)
    textingClient.sendPauseMessage(phoneNumber, userTwilioNumber, resp)
  
  # Case: the user wants help options.
  elif body == "#help":
    textingClient.sendHelpMessage(phoneNumber, userTwilioNumber, resp)
    
  # Case: message.
  else:
    handleMessage(body, user, userTwilioNumber, resp)

# Handle an incoming message. Route the message to the appropriate user.
def handleMessage(body, user, userTwilioNumber, resp):
  conversation = db.getCurrentConversationForUser(user["id"], userTwilioNumber)
  if conversation:
    # Get the matched user.
    matchedUserId = getOtherUserId(conversation, user)
    matchedUserTwilioNumberId = getOtherUserTwilioNumberId(conversation, user)
    matchedUser = db.getUserFromId(matchedUserId)
    matchedUserTwilioNumber = db.getTwilioNumberFromId(matchedUserTwilioNumberId)
    matchedPhoneNumber = matchedUser["phone_number"]
    
    # Send the message via text.
    textingClient.sendPartnerMessage(matchedPhoneNumber, matchedUserTwilioNumber, body)
    
    # Log the message in our own database.
    db.insertMessageForConversation(conversation["id"], user["id"], body)
  else:
    if db.userIsPaused(user["id"]):
      textingClient.sendNoConversationUnpauseMessage(user["phone_number"], userTwilioNumber)
    else:
      textingClient.sendNoConversationMessage(user["phone_number"], userTwilioNumber)

# Handles incoming text messages.
@app.route("/api/message", methods=['POST'])
def message():
  db.openConnection()

  phoneNumber = request.values.get("From")
  twilioNumber = db.getTwilioNumberFromNumber(request.values.get("To"))
  
  # Check that we have a twilio number.
  if not twilioNumber:
    return json.dumps({"status": "error", "error": "Convos doesn't recognize this twilio number."})
  
  body = request.values.get("Body").strip()

  # Log the message.
  db.logMessage(phoneNumber, twilioNumber, body, False)

  # Check if a user for this phone number exists in the database.
  user = db.getUserFromPhoneNumber(phoneNumber)

  # Initialize an appropriate twilio response.
  resp = twilio.twiml.Response()

  # Check if this is an instruction.
  if user:
    # Register the user with this twilio user if he's not already registered (no matter what he sent.)
    db.addTwilioNumberForUserIfNonexistent(user, twilioNumber)
    
    handleInstructionOrMessage(body, user, twilioNumber, phoneNumber, resp)
  # Otherwise the user is coming from mobile.
  elif body == "#signup" or body == "signup":
    # Create a new user, with registration status pending.
    verificationCode = str(db.generateUniqueVerificationCode())
    db.insertUserFromPhoneData(phoneNumber, verificationCode)
    
    # Send the user a signup url.
    textingClient.sendSignupUrl(phoneNumber, twilioNumber, verificationCode, resp)
  else:
    textingClient.sendUnknownMessage(phoneNumber, twilioNumber, resp)

  db.closeConnection()
  return str(resp)

@app.route("/api/login", methods=['POST'])
def login():
  db.openConnection()

  # Get the user and url code (if it exists).
  user = facebook.get_user_from_cookie(request.cookies, facebookAppId, facebookSecret)
  urlCode = request.values.get("code")  
  
  if user:
    graph = facebook.GraphAPI(user["access_token"])
    profile = graph.get_object("me")
        
    # Get the user's education, interest, and interested_in data.
    facebookData = graph.fql("SELECT " + ",".join(FACEBOOK_INTERESTS) + ", education, meeting_sex FROM user WHERE uid = me()")
    interestedInString = getInterestedInStringFromFacebookData(facebookData[0])
    if interestedInString:
      profile["interested_in"] = interestedInString
    
    collegeString = findMostRecentCollegeFromFacebookData(facebookData[0])
    if collegeString:
      profile["college"] = collegeString
    
    # Now begin searching for this user based on the available data (facebook data, verification code).
    foundUser = False
    
    # Check if this user already exists in the database.
    existingUser = db.getUserFromFacebookUid(user["uid"])
    if existingUser:
      # If the user hasn't registered yet, send back the verification code.
      if existingUser["registration_status"] == "pending":
        response = {"status": "pending"}
      else:
        response = {"status": "registered"}
      
      # Update the user with his Facebook data.
      db.updateUserFromFacebookData(existingUser["id"], profile)
      foundUser = True      
    # If there's a new url code, see if there's a user in the database for this code.
    elif urlCode:      
      # Check for an existing unregistered user.
      existingUser = db.getUnregisteredUserFromVerificationCode(urlCode)
      
      # If everything went well, we can update the user's Facebook data and register him.
      if existingUser:
        db.updateUserFromFacebookData(existingUser["id"], profile)
        twilioNumber = db.getNextAvailableTwilioNumberForUser(existingUser)
        
        # Register the user.
        db.registerUserWithPhoneNumber(existingUser["id"], existingUser["phone_number"], twilioNumber)
        
        # Send the user a welcome message.
        textingClient.sendWelcomeMessage(existingUser["phone_number"], twilioNumber)
        
        response = {"status": "registered"}
        foundUser = True

    # If we didn't find a user via the Facebook data or the urlCode, we need to make a new one.
    if not foundUser:
      # Create a new user, with registration status pending.
      db.insertUserFromFacebookData(profile)
      response = {"status": "pending"}
      existingUser = db.getUserFromFacebookUid(user["uid"])
    
    # Record the user interests in the database.
    try:
      interests = interestArrayFromFacebookLikeData(facebookData[0])
      db.setUserInterests(existingUser["id"], interests)
    # If anything goes wrong, we still want to continue, but we'll log an error.
    except Exception as e:
      app.logger.error(e)
    
    # Set a session variable so we can keep track of this user.
    session["user_id"] = existingUser["id"]
  else:
    response = {"status": "error", "error": "Not yet logged in to Facebook."}
  db.closeConnection()
  return json.dumps(response)

@app.route("/api/register_phone_number", methods=['POST'])
def registerPhoneNumber():
  db.openConnection()
  phoneNumber = request.values.get("phone_number")
  if not phoneNumber.startswith("+1") or not phoneNumber[2:].isdigit():
    app.logger.error("Invalid phone number %s" % phoneNumber);
    response = {"status": "error", "error": "Invalid phone number."}
  elif "user_id" in session:
    twilioNumber = db.getFirstTwilioNumber()
    db.registerUserWithPhoneNumber(session["user_id"], phoneNumber, twilioNumber)
    user = db.getUserFromId(session["user_id"])
    
    # Send the user a welcome message.
    textingClient.sendWelcomeMessage(user["phone_number"], twilioNumber)
    
    # Match the user.
    makeMatchAndNotify(user, twilioNumber, False)
    response = {"status": "registered"}
  else:
    response = {"status": "error", "error": "No user found."}
  return json.dumps(response)
  
@app.route("/api/end_conversation", methods=['POST'])
def endConversation():
  db.openConnection()
  userId = request.values.get("user_id")
  userTwilioNumberId = request.values.get("user_twilio_number_id")
  user = db.getUserFromId(userId)
  userTwilioNumber = db.getTwilioNumberFromId(userTwilioNumberId)
  
  # If the user is currently in a conversation, end it.
  endConversationForUserAndGetNewMatchForPartner(user, userTwilioNumber)
  
  # Get a new match for the user.
  makeMatchAndNotify(user, userTwilioNumber, True)
  db.closeConnection()
  return genericResponse()

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

## Admin urls.
# Gets all the SMS sent for a particular phone number and twilio number combo.
@app.route("/api/admin/get_messages", methods=["GET"])
def getMessages():
  db.openConnection()
  if "user_id" in session:
    user = db.getUserFromId(session["user_id"])
    if user["name"] != "Devin Finzer":
      return "Unauthorized."
  else:
    return "Need to log in."
  phoneNumber = request.values.get("phone_number")
  twilioNumber = db.getTwilioNumberFromNumber(request.values.get("twilio_number"))
  messages = db.getMessagesForPhoneNumberAndTwilioNumber(phoneNumber, twilioNumber)
  db.closeConnection()
  return json.dumps(messages)

if __name__ == "__main__":
  app.run(debug=True, port=10080)