import json
import random
import requests

# server_url='https://fsmbeta.vertivco.com/'
# db_name='Fsm'
# username='muthu32@vertivbeta.com'
# password='vertiv123'

# username='mani@vertivbeta.com'
# password='vertiv123'

# server_url='https://betatest.vertiv.mongrov.net'
# db_name='test0403'
# username='admin@mongrov.com'
# password='mi123'

#
server_url='http://localhost:8069'
db_name='test1905'
username='mani@mongrov.com'
password='mi123'

search_domain = []
# ['call_no', 'ilike', 'c0122']
fetch_data=[]
# ['call_no','engineerId','call_facetime_ids','call_status','call_type','fault_reported','call_log_date']
# table_name='hr.employee'
table_name='cms.info.model'

# create_data=[{"notification_from": "Mani",
#     "notification_to": "ezhil@mongrov.com",
#     "notification_type":"email",
#     "body": "Dear sSURESH, for call no. C0222-CHEPW-3231543 Engineer Mitchell Admin. will reach in 15 min. From Vertiv Customer care team",
#     "subject":"C0222-CHEPW-3231543 Service Update "}]


json_endpoint = "%s/jsonrpc" % server_url
headers = {"Content-Type": "application/json"}
def get_json_payload(service, method, *args):
 return json.dumps({
 "jsonrpc": "2.0",
 "method": 'call',
 "params": {
 "service": service,
 "method": method,
 "args": args
 },
 "id": random.randint(0, 100000000),
 })

 # return json.dumps({
 # "jsonrpc": "2.0",
 # "method": 'call',
 # "params": {
 # "service": service,
 # "method": method,
 # "args": args
 # },
 # "id": random.randint(0, 100000000),
 # })
payload = get_json_payload("common", "login", db_name,
username, password)
response = requests.post(json_endpoint, data=payload,
headers=headers)
user_id = response.json()['result']
if user_id:
 print("Success: User id is", user_id)
 # search for the books ids

 # payload = get_json_payload("object", "execute_kw",
 #                            db_name, user_id, password,
 #                            table_name, 'search', [search_domain], {'limit':15})


 # res = requests.post(json_endpoint, data=payload,
 #                     headers=headers).json()
 # print('Search Result:', res)  # ids will be in result keys
# read data for books ids
#  payload = get_json_payload("object", "execute_kw",
#                             db_name, user_id, password,
#                             table_name,'check_access_rights', ['read'], {'raise_exception': False})
#
#  res = requests.post(json_endpoint, data=payload,
#                      headers=headers).json()
#  print('Access read data:', res)

 # payload = get_json_payload("object", "execute_kw",
 #                            db_name, user_id, password,
 #                            table_name, 'search_read',  [search_domain,fetch_data ])
 payload = get_json_payload("object", "execute_kw",
                            db_name, user_id, password,
                            table_name, 'generate_number',  ['POWSER'])
 res = requests.post(json_endpoint, data=payload,
                     headers=headers).json()
 print('Calls data:', res)
 # payload = get_json_payload("object", "execute_kw",
 #                            db_name, user_id, password,
 #                            table_name, 'create',  [create_data])
 # res = requests.post(json_endpoint, data=payload,
 #                     headers=headers).json()
 # print('Create data:', res)

else:
    print("Failed: wrong credentials")
