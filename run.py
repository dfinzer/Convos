from flask import Flask
import twilio.twiml
from twilio.rest import TwilioRestClient

app = Flask(__name__)

account_sid = "AC52a3d465bd5577c994ebad881c1ac48a"
auth_token = "5fdc4c5e212bd4e3301211631ad5e729"
client = TwilioRestClient(account_sid, auth_token)
 
#message = client.sms.messages.create(to="+19253896343", from_="+19252720008", \
#  body="Hello there!")

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/message", methods=['GET', 'POST'])
def message():
  resp = twilio.twiml.Response()
  message = "Hi there."
  resp.sms(message)
  
  return str(resp)

if __name__ == "__main__":
  app.run(debug=True)
