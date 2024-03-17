from odoo import fields, models, api
from datetime import datetime, timedelta
from odoo import tools
import logging
import random
import threading
from datetime import date, datetime, timedelta
from psycopg2 import sql
from odoo import _
from odoo.exceptions import ValidationError
import requests
import json
from requests import Request, Session
from odoo import tools
import os
import sys
from sys import path, argv

HTML = ''
TOKEN=""
rcUsername = ''
rcPassword = ''

#Default password if no password is given
PASS_WORD = ''
_logger = logging.getLogger(__name__)



class Collab(models.Model):
    _name = "collab"
    _description = "Collab"

    @api.model
    def _get_html(self):
        global TOKEN, HTML
        Parameters = self.env['ir.config_parameter'].sudo()
        HTML = Parameters.get_param('vertiv_collab_reference_id')
        # HTML = tools.config['html']


    def _get_credentials(self):
        global rcUsername,rcPassword
        folder_found = False
        addons_path = tools.config['addons_path'].split(',')

        for addons_folder in addons_path:
            readme_path = addons_folder + '\\Vertiv'
         
            if os.path.isdir(readme_path):
                folder_found = True
                try:
                    f = open(readme_path + '/fsm.conf', "r")

                    f.close()
                except:
                    raise ValidationError(('Unable to read file at ' + readme_path))
                    return
                break

        if not folder_found:
            raise ValidationError("Unable to find  folder ")
            # TODO to be removed for production
            return
        rcfilepath = os.path.join(readme_path, 'fsm.conf')

        fsmvars = {}
        with open(rcfilepath, "r") as myfile:
            for line in myfile:
                line = line.strip()
                name, var = line.partition("=")[::2]
                fsmvars[name.strip()] = str(var)

        rcUsername = fsmvars['uname']
        rcPassword=fsmvars['upwd']

        myfile.close()
        
    def _get_user_token(self,emailid):
        self._get_html()
        createtoken_endpoint = "%s/api/v1/vertivusers.createToken" % HTML

        payload = json.dumps({
            "email": emailid,
            "vtoken": "u6a3fkt40ywp"
        })


        headers = {
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", createtoken_endpoint, headers=headers, data=payload)
        except Exception as e:
            raise ValidationError(_("Error , Contact admin \n %s ", e))

            return

        responsedata=response.json()

        if(responsedata['success']):
            userId=responsedata['data']['userId']
            authToken=responsedata['data']['authToken']
            return(userId,authToken)
        else:
            raise ValidationError(_("User not found , Contact admin \n  "))

    def _user_update(self,values,userid,type=None):
        global rcUsername, rcPassword
        
        if type=='profile':
            profileDetails={'name': values.name, 'email': values.email, 'mobile': values.mobile, 'manager': values.manager, 'product_group': values.product_group, 'role':values.role, 'city':values.city, 'state':values.state, 'branch':values.branch}
            data={'customFields': {"profileDetails": json.dumps(profileDetails), "userProfile": ""}}
        elif type=='activate':
            data = {'active': values}
        elif type == 'deactivate':
            data = {'active': values}
        else:
            data={'password':values}
        self._get_html()
        self._get_credentials()

        update_endpoint = "%s/api/v1/users.update" % HTML

        admin_data = self._generate_token(rcUsername, rcPassword)

        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': admin_data['Token'],
            'X-User-Id': admin_data['Userid'],

        }
        payload={"userId":userid,"data":data}
       
        res=requests.request("POST", update_endpoint, data=json.dumps(payload),
                         headers=headers)

    def post_msg(self, destination, message="Hi"):
        """ Post message wrapper
        Usage post_message(roomid/channel/username,"message to be sent")
        """

        global rcUsername, rcPassword
        self._get_html()
        self._get_credentials()
        _logger.debug("Post message details received ")
        gentoken = self._generate_token(rcUsername, rcPassword)
        msgheader = {
            'Content-Type': 'application/json',
            'X-Auth-Token': gentoken['Token'],
            'X-User-Id': gentoken['Userid']
        }
        if '#' in destination:
            channel=destination
        elif '@' in destination:
            channel= "@" + (destination).split('@')[0].lower()
        else:
            channel=destination
        payload={ "channel": channel, "text": message}
        postmsg = "%s/api/v1/chat.postMessage" % HTML
        try:

            pm = requests.request("POST", postmsg, headers=msgheader, data=json.dumps(payload))
            _logger.debug("post message passed")
        except:
            _logger.debug("Failed message exception called while sending")

    def get_room_id(self,roomname=None):
        global rcUsername, rcPassword

        gentoken=self._generate_token(rcUsername,rcPassword)
        _logger.debug("\n\nGet room api\n\n")

        room_endpoint = "%s/api/v1/rooms.info?roomName=%s" % (HTML, roomname)

        payload = {
            "roomName": roomname
        }
        roomheader = {

            'X-Auth-Token': gentoken['Token'],
            'X-User-Id':gentoken['Userid']
        }

        roomres = requests.request("GET", room_endpoint, headers=roomheader, data=payload)
        _logger.debug("\n%s %s",roomres,roomres.json())
        roomdata=roomres.json()
        _logger.debug("\nRoom data \n %s %s",room_endpoint,roomdata)
        return(roomdata['room']['_id'])

    def send_message(self,username,roomname="None",msg="Hi"):
        global rcUsername, rcPassword
        self._get_html()
        self._get_credentials()
        message = "%s/api/v1/chat.sendMessage" % HTML
        rid=self.get_room_id(roomname)
        _logger.info("\n\n Send message\n\n")
        gentoken = self._generate_token(rcUsername, rcPassword)
        _logger.debug("\n\n Token:%s",gentoken)
        _logger.debug("\n\n Rid:%s", rid)
        msgheader = {
            'Content-Type': 'application/json',
            'X-Auth-Token': gentoken['Token'],
            'X-User-Id': gentoken['Userid']
        }
        msgpayload = {
            "message": {"rid": rid,
                        "msg": msg}}
        messageres= requests.request("POST", message, headers=msgheader, data=json.dumps(msgpayload))
        _logger.debug("\n\n Token:%s",  messageres.json())
        return messageres.json()

    @api.model
    def _create_collab_user(self,record):
        global rcUsername,rcPassword

        self._get_html()
        self._get_credentials()


        create_endpoint = "%s/api/v1/users.create" % HTML

        admin_data = self._generate_token(rcUsername, rcPassword)

        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': admin_data['Token'],
           'X-User-Id': admin_data['Userid'],

        }
 
        if not record.password:
            record.password = PASS_WORD
        approval = self.env['user.approval']
        pwd=approval.decrypt(record.password)

        payload = "{\n    \"email\": \"%s\",\n  \"password\": \"%s\",\n    \"name\": \"%s\",\n    \"username\": \"%s\"\n}" % (
            record.email, pwd, record.name, (record.email).split('@')[0].lower())

        try:
            collab_create_response = requests.request("POST", create_endpoint, data=payload, headers=headers)

        except Exception as e:
            raise ValidationError(_("Error , Contact admin \n %s ", e))
        ccres = collab_create_response.json()
        _logger.debug("\n\n Create response %s",ccres)
        if ccres['success']:
            _logger.info("Ccres:%s", ccres)
            createdUserid = ccres['user']['_id']
            self._user_update(record,createdUserid,type='profile')
        if ccres['success'] == False:

            raise ValidationError(
                _("Conflicting user exist in collab for `%s` user cleanup and try again .\n. Possible error also %s" % (record.name,ccres['error']))
            )
            return (None)

    def generate_report(self,call_no):
        global rcUsername, rcPassword,HTML

        self._get_html()
        _logger.info("\n>>>genereate report")
        report_getpdf_endpoint = "%s/api/v1/report.getpdf" % HTML
        params="call_no="+call_no
        res=requests.get(report_getpdf_endpoint,params=params)

        return res.json()

    def delete_report(self, call_no):
        global rcUsername, rcPassword, HTML

        self._get_html()
        _logger.info("\n>>>delete report")
        report_getpdf_endpoint = "%s/api/v1/report.deletepdf" % HTML
        params = "call_no=" + call_no
        res = requests.get(report_getpdf_endpoint, params=params)

        return res.json()


    def _generate_token(self, username, password):
        # Create Auth token using login api in collab
        _logger.debug("in generate token")
        self._get_html()
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
        _logger.debug(login_data)
        if login_data['status'] == 'success':
            return ({'Token': login_data['data']['authToken'], 'Userid': login_data['data']['userId']})
        else:
            _logger.error(login_data.get('errors'))
            tokenvalue = 'Null %s' % login_data
            return ({'Token': tokenvalue})


    def autoclose(self):
        cms=self.env['cms.info.model']
        calls = cms.search([('call_status', '=', 'Completed')])
        for i in calls:
            self.call_status = 'Closed'

    def jsondump(self,data):
        return(json.dumps(data))

