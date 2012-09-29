# Runs scripts for convos, including running the dev server and sending reminders to stagnant conversations.
from application import *
from datetime import datetime, timedelta
from flask.ext.script import Manager

manager = Manager(app)

# Remind users of their options if they're in stagnant conversations.
@manager.command
@manager.option('-t', '--texts', help='Text reminders.')
@manager.option('-s', '--stagancy_threshold', help='How many hours qualify a conversation as stagnant.')
def remind(texts=False, stagnancy_threshold=24):
  db.openConnection()

  # Iterate through active conversations.
  conversations = db.getInProgressConversations()
  for conversation in conversations:
    message = db.getLastMessageForConversation(conversation["id"])
    reminder = db.getReminderForConversation(conversation["id"])
    twentyFourHours = timedelta(hours=int(stagnancy_threshold))

    # Check that a message hasn't been sent in the last twenty four hours.
    if message["timestamp"] and datetime.now() - message["timestamp"]  > twentyFourHours:
      userOne = db.getUserFromId(conversation["user_one_id"])
      userTwo = db.getUserFromId(conversation["user_two_id"])
      print "Stagnant conversation for users %s, %s %s" % (userOne["name"], userTwo["name"], \
        ("(reminder sent)" if reminder else "(no reminder sent)"))
        
      # If texting mode is off, don't send a message.
      if not texts:
        continue
      
      # If no reminder has been sent yet, send one.
      if not reminder:
        # Get the user id's for the last person who texted and the user who hasn't texted.
        lastTexterUserId = message["from_user_id"]
      
        # Get the twilio numbers for the users.
        if lastTexterUserId == conversation["user_one_id"]:
          lastTexterTwilioNumberId = conversation["user_one_twilio_number_id"]
          notLastTexterTwilioNumberId = conversation["user_two_twilio_number_id"]
        else:
          lastTexterTwilioNumberId = conversation["user_two_twilio_number_id"]
          notLastTexterTwilioNumberId = conversation["user_one_twilio_number_id"]
      
        # Fetch the twilio numbers from the db.
        lastTexterTwilioNumber = db.getTwilioNumberFromId(lastTexterTwilioNumberId)
        notLastTexterTwilioNumber = db.getTwilioNumberFromId(notLastTexterTwilioNumberId)
      
        # Get user data.
        lastTexterUser = db.getUserFromId(lastTexterUserId)
        notLastTexterUserId = getOtherUserId(conversation, lastTexterUser["id"])
        notLastTexterUser = db.getUserFromId(notLastTexterUserId)

        # Send the messages.
        textingClient.sendReminderLastTexter(lastTexterUser["phone_number"], \
          lastTexterTwilioNumber)
        textingClient.sendReminderNotLastTexter(notLastTexterUser["phone_number"], \
          notLastTexterTwilioNumber)

        # Insert the reminder into the database.
        db.insertReminderForConversation(conversation["id"])
  
  db.closeConnection()

if __name__ == "__main__":
  manager.run()

