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
  def sendMessage(self, toNumber, body, existingResponse=None):    
    bodyStrings = arrayOfAppropriateLengthStringsFromString(body)
    individualMessageBodyIndex = 0
    if existingResponse:
      existingResponse.sms(bodyStrings[0])
      individualMessageBodyIndex = 1
      
    for bodyString in bodyStrings[individualMessageBodyIndex:]:
      self.sendIndividualMessage(toNumber, bodyString)
  
  def sendIndividualMessage(self, toNumber, body):
    client.sms.messages.create(to=toNumber, from_=TWILIO_PHONE_NUMBER, body=body)
  
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
    
  def sendNewMatchMessage(self, toNumber, matchedUser, matchedInterests, existingResponse=None):
    matchMessage = newMatchString(matchedUser["gender"], matchedUser["college"], \
      matchedInterests)
    self.sendMessage(toNumber, matchMessage, existingResponse)
    
  def sendPartnerEndedNewMatchMessage(self, toNumber, matchedUser, matchedInterests):
    matchMessage = partnerEndedNewMatchString(matchedUser["gender"], matchedUser["college"], \
      matchedInterests)
    self.sendMessage(toNumber, matchMessage, existingResponse)
    
  def sendPartnerEndedFindingMatchMessage(self, toNumber):
    self.sendMessage(toNumber, PARTNER_ENDED_FINDING_MATCH)
    
class TwilioTestClient(TwilioClient):
  def sendIndividualMessage(self, toNumber, body):
    try:
      # We use the port as the phone number.
      sendMessage("localhost", toNumber, TWILIO_PHONE_NUMBER, body)
    # TODO: Handle exceptions better.
    except:
      print "Connection error sending message."
    print "Sending message to %s, body: {%s}" % (toNumber, body)