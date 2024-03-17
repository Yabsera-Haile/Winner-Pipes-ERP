from xmlrpc import client

server_url='http://localhost:8069'
db_name='Vertivnew'
username='mani@mongrov.com'
password='manik123'

# server_url='https://fsm.vertiv.mongrov.net'
# db_name='fsm'
# username='admin@mongrov.com'
# password='mi123'

common = client.ServerProxy('%s/xmlrpc/2/common' % server_url)
models=client.ServerProxy('%s/xmlrpc/2/object' % server_url)
user_id = common.authenticate(db_name, username, password, {})
if user_id:
 print("Success: User id is", user_id)
 search_domain = ['call_no', 'ilike', 'C0122'],
 call_info_ids=models.execute_kw(db_name,user_id,password,'cms.info.model','search',[search_domain],{'limit':5})
 call_info_data=models.execute_kw(db_name,user_id,password,'cms.info.model','read',[call_info_ids,['call_no']])
 print(call_info_data)
else:
 print("Failed: wrong credentials")