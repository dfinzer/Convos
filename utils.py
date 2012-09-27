# Gets the other user id from a conversation.
def getOtherUserId(conversation, userId):
  return conversation["user_two_id"] if conversation["user_one_id"] == userId \
    else conversation["user_one_id"]

def getOtherUserTwilioNumberId(conversation, userId):
  return conversation["user_two_twilio_number_id"] if conversation["user_one_id"] == userId \
    else conversation["user_one_twilio_number_id"]