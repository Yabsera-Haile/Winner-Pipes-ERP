from odoo import fields, models, api
from odoo import _
from odoo import tools
from datetime import datetime
from odoo.exceptions import ValidationError
import requests
import json
import os
import sys
from sys import path, argv
from hashlib import sha256
import logging
from . import _var_data
_logger = logging.getLogger(__name__)
import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad

KEY=''

HTML = ''
TOKEN=""
rcUsername = ''
rcPassword =  ''

PASS_WORD = ''
USER_PRIVATE_FIELDS = ['password','verification_code']


import decorator
import passlib.context



class employee_approval(models.Model):
    _name = "user.approval"
    _description = "Engineer approval waiting list"

    name = fields.Char('Employee Name')
    email = fields.Char('Email',groups="Vertiv.vertiv_admin_group,Vertiv.opr_group,Vertiv.user_register_group,Vertiv.engineer_group")
    mobile = fields.Char('Mobile Number')
    is_mobile_verified = fields.Boolean('Mobile Verified')
    role = fields.Char('Role')
    password = fields.Char(inverse='_encrypt', copy=False,groups="Vertiv.vertiv_admin_group,Vertiv.tl_group,Vertiv.opr_group,Vertiv.user_register_group")
    manager = fields.Char('Manager Name')
    title = fields.Char('Title')
    product_group = fields.Char('Product Group')
    city = fields.Char('City')
    state = fields.Char('State')
    branch = fields.Char('Branch')
    is_approved = fields.Boolean('Approved')
    approvedby = fields.Char(readonly=True)
    approveddate = fields.Date(readonly=True)
    requestdate = fields.Date(readonly=True, invisible="1")
    is_verified = fields.Boolean('Verified')
    verification_code = fields.Char(inverse="_encryptcode",string='Verification Code',groups="Vertiv.vertiv_admin_group,Vertiv.opr_group,Vertiv.tl_group, Vertiv.user_register_group")
    is_profile_updated = fields.Boolean('Profile Updated')
    collab_user_create=fields.Boolean()
    hr_user_created=fields.Boolean()
    login_user_created=fields.Boolean()
    # newpass=fields.Char(compute=_encrypt)

    # User can read a few of his own fields
    SELF_READABLE_FIELDS = ['email','is_profile_updated', 'is_verified', 'is_mobile_verified', 'is_approved']
    SELF_READABLE_FIELDS1 = ['email', 'is_verified']
    SELF_READABLE_FIELDS3 = ['email','is_approved']
    SELF_READABLE_FIELDS2 = ['name','role','manager','title','mobile','state','product_group','city','branch' ,'email', 'is_profile_updated', 'is_verified', 'is_mobile_verified', 'is_approved']
    SELF_WRITABLE_FIELDS = ['email',  'is_verified', 'verification_code']
    SELF_WRITABLE_FIELDS2 = ['email','mobile', 'role','is_mobile_verified','is_profile_updated', 'is_verified', 'verification_code']
    SELF_WRITABLE_FIELDS3=['email',  'is_verified', 'verification_code']

    # @api.onchange('role_selection')
    # def _onchange_role_selection(self):
    #     self.role=self.role_selection
    def on_role_selection_change(self):
        self.role=self.role_selection

    def change_role(self):
        wizard_id = self.env['role.change'].create({'list_id':self.id,'role': self.role})
        return {
            'name': _('Edit'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'role.change',
            'res_id': wizard_id.id,
            'target': 'new',
        }

    @api.onchange('password')
    def _onchange_password(self):
        _logger.info("\n\nChange password called\n\n")
        collab = self.env['collab']
        if (self.is_approved == True):
            User = self.env['res.users']
            target_user = User.search([('login', '=', self.email)])
           
            n = self.password
          
            target = target_user.sudo().write({'password': n})
            userid,token=collab._get_user_token(self.email)
         
            res=collab._user_update(n,userid)
            self.password = False
        else:
            return

    def _onchange_verification_code(self):


        code = self.verification_code
        notify = self.env['notification']
        body = ""
        email = ""
        notification_type = "Email"
        if self.verification_code == False:
            code = ""
        else:
            code = self.verification_code

        if (self.is_verified==False):

            body = "Your OTP is " + code
            notification_type = 'Email'
            email = self.email
        elif (self.mobile and self.is_verified and not (self.is_profile_updated)):
            body = "Your Mobile Verification code is " + code


            notification_type = 'sms'
            email = self.mobile
        elif (self.is_approved):


            body = "Your Login OTP  is " + self.verification_code
            notification_type = 'Email'
            email = self.email
        else:
            body = "Code not generated"
            notification_type = 'Email'
            email = self.email

        subject = "Vertiv Authentication OTP"

        curr_time = datetime.now()
        vals = {'notification_type': notification_type, 'notification_from': 'Vertiv team', 'body': body,
                'subject': subject,
                'notification_to': email, 'sent_time': curr_time}
        s = notify.sudo().create(vals)

        self.verification_code = False

        return


    def _create_res_user(self):


        emailid = self.email
        User = self.env['res.users']
        if not self.password:
            self.password = PASS_WORD
        nwpwd=self.decrypt(self.password)


        res = User.sudo().create({'name': self.name, 'login': self.email, 'email': self.email, 'password': nwpwd,'active':True})

        self.login_user_created=1
        return res

    def _read(self, fields):

        super(employee_approval, self)._read(fields)
        canwrite = self.check_access_rights('write', raise_exception=False)
        if not canwrite and set(USER_PRIVATE_FIELDS).intersection(fields):
            for record in self:
                for f in USER_PRIVATE_FIELDS:
                    try:
                        record._cache[f]
                        record._cache[f] = '********'
                    except Exception:
                        # skip SpecialValue (e.g. for missing record or access right)
                        pass

    
    def read(self, fields=None, load='_classic_read'):


        user_pool = self.env['res.users']
        user = user_pool.browse(self._uid)

        user_register_group=self.env['res.groups'].sudo().search([('name','=','User Regisration Group')])
        is_user_register_group = self.env.user.id in user_register_group.users.ids

        admin_group = self.env['res.groups'].sudo().search([('name', '=', 'Vertiv admin users')])
        is_admin_group = self.env.user.id in user_register_group.users.ids

        for i in self:
            if not(i.is_verified):
                fields = i.SELF_READABLE_FIELDS1 if is_user_register_group else i.SELF_READABLE_FIELDS2
            elif i.is_verified and i.is_approved:
                fields = i.SELF_READABLE_FIELDS3 if is_user_register_group else i.SELF_READABLE_FIELDS2
            else:
                fields = i.SELF_READABLE_FIELDS  if is_user_register_group else i.SELF_READABLE_FIELDS2
            if (is_user_register_group):
                    

                if fields and self == self.env.user:
                    for key in fields:

                        if not (key in self.SELF_READABLE_FIELDS or key.startswith('context_')):
                            break
                    else:
                        # safe fields only, so we read as super-user to bypass access rights
                        self = self.sudo()

        return super(employee_approval, self).read(fields=fields, load=load)

    def _create_hr_employee(self,res):
        """Create hr employee user with the userapproval table data
        If manager user is not available a manager is created with email and assigned to it"""
        emailid = self.email
        User = self.env['res.users']
        Employee = self.env['hr.employee']
        manager_in_hr = Employee.search([('work_email', '=like', self.manager)])


        #check if manager has been already available




        if (manager_in_hr == False):
            raise ValidationError("Manager not in FSM. Manager to be created to proceed...")

        if not (manager_in_hr):
            manager_name_exists = Employee.search([('name', '=like', self.manager)])
            #if manager not available create a manager with email id.

            if not (manager_name_exists):
                manager_in_hr = Employee.create({'name': self.manager})
            else:
                manager_in_hr = manager_name_exists[0]

        emp_role = (self.role).strip()
        token = "N.A"

        if emp_role == "Zonal Manager":
            group = self.env.ref('Vertiv.zone_group')
            oprgroup=self.env.ref('Vertiv.opr_group')
            empgroup = self.env.ref('hr.group_hr_user')
            admingroup = self.env.ref('base.group_erp_manager')
            group.sudo().write({'users': [(4, res.id)]})
            oprgroup.sudo().write({'users': [(4, res.id)]})
            empgroup.sudo().write({'users': [(4, res.id)]})
            admingroup.sudo().write({'users': [(4, res.id)]})
            role_value = 'zsm'
        elif emp_role == "Team Leader":
            group = self.env.ref('Vertiv.tl_group')
            group.sudo().write({'users': [(4, res.id)]})
            role_value = 'tl'
        elif emp_role == "Operations Manager":
            group = self.env.ref('Vertiv.opr_group')
            empgroup = self.env.ref('hr.group_hr_user')
            admingroup = self.env.ref('base.group_erp_manager')
            group.sudo().write({'users': [(4, res.id)]})
            empgroup.sudo().write({'users': [(4, res.id)]})
            admingroup.sudo().write({'users': [(4, res.id)]})
            role_value = 'om'
        elif emp_role == "Technical Support":
            group = self.env.ref('Vertiv.technical_support')
            group.sudo().write({'users': [(4, res.id)]})
            role_value = 'se'
        elif emp_role == "Warehouse Manager":
            group = self.env.ref('Vertiv.warehouse_group')
            group.sudo().write({'users': [(4, res.id)]})
            role_value = 'wm'
        elif emp_role == "Admin":
            group = self.env.ref('Vertiv.vertiv_admin_group')
            empgroup = self.env.ref('hr.group_hr_user')
            admingroup = self.env.ref('base.group_erp_manager')
            group.sudo().write({'users': [(4, res.id)]})
            empgroup.sudo().write({'users': [(4, res.id)]})
            admingroup.sudo().write({'users': [(4, res.id)]})

            role_value = 'ad'
        else:
            group = None
            role_value = 'engineer'
     
        if emp_role != "Engineer":
            if emp_role!='Team Leader':
             
                check_engineer = self.env.ref('Vertiv.engineer_group')
                check_engineer.sudo().write({'users': [(3, res.id)]})



        check_already_create = Employee.search([('name', '=', self.email)], limit=1)

        if not (check_already_create):
            emp_res = Employee.sudo().create(
                {'name': self.name,
                 'user_id': res.id,
                 'parent_id': manager_in_hr.id,
                 "is_approved": True,
                 'mobile_phone': self.mobile,
                 'role': role_value,
                 'job_title': self.title,
                 # 'job_title': ldap.ADTitle,
                 "token": token
                 })
            self.hr_user_created=1
        else:
            emp_res = check_already_create.sudo().write(
                {'name': self.name,
                 'user_id': res.id, 'parent_id': manager_in_hr.id,
                 "is_approved": True,
                 'mobile_phone': self.mobile,
                 'role': role_value,
                 # 'job_title': ldap.ADTitle,
                 'job_title': self.title,
                 "token": token
                 })


    def _get_html(self):
        global TOKEN, HTML
        Parameters = self.env['ir.config_parameter'].sudo()
        HTML = Parameters.get_param('vertiv_collab_reference_id')
        # HTML = tools.config['html']

    def buttonClickEvent(self):

        User = self.env['res.users']
        context = self._context
        current_uid = context.get('uid')
        current_user = User.browse(current_uid)
        current_role = current_user.employee_id.role
        if (self.env.user.has_group('Vertiv.tec_support_manager_group') and self.role == 'Technical Support'):
            pass
        else:
            # check for role
            if not (current_role == 'om' or current_role == 'ad' or current_role == 'zsm' or current_role == 'tl'):
                raise ValidationError(
                    _("You should be Operation manager or Zonal manager or Admin to approve users to join FSM, Contact admin")
                )
                return
            # check for role weightage
            if current_role == 'tl' and (
                    self.role == 'Operations Manager' or self.role == 'Warehouse Manager' or self.role == 'Zonal Manager' or self.role == 'Admin'):
                raise ValidationError(
                    _("Your are not allowed to approve for this role, Contact admin")
                )
                return

            if current_role == 'om' and (
                    self.role == 'Warehouse Manager' or self.role == 'Zonal Manager' or self.role == 'Admin'):
                raise ValidationError(
                    _("Your are not allowed to approve for this role, Contact admin")
                )
                return

            if (self.role == False or self.email == False):
                raise ValidationError("Required fields not set")
                return
        res = self._create_res_user()

        collab = self.env['collab']
        collab._create_collab_user(self)
        self._create_hr_employee(res)

        self.is_approved = True
        self.approveddate = datetime.today()
        self.approvedby = current_user.name

    def ResetProfile(self):
        self.is_profile_updated = False
        self.is_approved = False

    def _encryptcode(self):

        self._onchange_verification_code()
        pwd = self.verification_code
        if pwd != False:
            encrypted = self.encrypt(pwd)
            self.verification_code = encrypted.decode("utf-8", "ignore")

            return
        return
    def _get_key(self):
        global KEY

        folder_found = False
        addons_path = tools.config['addons_path'].split(',')

        for addons_folder in addons_path:
            readme_path = addons_folder + '\\Vertiv'
            _logger.info("\n Userapproval Readme path::%s", readme_path)
            _logger.info("\n OS Path::%s", os.path.dirname(os.path.realpath(__file__)))
            if os.path.isdir(readme_path):
                folder_found = True
                try:
                    f = open(readme_path + '\\fsm.conf', "r")

                    f.close()
                except:
                    raise ValidationError(('Unable to read file at ' + readme_path))
                

                    return
                break

        if not folder_found:
            raise ValidationError("Unable to find  folder ")
          
            # todo to be removed for production

            return
        rcfilepath = os.path.join(readme_path, 'fsm.conf')

        _logger.info("User approval")
        fsmvars = {}
        with open(rcfilepath, "r") as myfile:
            for line in myfile:
                line = line.strip()
                name, var = line.partition("=")[::2]
                fsmvars[name.strip()] = str(var)
        KEY=fsmvars['key']
  
        myfile.close()

    def _encrypt(self):
   
        if self.password==False:
            return
        if self.is_approved:
  
            self._onchange_password()
            return
        pwd=self.password
        if pwd!=False:
            encrypted = self.encrypt(pwd)
            self.password = encrypted.decode("utf-8", "ignore")

            return
        return

    def encrypt(self,raw):
        global KEY
        self._get_key()

        raw = pad(raw.encode(), 16)

        cipher = AES.new(KEY.encode('utf-8'), AES.MODE_ECB)

        return base64.b64encode(cipher.encrypt(raw))

    def decrypt(self, pwd):
        global KEY
        enc = pwd
        self._get_key()
        enc = base64.b64decode(pwd)

        cipher = AES.new(KEY.encode('utf-8'), AES.MODE_ECB)

        decrypted=unpad(cipher.decrypt(enc), 16)

        return(decrypted.decode("utf-8", "ignore"))
    
   
    
    