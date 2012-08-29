import argparse

from flask import Flask, request, session
from testUtils import sendMessage

# Parse command line options
parser = argparse.ArgumentParser(description='Command line options for convos robot.')
parser.add_argument('--host', type=str, default="localhost")
parser.add_argument('--port', type=int, default=10080)
parser.add_argument('--number', type=int, default=8000)
parser.add_argument('--body', type=str, default="Test message")
parser.add_argument('--send', type=bool, default=False)
args = parser.parse_args()

if args.send:
  # Send a message.
  print "Sending message '%s' from %s" % (args.body, args.number)
  print "Received " + sendMessage(args.host, args.port, args.number, args.body)
else:
  app = Flask(__name__)

  # Receive messages.
  @app.route("/message", methods=['POST'])
  def receiveMessage():
    print "Received {" + request.values.get("Body") + "}"
    return "Received message"

  # Run on the port of the phone number.
  app.run(debug=True, port=args.number)
