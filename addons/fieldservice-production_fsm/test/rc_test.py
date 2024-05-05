import token

import requests
import json

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


url = "https://vertivco.mongrov.net/api/v1/login"
login_endpoint = url
payload = json.dumps({
  "user": "admin",
  "password": "mi123"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
login_data = response.json()
print(login_data['status'])
if (login_data['status'] == 'success'):
  print("Success story:")
else:
  print("failure")
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
