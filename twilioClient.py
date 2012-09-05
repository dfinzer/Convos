import twilio.twiml

from strings import *
from testUtils import sendMessage
from twilio.rest import TwilioRestClient

# Twilio configuration.
TWILIO_ACCOUNT_SID = "AC52a3d465bd5577c994ebad881c1ac48a"
TWILIO_AUTH_TOKEN = "5fdc4c5e212bd4e3301211631ad5e729"

SECRET_NUMBER_STRING = "$"

client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class TwilioClient:
  def __init__(self, db):
    self.db = db
    
  # Sends a message in one of two ways: 1. via the Twilio REST API. 2. By modifying the
  # server's response to Twilio.
  def sendMessage(self, toNumber, twilioNumber, body, existingResponse=None):    
    bodyStrings = arrayOfAppropriateLengthStringsFromString(body)
    
    # The index of the first bodyString that will be sent via the Twilio REST API.
    individualMessageBodyIndex = 0
    
    # If the server is crafting a twilio response, we'll use that, at least
    # for the first part of the message.
    if existingResponse:
      existingResponse.sms(bodyStrings[0])
      
      # Log the message.
      self.db.logMessage(toNumber, twilioNumber, bodyStrings[0], True)
      
      # Since we sent that one using the response, we send the rest using the REST API.
      individualMessageBodyIndex = 1
      
    for bodyString in bodyStrings[individualMessageBodyIndex:]:
      self.sendIndividualMessage(toNumber, twilioNumber, bodyString)
  
  def sendIndividualMessage(self, toNumber, twilioNumber, body):
    # Don't send numbers that begin with the secret number string. We reserve these for
    # admin purposes.
    if not toNumber.startswith(SECRET_NUMBER_STRING):
      # Send via twilio.
      client.sms.messages.create(to=toNumber, from_=twilioNumber["number"], body=body)
    
    # Log the message.
    self.db.logMessage(toNumber, twilioNumber, body, True)
  
  def sendWelcomeMessage(self, toNumber, twilioNumber, existingResponse=None):
    self.sendMessage(toNumber, twilioNumber, WELCOME_MESSAGE, existingResponse)
    
  def sendIncorrectVerificationCodeMessage(self, toNumber, twilioNumber, existingResponse=None):
    self.sendMessage(toNumber, twilioNumber, INCORRECT_VERIFICATION_CODE_MESSAGE, existingResponse)
  
  def sendUnknownMessage(self, toNumber, twilioNumber, existingResponse=None):
    self.sendMessage(toNumber, twilioNumber, UNKNOWN_MESSAGE, existingResponse)
  
  def sendPartnerEndedFindingMatchMessage(self, toNumber, twilioNumber, existingResponse=None):
    self.sendMessage(toNumber, twilioNumber, PARTNER_ENDED_FINDING_MATCH, existingResponse)
    
  def sendFindingMatchMessage(self, toNumber, twilioNumber, existingResponse=None):
    self.sendMessage(toNumber, twilioNumber, FINDING_MATCH, existingResponse)
    
  def sendPauseMessage(self, toNumber, twilioNumber, existingResponse=None):
    self.sendMessage(toNumber, twilioNumber, PAUSED, existingResponse)
    
  def sendUnknownInstructionMessage(self, toNumber, twilioNumber, existingResponse=None):
    self.sendMessage(toNumber, twilioNumber, UNKNOWN_INSTRUCTION, existingResponse)

  def sendPartnerMessage(self, toNumber, twilioNumber, body):
    self.sendMessage(toNumber, twilioNumber, "Partner: %s" % body)
    
  def sendNewMatchMessage(self, toNumber, twilioNumber, matchedUser, matchedInterests, commonInterests, existingResponse=None):
    matchMessage = newMatchString(matchedUser["gender"], matchedUser["college"], \
      matchedInterests, commonInterests)
    self.sendMessage(toNumber, twilioNumber, matchMessage, existingResponse)
    
  def sendPartnerEndedNewMatchMessage(self, toNumber, twilioNumber, matchedUser, matchedInterests, commonInterests):
    matchMessage = partnerEndedNewMatchString(matchedUser["gender"], matchedUser["college"], \
      matchedInterests, commonInterests)
    self.sendMessage(toNumber, twilioNumber, matchMessage)
    
  def sendPartnerEndedFindingMatchMessage(self, toNumber, twilioNumber):
    self.sendMessage(toNumber, twilioNumber, PARTNER_ENDED_FINDING_MATCH)
    
  def sendNoConversationUnpauseMessage(self, toNumber, twilioNumber, existingResponse=None):
    # TODO: why don't these include existingResponse?
    self.sendMessage(toNumber, twilioNumber, NO_CONVERSATION_UNPAUSE)
    
  def sendNoConversationMessage(self, toNumber, twilioNumber, existingResponse=None):
    # TODO: why don't these include existingResponse?
    self.sendMessage(toNumber, twilioNumber, NO_CONVERSATION)
  
  def sendMaxConversationsMessage(self, toNumber, twilioNumber, existingResponse=None):
    self.sendMessage(toNumber, twilioNumber, MAX_CONVERSATIONS, existingResponse)
    
  def sendHelpMessage(self, toNumber, twilioNumber, existingResponse=None):
    self.sendMessage(toNumber, twilioNumber, HELP_MESSAGE, existingResponse)
    
  def sendSignupUrl(self, toNumber, twilioNumber, verificationCode, existingResponse=None):
    signupMessage = signupUrlString(verificationCode)
    self.sendMessage(toNumber, twilioNumber, signupMessage, existingResponse)
    
class TwilioTestClient(TwilioClient):
  def sendMessage(self, toNumber, twilioNumber, body, existingResponse=None):
    # Just logs the message. Doesn't send via twilio.
    self.db.logMessage(toNumber, twilioNumber, body, True)