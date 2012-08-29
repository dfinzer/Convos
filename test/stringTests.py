from strings import *

shortString = "Yo what's up dog"
longStringNoPunctuation = "This is a very long string with spaces but no punctuaation hopefully \
  it is greater than 160 characters that is all apparently it wasnt so i am \
  making it longer wooo hooo catch me if you can im such a boss"
veryLongStringNoPunctuation = longStringNoPunctuation + longStringNoPunctuation

longStringPunctuation = "This is a very long string with spaces. and punctuaation hopefully \
  it is greater than 160 characters that is all. apparently it wasnt so i am \
  making it longer wooo hooo catch me if you can. im such a boss"
  
longStringPunctuationAtEnd = longStringNoPunctuation + "."
longStringPunctuationAtStart = "." + longStringNoPunctuation
  
strings = [shortString, longStringNoPunctuation, veryLongStringNoPunctuation, longStringPunctuation, \
  longStringPunctuationAtEnd, longStringPunctuationAtStart]
  
def checkStringArray(stringArray):
  for string in stringArray:
    assert(len(string) <= SMS_MAX_LENGTH)
    
for string in strings:
  stringArray = arrayOfAppropriateLengthStringsFromString(string)
  print stringArray
  checkStringArray(stringArray)