from twilio.rest import TwilioRestClient

# Twilio configuration.
account_sid = "AC52a3d465bd5577c994ebad881c1ac48a"
auth_token = "5fdc4c5e212bd4e3301211631ad5e729"
twilio_phone_number = "+19252720008"
client = TwilioRestClient(account_sid, auth_token)

class TwilioClient:
  def sendMessage(self, toNumber, body):
    print "Using Twilio to send message to %s, body {%s}" % (toNumber, body)
    client.sms.messages.create(to=toNumber, from_=twilio_phone_number, body=body)
      
class TwilioTestClient(TwilioClient):
  def sendMessage(self, toNumber, body):
    print "Sending message to %s, body: {%s}" % (toNumber, body)