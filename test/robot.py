import argparse
import httplib
import urllib

def postRequest(conn, path, params):
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
  conn.request("POST", path, urllib.urlencode(params), headers)
  response = conn.getresponse()
  return response.read()
  
def sendMessage(host, port, phoneNumber, body):
  conn = httplib.HTTPConnection(host, port)
  params = {"From": phoneNumber, "Body": body}
  postRequest(conn, "/message", params)

# Parse command line options
parser = argparse.ArgumentParser(description='Command line options for convos robot.')
parser.add_argument('--host', type=str, default="localhost")
parser.add_argument('--port', type=int, default=10080)
parser.add_argument('--body', type=str, default="Test message")
parser.add_argument('--phoneNumber', type=str, default="+19253896343")
args = parser.parse_args()

# Send a message.
print "Sending message '%s' from %s" % (args.body, args.phoneNumber)
sendMessage(args.host, args.port, args.phoneNumber, args.body)