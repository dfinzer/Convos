import twilio.twiml

from strings import *
from testUtils import sendMessage
from twilio.rest import TwilioRestClient

# Twilio configuration.
TWILIO_ACCOUNT_SID = "AC52a3d465bd5577c994ebad881c1ac48a"
TWILIO_AUTH_TOKEN = "5fdc4c5e212bd4e3301211631ad5e729"
TWILIO_PHONE_NUMBER = "+19252720008"

client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class TwilioClient:
  def __init__(self, db):
    self.db = db
    
  # Sends a message in one of two ways: 1. via the Twilio REST API. 2. By modifying the
  # server's response to Twilio.
  def sendMessage(self, toNumber, body, existingResponse=None):    
    bodyStrings = arrayOfAppropriateLengthStringsFromString(body)
    
    # The index of the first bodyString that will be sent via the Twilio REST API.
    individualMessageBodyIndex = 0
    
    # If the server is crafting a twilio response, we'll use that, at least
    # for the first part of the message.
    if existingResponse:
      existingResponse.sms(bodyStrings[0])
      
      # Log the message.
      self.db.logMessage(toNumber, bodyStrings[0], True)
      
      # Since we sent that one using the response, we send the rest using the REST API.
      individualMessageBodyIndex = 1
      
    for bodyString in bodyStrings[individualMessageBodyIndex:]:
      self.sendIndividualMessage(toNumber, bodyString)
  
  def sendIndividualMessage(self, toNumber, body):
    # Send via twilio.
    client.sms.messages.create(to=toNumber, from_=TWILIO_PHONE_NUMBER, body=body)
    
    # Log the message.
    self.db.logMessage(toNumber, body, True)
  
  def sendWelcomeMessage(self, toNumber, existingResponse=None):
    self.sendMessage(toNumber, WELCOME_MESSAGE, existingResponse)
    
  def sendIncorrectVerificationCodeMessage(self, toNumber, existingResponse=None):
    self.sendMessage(toNumber, INCORRECT_VERIFICATION_CODE_MESSAGE, existingResponse)
  
  def sendUnknownMessage(self, toNumber, existingResponse=None):
    self.sendMessage(toNumber, UNKNOWN_MESSAGE, existingResponse)
  
  def sendPartnerEndedFindingMatchMessage(self, toNumber, existingResponse=None):
    self.sendMessage(toNumber, PARTNER_ENDED_FINDING_MATCH, existingResponse)
    
  def sendFindingMatchMessage(self, toNumber, existingResponse=None):
    self.sendMessage(toNumber, FINDING_MATCH, existingResponse)
    
  def sendPauseMessage(self, toNumber, existingResponse=None):
    self.sendMessage(toNumber, PAUSED, existingResponse)
    
  def sendUnknownInstructionMessage(self, toNumber, existingResponse=None):
    self.sendMessage(toNumber, UNKNOWN_INSTRUCTION, existingResponse)

  def sendPartnerMessage(self, toNumber, body):
    self.sendMessage(toNumber, "Partner: %s" % body)
    
  def sendNewMatchMessage(self, toNumber, matchedUser, matchedInterests, commonInterests, existingResponse=None):
    matchMessage = newMatchString(matchedUser["gender"], matchedUser["college"], \
      matchedInterests, commonInterests)
    self.sendMessage(toNumber, matchMessage, existingResponse)
    
  def sendPartnerEndedNewMatchMessage(self, toNumber, matchedUser, matchedInterests, commonInterests):
    matchMessage = partnerEndedNewMatchString(matchedUser["gender"], matchedUser["college"], \
      matchedInterests, commonInterests)
    self.sendMessage(toNumber, matchMessage)
    
  def sendPartnerEndedFindingMatchMessage(self, toNumber):
    self.sendMessage(toNumber, PARTNER_ENDED_FINDING_MATCH)
    
  def sendNoConversationUnpauseMessage(self, toNumber, existingResponse=None):
    self.sendMessage(toNumber, NO_CONVERSATION_UNPAUSE)
    
  def sendNoConversationMessage(self, toNumber, existingResponse=None):
    self.sendMessage(toNumber, NO_CONVERSATION)
    
class TwilioTestClient(TwilioClient):
  def sendIndividualMessage(self, toNumber, body):
    try:
      # We use the port as the phone number.
      sendMessage("localhost", toNumber, TWILIO_PHONE_NUMBER, body)
    # TODO: Handle exceptions better.
    except:
      print "Connection error sending message."
    print "Sending message to %s, body: {%s}" % (toNumber, body)
    
    # Log the message.
    self.db.logMessage(toNumber, body, True)