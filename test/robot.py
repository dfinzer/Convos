def postRequest(conn, path, params):
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
  conn.request("POST", path, urllib.urlencode(params), headers)
  response = conn.getresponse()
  return response.read()

def sendMessage(phoneNumber, body):
  conn = httplib.HTTPConnection("localhost", globals.HTTP_PORT)
  params = {"From": phoneNumber, "Body": body}
  postRequest(conn, "/message", params)
  
