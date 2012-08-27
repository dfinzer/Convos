import db
import facebook
import json
import twilio.twiml

from flask import Flask
from flask import request
from twilio.rest import TwilioRestClient

app = Flask(__name__)

# Twilio configuration.
account_sid = "AC52a3d465bd5577c994ebad881c1ac48a"
auth_token = "5fdc4c5e212bd4e3301211631ad5e729"
client = TwilioRestClient(account_sid, auth_token)

# Facebook configuration.
facebook_app_id = '326547147430900'
facebook_secret = 'd0347b67f972d8c3c751c7a29ee55b5d'

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/message", methods=['GET', 'POST'])
def message():
  resp = twilio.twiml.Response()
  message = "Hi there."
  resp.sms(message)
  
  return str(resp)

@app.route("/register", methods=['POST'])
  # Get the verification code the user entered.
  enteredVerificationCode = request.form["verification_code"]
  
  # Check it against the stored verification code.
  user = facebook.get_user_from_cookie(request.cookies, facebook_app_id, facebook_secret)
  
  # TODO: check verification code.

@app.route("/login", methods=['POST'])
def login():
  user = facebook.get_user_from_cookie(request.cookies, facebook_app_id, facebook_secret)
  if user:
    graph = facebook.GraphAPI(user["access_token"])
    profile = graph.get_object("me")
    friends = graph.get_connections("me", "friends")
    response = {"status": "ok"}
    
    # Check if this user already exists in the database.
    existingUser = db.getUserFromFacebookUid(user["uid"])
    if existingUser:
      response = {"status": user["registration_status"]}
    
    # Create a new user, with registration status pending.
    verificationCode = "12345"
    db.insertUserFromFacebookData(profile, verificationCode)
    response = {"status": "pending", "verification_code": verificationCode}
  else:
    response = {"status": "Not yet logged in with facebook."}
  return json.dumps(response)
  
if __name__ == "__main__":
  app.run(debug=True)
