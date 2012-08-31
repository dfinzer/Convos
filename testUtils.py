import httplib
import urllib

def postRequest(conn, path, params):
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
  conn.request("POST", path, urllib.urlencode(params), headers)
  response = conn.getresponse()
  return response.read()
  
def sendMessage(host, port, phoneNumber, body, toNumber="0"):
  conn = httplib.HTTPConnection(host, port)
  params = {"From": phoneNumber, "Body": body, "To": toNumber}
  return postRequest(conn, "/api/message", params)