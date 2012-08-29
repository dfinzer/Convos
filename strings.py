import re

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
        return [string[0:bestIndex], string[bestIndex:stringLength]]
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
  college = college.replace(", ", "'")
  return college

# Generates a "new match" string given the available data.
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