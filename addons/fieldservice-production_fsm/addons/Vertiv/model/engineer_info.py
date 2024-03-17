from odoo import fields, models, api,exceptions, _
from datetime import datetime
from odoo.tools import format_datetime
from odoo.exceptions import ValidationError
import requests
import json

import logging

# import os.path
from odoo.modules.module import get_module_resource
import base64
import os

_logger = logging.getLogger(__name__)

HTML = ''
PASS_WORD = ''



class EmployeeInfo(models.Model):
    _inherit = "hr.employee"
    _description = "FSM employee Info "

    # employeenumber = fields.Char('Employee Number')
    # employee_code = fields.Char()
    mobile_phone = fields.Char('Mobile')
    work_phone = fields.Char(invisible="1")
    work_email = fields.Char('Email')
    branch_id = fields.Many2one('branch.info', "Branch")
    work_location = fields.Char(related='branch_id.branch_description', store=True, readonly=False)
    employee_city = fields.Char(related='branch_id.branch_name', string="City", readonly=False, related_sudo=False)
    employee_state = fields.Char('State')
    department_id = fields.Many2one('hr.department', 'Territory',
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    role = fields.Selection([
        ('engineer', 'Engineer'),
        ('tl', 'Team leader'),
        ('om', 'Operations Manager'),
        ('zsm', 'Zonal Manager'),
        ('se', 'Technical Support'),
        ('wm', 'Warehouse Manager'),
        ('ad', 'Admin'),
        ('sem', 'Tech Support Manager'),
        ('to_define', 'To Define')], default='engineer', store=1)


    product_group = fields.Selection([
        ('power', "Power"),
        ('dcps', "DCPS"),
        ('dpg', 'DPG'),
        ('smart', 'SMART Solution'),
        ('monitoring', 'Monitoring')
    ], "Product group")
    is_approved = fields.Boolean("Is Approved", tracking=True)
    approvedby = fields.Many2one('hr.employee', 'Approved by', store=True, readonly=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    approveddate = fields.Date("Approved date", readonly=True)
    geolocationlat = fields.Char()
    geolocationlong = fields.Char()
    geoupdatedtime = fields.Datetime()
    token = fields.Char("Token")
    wh_state=fields.Char("Warehouse State")
    user_avatar_image_url = fields.Char("Image Avatar Url",compute="compute_user_avatar_url")
    # avatar_image_new = fields.Binary("Image Avatar bool",compute="compute_user_avatar_image")
    # collab_user = fields.Char("Collab user Id")

    # @api.depends('role')
    # def onchange_role(self):
    #     _logger.info('set role')
    #     self.set_role(self.role)

    def compute_user_avatar_url(self):
        for rec in self:
            Parameters = self.env['ir.config_parameter'].sudo()
            url = Parameters.get_param('vertiv_collab_reference_id')
            if rec.work_email:
                user_name = rec.work_email.split('@')[0]
                rec.user_avatar_image_url = url + '/avatar/' + user_name
            else:
                rec.user_avatar_image_url = ''

    # def compute_user_avatar_image(self):
    #     for rec in self:
    #         rec.avatar_image_new = False
    #         c = self.env['collab']
    #         svg_data = f"""{c._get_user_avatar(self.env.user.login)}"""
    #         print("......svg_data......",svg_data)
    #         if svg_data:
    #             svg2png(bytestring=svg_data, write_to='project/mongrov/latest/fieldservice/addons/Vertiv/static/src/employee_avatar_image.png')
    #             image_path = get_module_resource('Vertiv', 'static/src', 'employee_avatar_image.png')
    #             image = base64.b64encode(open(image_path, 'rb').read())
    #             print("..........image........",image)
    #             rec.avatar_image_new = image
    #             rec.user_id.image_1920 = image

    def change_role(self):
        wizard_id = self.env['hr.role.change'].create({'list_id': self.id, 'role': self.role})
        return {
            'name': _('Edit'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.role.change',
            'res_id': wizard_id.id,
            'target': 'new',
        }



class ldap_engg_info(models.Model):
    _name = "ldap"
    _description = "FSM LDAP list"

    ADDisplayName = fields.Char('Display Name')
    ADUserid = fields.Char('User Id')
    ADEmailid = fields.Char('Email')
    ADIsActive = fields.Char('Is Active')
    ADMobileNumber = fields.Char('Mobile')
    ADOrganizationName = fields.Char('Org Name')
    ADMgrDisplayName = fields.Char('Manager Name')
    ADMgrEmailid = fields.Char('Manager email')
    ADLocation = fields.Char('Location')
    ADTitle = fields.Char('Title')
    ADDepartment = fields.Char('Department')
    ADFirstName = fields.Char('First Name')
    ADLastName = fields.Char('Last Name')

    @api.model
    def user_activate(self):
        """Method to reactivate removed users"""
        users=self.env['res.users']
        _logger.info('user activate')
        collab = self.env['collab']
        deactivated_users=users.search([('active','=',False)])
        ldap_users=self.env['ldap']
        for i in deactivated_users:

            changed_users=ldap_users.search([('ADEmailid','=',i.login)])
            if changed_users.ADIsActive=='True':

                i.write({'active':True})
                userid, token = collab._get_user_token(changed_users.ADEmailid)
                collab._user_update(True, userid, type='activate')


    @api.model
    def user_deactivate(self):
        """ Method to remove login for AD removed users"""
        users = self.env['res.users']
        ldap_users = self.env['ldap']
        collab = self.env['collab']
        _logger.info('user deactivate')
        query = 'select \"ADEmailid\" from ldap where \"ADIsActive\" = \'False\''
        self.env.cr.execute(query)
        ldap_removed_users = self.env.cr.fetchall()

        for i in ldap_removed_users:
            changed_users = users.search(['&', ('login', '=', i[0]), ('active', '=', True)])
            _logger.info(changed_users)

            if len(changed_users) > 0:
                changed_users.write({'active': False})
                userid, token = collab._get_user_token(changed_users.login)
                collab._user_update(False, userid, type='deactivate')



class cms_employee(models.Model):
    _name = "cms.employee"
    _description = "CMS Employee list"

    employee_code = fields.Char('Employee Code')
    employee_name = fields.Char('Name')
    designation = fields.Char('Designation')
    sr_group = fields.Char('SR Group')
    email = fields.Char('Email')
    mob_no = fields.Char('Mobile')


class hrRolechange(models.TransientModel):
    _name='hr.role.change'
    _description='Change role'

    list_id= fields.Many2one('hr.employee')
    work_email=fields.Char(related='list_id.work_email')
    role = fields.Selection([
        ('engineer', 'Engineer'),
        ('tl', 'Team leader'),
        ('om', 'Operations Manager'),
        ('zsm', 'Zonal Manager'),
        ('se', 'Technical Support'),
        ('wm', 'Warehouse Manager'),
        ('sem', 'Tech Support Manager'),
        ('ad', 'Admin'),('to_define','to_define')], default='engineer', store=1)

    def change_role(self):
        self.list_id.with_context({'change_role': 1}).change_role()
        engineerlist=self.list_id
        engineerlist.role =self.role
        self.set_role(self.role)

    def set_role(self, role):
        _logger.info('\nset role')
        _logger.info(role)
        emp_role = (role).strip()
        users = self.env['res.users']
        groups = self.env['res.groups']
        res = users.search([('login', '=', self.work_email)])

        if emp_role == "zsm":
            group = self.env.ref('Vertiv.zone_group')
            oprgroup = self.env.ref('Vertiv.opr_group')
            empgroup = self.env.ref('hr.group_hr_user')
            admingroup = self.env.ref('base.group_erp_manager')
            res.sudo().write({'groups_id': [(6, 0, [group.id, oprgroup.id, empgroup.id, admingroup.id])]})
            role_value = 'zsm'

        elif emp_role == "tl":
            group = self.env.ref('Vertiv.tl_group')
            eng_group = self.env.ref('Vertiv.engineer_group')
            base_group = self.env.ref('base.group_user')
            res.sudo().write({'groups_id': [(6, 0, [group.id, base_group.id])]})
            role_value = 'tl'

        elif emp_role == "om":
            group = self.env.ref('Vertiv.opr_group')
            empgroup = self.env.ref('hr.group_hr_user')
            admingroup = self.env.ref('base.group_erp_manager')
            allowexport=self.env.ref('base.group_allow_export')
            res.sudo().write({'groups_id': [(6, 0, [group.id, empgroup.id, admingroup.id,allowexport.id])]})
            role_value = 'om'

        elif emp_role == "se":
            group = self.env.ref('Vertiv.technical_support')
            base_group = self.env.ref('base.group_user')
            res.sudo().write({'groups_id': [(6, 0, [group.id, base_group.id])]})
            role_value = 'se'
        elif emp_role == "sem":
            group = self.env.ref('Vertiv.tec_support_manager_group')
            group.sudo().write({'users': [(4, res.id)]})
            role_value = 'sem'
        elif emp_role == "wm":
            group = self.env.ref('Vertiv.warehouse_group')
            base_group = self.env.ref('base.group_user')
            res.sudo().write({'groups_id': [(6, 0, [group.id, base_group.id])]})
            role_value = 'wm'

        elif emp_role == "ad":
            group = self.env.ref('Vertiv.vertiv_admin_group')
            empgroup = self.env.ref('hr.group_hr_user')
            admingroup = self.env.ref('base.group_erp_manager')
            allowexport = self.env.ref('base.group_allow_export')
            res.sudo().write({'groups_id': [(6, 0, [group.id, empgroup.id, allowexport.id,admingroup.id])]})
            role_value = 'ad'

        else:
            group = self.env.ref('Vertiv.engineer_group')
            base_group = self.env.ref('base.group_user')
            res.sudo().write({'groups_id': [(6, 0, [group.id, base_group.id])]})
            role_value = 'engineer'
