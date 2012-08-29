import argparse
import db
import facebook
import json
import random
import twilio.twiml

from constants import *
from flask import Flask, request, session
from strings import *
from twilioClient import TwilioClient, TwilioTestClient

app = Flask(__name__)
app.debug = True
app.secret_key = 'abcdefgh123456'

# Parse command line options
parser = argparse.ArgumentParser(description='Command line options for convos server.')
parser.add_argument('--debug', action="store_true", default=False, dest="debug")
args = parser.parse_args()

# Enable/disable texting.
if not args.debug:
  textingClient = TwilioClient()
else:
  textingClient = TwilioTestClient()

# Facebook configuration.
if not args.debug:
  facebookAppId = DEBUG_FACEBOOK_ID
  facebookSecret = DEBUG_facebookSecret
else:
  facebookAppId = PROD_FACEBOOK_ID
  facebookSecret = PROD_facebookSecret

# Handles incoming text messages.
@app.route("/message", methods=['POST'])
def message():
  body = request.values.get("Body").strip()
  phoneNumber = request.values.get("From")

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
    if registerUser(body, phoneNumber):
      resp.sms(WELCOME_MESSAGE)
    else:
      resp.sms(INCORRECT_VERIFICATION_CODE_MESSAGE)
  else:
    resp.sms(UNKNOWN_MESSAGE)
  return str(resp)

# Gets the other user id from a conversation.
def getOtherUserId(conversation, user):
  return conversation["user_two_id"] if conversation["user_one_id"] == user["id"]  \
    else conversation["user_one_id"]

# Ends the specified conversation and gets a new match for the rejected partner.
def endConversationForUserAndGetNewMatchForPartner(user):
  conversation = db.getCurrentConversationForUser(user["id"])
  if conversation:
    oldMatchedUserId = getOtherUserId(conversation, user)
    db.endConversation(conversation["id"])
    
    oldMatchedUser = db.getUserFromId(oldMatchedUserId)
    oldMatchedPhoneNumber = oldMatchedUser["phone_number"]
  
    # Look for a new match for this user.
    newMatchForOldUser = db.getMatchForUser(oldMatchedUserId)
    
    # If we found a match, make a new conversation and text the user.
    if newMatchForOldUser:
      db.insertConversation(oldMatchedUserId, newMatchForOldUser["id"])
      
      # Update the old user.
      textingClient.sendMessage(oldMatchedPhoneNumber, PARTNER_ENDED_NEW_MATCH \
        % (newMatchForOldUser["gender"], newMatchForOldUser["name"]))
        
      # Update the old user's new match.
      textingClient.sendMessage(newMatchForOldUser["phone_number"], NEW_MATCH \
        % (oldMatchedUser["gender"], oldMatchedUser["name"]))
    else:
      textingClient.sendMessage(oldMatchedPhoneNumber, PARTNER_ENDED_FINDING_MATCH)  

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
      newMatchedUser = db.getMatchForUser(userId)
      if newMatchedUser:
        db.insertConversation(userId, newMatchedUser["id"])
        resp.sms(NEW_MATCH % (newMatchedUser["gender"], newMatchedUser["name"]))
        
        # Notify the matched user.
        textingClient.sendMessage(newMatchedUser["phone_number"], NEW_MATCH % (user["gender"], user["name"]))
      else:
        resp.sms(FINDING_MATCH)
        
    # Case: the user wants to pause service.
    elif instruction == "pause":
      # End active conversations for this user.
      endConversationForUserAndGetNewMatchForPartner(user)
      
      # Pause this user.
      db.pauseUser(userId)
      resp.sms(PAUSED)
    
    # Case: unknown instruction
    else:
      resp.sms(UNKNOWN_INSTRUCTION)

# Handle an incoming message. Route the message to the appropriate user.
def handleMessage(body, user, resp):
  if user:
    conversation = db.getCurrentConversationForUser(user["id"])
    if conversation:
      # Get the matched user.
      matchedUserId = getOtherUserId(conversation, user)
      matchedUser = db.getUserFromId(matchedUserId)
      matchedPhoneNumber = matchedUser["phone_number"]
      
      # Send the message via text.
      textingClient.sendMessage(matchedPhoneNumber, "Partner: " + body)
      
      # Log the message in our own database.
      db.insertMessageForConversation(conversation["id"], user["id"], body)

# Attempts to register an existing user with the specified verification code.
# Returns whether we were successful.
def registerUser(verificationCode, phoneNumber):
  # Check that there exists an unregistered user with that verification code.
  existingUser = db.getUserFromVerificationCode(verificationCode)
  if existingUser:
    db.registerUserWithPhoneNumber(existingUser["id"], phoneNumber)
    return True
  else:
    return False

@app.route("/login", methods=['POST'])
def login():
  user = facebook.get_user_from_cookie(request.cookies, facebookAppId, facebookSecret)
  
  # TODO: just check the user's session uid instead of going to Facebook every time.
  if user:
    graph = facebook.GraphAPI(user["access_token"])
    profile = graph.get_object("me")
    
    # Update the user's network and education data.
    networkAndEducationData = graph.fql("SELECT affiliations, education FROM user WHERE uid = me()")
    print networkAndEducationData
    
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
    
    # Set a session variable so we can keep track of this user.
    session["user_id"] = existingUser["id"]
  else:
    response = {"status": "error", "error": "Not yet logged in to Facebook."}
  return json.dumps(response)

@app.route("/registration_status", methods=['GET'])
def registrationStatus():
  if "user_id" in session:
    user = db.getUserFromId(session["user_id"])
    response = {"status": user["registration_status"]}
  else:
    response = {"status": "nonexistent"}
  return json.dumps(response)
  
if __name__ == "__main__":
  app.run(debug=True, port=10080)