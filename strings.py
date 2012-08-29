# String constants.

WELCOME_MESSAGE = "Welcome to Convos. To start a new conversation text #new. \
  Text #new at any time to end your current conversation and start a new one."

INCORRECT_VERIFICATION_CODE_MESSAGE = "That verification code doesn't match our records. \
  Make sure you entered the verification code correctly."
  
NEW_MATCH = "You have a new texting partner! "
SAY_HI = "Say Hi!"
FINDING_MATCH = "Looking for a match. You'll get a text when one is available!"

PARTNER_ENDED_NEW_MATCH = "Your current partner ended the conversation, but we matched \
  you up with someone new: "
PARTNER_ENDED_FINDING_MATCH = "Your current partner ended the conversation. \
  We're looking for a new match and will text you when one is available."

PAUSED = "Convos is now paused. When you're ready to start again, text #new to get a new conversation."

UNKNOWN_MESSAGE = "Convos doesn't recognize this instruction. Valid instructions are: \
  #new - new conversation, #pause - take a break."
UNKNOWN_MESSAGE = "Convos doesn't recognize this phone number. Please check that you entered the correct four-digit verification code."

PHONE_NUMBER_ALREADY_REGISTERED = "This phone number is already registered with Convos. Please use a different phone number."

# TODO: these should return an array of appropriately broken up strings that can be then sent to the twilioClient for distribution.

def abbreviatedCollegeString(college):
  college = college.replace(" University", "")
  college = college.replace(" College", "")
  college = college.replace(", ", "'")
  return college

# Generates an appropriate array of "new match" strings given the available data.
def newMatchString(gender, college, interests, newMatchMessage=NEW_MATCH):
  newPartnerString = NEW_MATCH
  if gender:
    newPartnerString += gender + ", "
  if college:
    newPartnerString += abbreviatedCollegeString(college)
  if len(interests) > 0:
    newPartnerString += " with interests in "
    newPartnerString += ", ".join(interests[:3])
  newPartnerString += (". " + SAY_HI)
  return newPartnerString

def partnerEndedNewMatchString(gender, college, interests):
  return partnerEndedNewMatchString + newMatchString(gender, college, interests, PARTNER_ENDED_NEW_MATCH)