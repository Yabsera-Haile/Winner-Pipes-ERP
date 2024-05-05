import token

import requests
import json
from requests import Request, Session

HTML = "https://vertivco.mongrov.net"


def generate_token(username, password):
  login_payload = json.dumps({
    "user": username,
    "password": password
  })
  login_endpoint = "%s/api/v1/login" % HTML
  login_headers = {
    'Content-Type': 'application/json'
  }
  login_res = requests.request("POST", login_endpoint, headers=login_headers, data=login_payload)
  login_data = login_res.json()
  return ({'Token': login_data['data']['authToken'], 'Userid': login_data['data']['userId']})

def login_token(payload):
  print("Received payload for logging",payload,type(payload))

  login_payload =  json.dumps(payload)
  print(login_payload)
  login_endpoint = "%s/api/v1/login" % HTML
  login_headers = {
    'Content-Type': 'application/json'
  }

  login_res = requests.request("POST", login_endpoint, headers=login_headers, data=login_payload)
  print("Login response:",login_res)
  login_data = login_res.json()
  print(login_data)
  return(login_data)

def create_personal_token(payload, headers):
  token_endpoint = "%s/api/v1/users.createToken" % HTML
  token_headers = headers
  token_payload = json.dumps(payload)
  token_res = requests.request("POST", token_endpoint, headers=token_headers, data=token_payload)
  print(token_res.text, token.EXACT_TOKEN_TYPES, token.tok_name)
  return token_res


def create_collab_user(payload, headers):
  create_endpoint = "%s/api/v1/users.create" % HTML
  print(payload)
  create_payload = json.dumps({
    "name": payload['name'],
    "password": payload['password'],
    "email": payload['email'],
    "username": payload['username'],
  })
  print(create_payload)
  collab_create_response = requests.request("POST", create_endpoint, data=create_payload, headers=headers)
  print(collab_create_response.text)
  return(collab_create_response)


def register_user(payload):
  register_endpoint="%s/api/v1/users.register" % HTML
  register_payload=json.dumps({
    "name": payload['name'],
    "pass": payload['password'],
    "email": payload['email'],
    "username": payload['username'],
  })
  headers = {
    'Content-Type': 'application/json'
  }
  register_response = requests.request("POST", register_endpoint, data=register_payload, headers=headers)
  return(register_response)

url = "https://vertivco.mongrov.net/api/v1/login"

#test for Login using vertivco sample

url = "%s/api/v1/vertivusers.createToken" % HTML
print(url)
login_endpoint = url
payload = json.dumps({
  "user": "admin",
  "password": "mi123",
  "email": "admin@mongrov.com",
  "vtoken": "u6a3fkt40ywp"
})

headers = {
  'Content-Type': 'application/json'
}

print(payload,"\n",headers)
sess = Session()
response = requests.request("POST", url, headers=headers, data=payload)
# print("\\nresponse",response)
login_data = response.json()
print("lOGIN DATEA",login_data)
if (login_data['success'] == 'True'):
  print("Success story:")
  print("Login Data", login_data, login_data.get('data').get('authToken'))
else:
  print("failure")
print(response)


tpayload = {
  "resume": login_data['data']['authToken'],
}
print(tpayload)
s=login_token(tpayload)
print("Using Get:",s.get('data').get('authToken'))
instance= "%s/api/v1/instances.get" % HTML
header={
  'X-User-Id':login_data['data']['userId'],
  'X-Auth-Token':login_data['data']['authToken']
}
print(header)
response = requests.request("GET", instance, headers=header)
print("STATUS OF S GET",sess.adapters)

login_payload =  json.dumps(tpayload)
print(login_payload)
url = "%s/api/v1/login" % HTML
login_headers = {
  'Content-Type': 'application/json'
}

options = {
  'headers': login_headers,
  'data': login_payload
}

session = Session()
request = Request('POST', url, **options)
prepped = request.prepare()
r = session.send(prepped)

print("\n\n\n Printing session value",r.json())

#########################test ends

##############Generate token for admin saple
email = 'admin@mongrov.com'
password = 'mi123'
login_payload = json.dumps({
  "user": email,
  "password": password
})

s = generate_token(email, password)
print("New token", s['Token'])
admin_data = generate_token(email, password)
headers = {
  'Content-Type': 'application/json',
  'X-Auth-Token': admin_data['Token'],
  'X-User-Id': 'bZr6E2cAKckQX2gRm'
}
payload = {'name': 'Raghul', 'email': 'raghul@mongrov.com', 'username': 'raghul', 'password': 'vertiv123'}
t = create_collab_user(payload, headers)
print(t)
payload = {'username': 'raghul'}
s = create_personal_token(payload, headers)
print("Personal token", s.text)

login_payload = json.dumps({
  "resume": admin_data['Token']
})
login_endpoint = "%s/api/v1/login" % HTML
login_headers = {
  'Content-Type': 'application/json'
}
login_res = requests.request("POST", login_endpoint, headers=login_headers, data=login_payload)
login_data = login_res.json()
print(login_data)

######################Ends
#Register user flow
# payload = {'name': 'Ra2aghul', 'email': 'raghw2ul@mongrov.com', 'username': 'raaghul', 'password': 'vertiv123'}
# t = register_user(payload)
# print(t.text)
###########Registe
