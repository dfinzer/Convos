from strings import arrayOfAppropriateLengthStringsFromString
from testUtils import sendMessage
from twilio.rest import TwilioRestClient

# Twilio configuration.
TWILIO_ACCOUNT_SID = "AC52a3d465bd5577c994ebad881c1ac48a"
TWILIO_AUTH_TOKEN = "5fdc4c5e212bd4e3301211631ad5e729"
TWILIO_PHONE_NUMBER = "+19252720008"

client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class TwilioClient:
  def sendMessage(self, toNumber, body):
    bodyStrings = arrayOfAppropriateLengthStringsFromString(body)
    for bodyString in bodyStrings:
      self.sendIndividualMessage(toNumber, bodyString)
  
  def sendIndividualMessage(self, toNumber, body):
    client.sms.messages.create(to=toNumber, from_=TWILIO_PHONE_NUMBER, body=body)
      
class TwilioTestClient(TwilioClient):
  def sendIndividualMessage(self, toNumber, body):
    # We use the port as the phone number.
    sendMessage("localhost", toNumber, TWILIO_PHONE_NUMBER, body)
    print "Sending message to %s, body: {%s}" % (toNumber, body)