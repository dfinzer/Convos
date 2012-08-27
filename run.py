import argparse
import db
import facebook
import json
import random
import twilio.twiml

from flask import Flask
from flask import request
from twilioClient import TwilioClient, TwilioTestClient

app = Flask(__name__)

# Parse command line options
parser = argparse.ArgumentParser(description='Command line options for convos server.')
parser.add_argument('--texting', action="store_true", default=False, dest="texting")
args = parser.parse_args()

# Enable/disable texting.
if args.texting:
  textingClient = TwilioClient()
else:
  textingClient = TwilioTestClient()

# Facebook configuration.
facebook_app_id = '326547147430900'
facebook_secret = 'd0347b67f972d8c3c751c7a29ee55b5d'

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
  if body.startswith("#"):
    handleInstruction(body[1:], user, phoneNumber, resp)
  # Otherwise, we need to route this message.
  else:
    handleMessage(body, user, resp)
  return str(resp)

# Gets the other user id from a conversation.
def getOtherUserId(conversation, user):
  return conversation["user_two_id"] if conversation["user_one_id"] == user["id"]  \
    else conversation["user_two_id"]

# Handle an instruction from the user. Includes getting matches, stopping conversations, and verifying accounts.
def handleInstruction(instruction, user, phoneNumber, resp):  
  # If there's a user, handle the instruction.
  if user:
    userId = user["id"]
    # Case: the user wants a new conversation.
    if instruction == "new":
      # If the user is currently in a conversation, end it.
      db.getCurrentConversationForUser(user["id"])
      if conversation:
        matchedUserId = getOtherUserId(conversation, user)
        db.endConversation(conversation["id"])
        
        # Notify the other user that the conversation has ended.
        oldMatchedUser = db.getUserFromId(matchedUserId)
        oldMatchedPhoneNumber = matchedUser["phone_number"]
      
        # Look for a new match for this user.
        newMatchForOldUser = db.getMatchForUser(userId)
        
        if newMatchForOldUser:
          textingClient.sendMessage(matchedPhoneNumber, "Your current partner ended the conversation. We've matched you up with a new partner: %s %s" \
            % (newMatchForOldUser["gender"], newMatchForOldUser["name"]))
        else:
          textingClient.sendMessage(matchedPhoneNumber, \
            "Your current partner ended the conversation. We're looking for a new match and will text you when one is available.")

      # Get a new match for the user.
      matchedUser = db.getMatchForUser(userId)
      if matchedUser:
        conversation = db.insertConversation(userId, matchedUser["id"])
        resp.sms("You have a new texting partner: %s %s" % (matchedUser["gender"], matchedUser["name"]))
      else:
        resp.sms("Looking for a match. You'll get a text when one is available!")
        
    # Case: the user wants to pause service.
    elif instruction == "pause":
      db.pauseUser(userId)
      resp.sms("Paused. When you're read to start again, text #new to get a new conversation.")
      
  # If there's no user and the instruction is a digit, it's a verification code. So try to register the user.
  elif instruction.isdigit():
    if registerUser(instruction, phoneNumber):
      resp.sms("Welcome to convos, breh.")
    else:
      resp.sms("Verification code doesn't exist.")

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
  user = facebook.get_user_from_cookie(request.cookies, facebook_app_id, facebook_secret)
  if user:
    graph = facebook.GraphAPI(user["access_token"])
    profile = graph.get_object("me")
    friends = graph.get_connections("me", "friends")
    
    # Check if this user already exists in the database.
    existingUser = db.getUserFromFacebookUid(user["uid"])
    if existingUser:
      # If the user hasn't registered yet, send back the verification code.
      if existingUser["registration_status"] == "pending":
        response = {"status": "pending", "verification_code": existingUser["verification_code"]}
      else:
        response = {"status": "registered"}
    else:
      # Create a new user, with registration status pending.
      verificationCode = str(random.randint(1000, 10000))
      db.insertUserFromFacebookData(profile, verificationCode)
      response = {"status": "pending", "verification_code": verificationCode}
  else:
    response = {"status": "error", "error": "Not yet logged in to Facebook."}
  return json.dumps(response)
  
if __name__ == "__main__":
  app.run(debug=True)
