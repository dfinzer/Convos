import re

# String constants.
WELCOME_MESSAGE = "Welcome to Convos! Text \
#new at any time to start a new convo (without ending your current one), or #help for more options."

HELP_MESSAGE = "#new - get a new partner (without ending your current convo)\n\
#end - end the current convo on this number\n\
#pause - take a break (end all current convos)"

INCORRECT_VERIFICATION_CODE_MESSAGE = "That verification code doesn't match our records. \
Make sure you entered the verification code correctly."

NEW_MATCH = "You have a new texting partner! "
SAY_HI = "Say hi! (just reply to this number)"
FINDING_MATCH = "Looking for a new match. You'll get a text when one is available!"

PARTNER_ENDED_NEW_MATCH = "Your current partner ended the conversation, but we matched \
you up with someone new: "
PARTNER_ENDED_FINDING_MATCH = "Your current partner ended the conversation. \
We're looking for a new match and will text you when one is available."

PAUSED = "Convos is now paused. When you're ready to start again, text #new to get a new conversation."

UNKNOWN_INSTRUCTION = "Convos doesn't recognize this instruction. Valid instructions are: \
#new - new conversation, #pause - take a break."
UNKNOWN_MESSAGE = "Convos doesn't recognize this phone number. Please check that you entered the correct four-digit verification code."

PHONE_NUMBER_ALREADY_REGISTERED = "This phone number is already registered with Convos. Please use a different phone number."

NO_CONVERSATION_UNPAUSE = "Convos is paused. Text #new to unpause and start a new convo."
NO_CONVERSATION = "You aren't in a conversation with anyone at the moment on this number. We'll text you when we find someone. Hold tight!"

MAX_CONVERSATIONS = "Sorry, you can only have 3 conversations at a time. You'll have to send #end to one of your conversations to get a \
new partner."

SIGNUP_URL = "Welcome to Convos. To get started, click the following url: http://getconvos.com?code=%s"

REMINDER_LAST_TEXTER = "It's been a while since you've received a message from your texting partner. To end the conversation, text #end. To start a \
new conversation (without ending this one), text #new."
REMINDER_NOT_LAST_TEXTER = "It's been a while since you've responded to this conversation. To end the conversation text #end, or to start a new \
conversation (without ending this one), text #new."

# Other constants.
SMS_MAX_LENGTH = 160

# Brute forces an array of strings with length < 160. Just takes the first 160 characters
# until we run out of characters.
def bruteForceArrayOfAppropriateLengthStringsFromString(string):
  stringArray = []
  startIndex = 0
  endIndex = SMS_MAX_LENGTH
  while startIndex < len(string):
    stringArray += [string[startIndex:endIndex]]
    startIndex += SMS_MAX_LENGTH
    endIndex += SMS_MAX_LENGTH
  return stringArray

# Gets an array of appropriate length strings from a longer string.
def arrayOfAppropriateLengthStringsFromString(string):
  stringLength = len(string)
  
  # If the length of the string is less than the maximum length, we're all good.
  if stringLength <= SMS_MAX_LENGTH:
    return [string]
  else:
    # First we'll try the smart method. Ideally, we want to break up the string by punctuation.
    # First find all the indices of punctuation.
    punctuationIndices = [m.start() for m in re.finditer('[,.!]', string)]
    
    if len(punctuationIndices) > 0:
      # Find a punctuation index that results in substrings with equal length.
      minDiff = stringLength
      bestIndex = -1
            
      # Iterate through the indices of punctuation, looking for an appropriate splitting point.
      for punctuationIndex in punctuationIndices:
        splitIndex = punctuationIndex + 1
        if splitIndex >= stringLength:
          continue
          
        firstStringLength = splitIndex
        secondStringLength = stringLength - splitIndex
        diff = abs(firstStringLength - splitIndex)
        
        if diff < minDiff and firstStringLength < SMS_MAX_LENGTH \
          and secondStringLength < SMS_MAX_LENGTH:
          minDiff = diff
          bestIndex = splitIndex
      
      # If we found a good index, return it.
      if bestIndex != -1:
        return [string[0:bestIndex], string[bestIndex:]]
      # Otherwise just brute force it.
      else:
        return bruteForceArrayOfAppropriateLengthStringsFromString(string)
        
    # If there's no punctuation to brute force it.
    # TODO: we should really brute force by words, but we're keeping the logic simple for now.
    else:
      return bruteForceArrayOfAppropriateLengthStringsFromString(string)

# Abbreviates the college string.
def abbreviatedCollegeString(college):
  college = college.replace(" University", "")
  college = college.replace(" College", "")
  college = college.replace(", ", " '")
  college = college.replace("20", "")
  return college

# Generates a "new match" string given the available data.
def newMatchString(gender, college, interests, commonInterests, newMatchMessage=NEW_MATCH):
  # Capitalize gender.
  gender = "Male" if gender == "male" else "Female"
  
  newPartnerString = newMatchMessage
  if gender:
    newPartnerString += gender
  if college:
    newPartnerString += ", from " + abbreviatedCollegeString(college)
  if len(commonInterests) > 0:
    newPartnerString += " with common interests in "
    newPartnerString += ", ".join(commonInterests[:2])
  elif len(interests) > 0:
    newPartnerString += " with interests in "
    newPartnerString += ", ".join(interests[:2])
  newPartnerString += (". " + SAY_HI)
  return newPartnerString

def partnerEndedNewMatchString(gender, college, interests, commonInterests):
  return newMatchString(gender, college, interests, commonInterests, PARTNER_ENDED_NEW_MATCH)
  
def signupUrlString(verificationCode):
  return SIGNUP_URL % verificationCode