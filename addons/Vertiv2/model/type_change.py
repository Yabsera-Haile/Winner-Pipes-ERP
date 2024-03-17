from odoo import fields, models, api
from odoo import _
from datetime import datetime
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class call_type_change_request_log(models.Model):
    _name = "change.request"
    _description = "Call type change request log"
    _rec_name = "call_no"

    call_id = fields.Many2one('cms.info.model')
    call_no = fields.Char(related='call_id.call_no', store=1)
    customer_name=fields.Char(related='call_id.customer_name',store=1)
    inital_call_type = fields.Char()
    change_call_type = fields.Char()
    request_at_date=fields.Datetime()
    requested_by=fields.Many2one()
    status=fields.Char()
    approved_at_date = fields.Datetime()
    approved_by = fields.Char()
    request_notes=fields.Char()

    # On approve button
    def buttonClickEvent(self):
        call = self.env['cms.info.model']

        callnumber = call.search([('call_no', '=', self.call_no)], limit=1)
        engineerId = callnumber.engineerId
        teamleadId = engineerId.parent_id
        context = self._context
        current_uid = context.get('uid')
        User = self.env['res.users']
        current_user = User.browse(current_uid)
        current_role = current_user.employee_id.role
        teamlead_role=engineerId.parent_id.role
        if teamlead_role=='om':
            managerId = teamleadId
            manager_user_id = managerId.user_id
        else:
            managerId = teamleadId.parent_id
            manager_user_id = managerId.user_id
   
        # check for manager role
        if not (current_role == 'tl'  or current_role == 'om' or current_role == 'ad'):
            raise ValidationError(
                _("You should be Operation manager or Team lead to approve , Contact admin")
            )
            return

        # if not (manager_user_id == current_user or current_role == 'ad'):
        #     raise ValidationError(
        #         _("You are not authorised to approve other territory calls")
        #     )
        #
        #     return

        if self.change_call_type:
            new_call_type = self.change_call_type
            s = callnumber.update(
                {'call_type': new_call_type, 'change_call_type': False, 'change_call_type_notes': False})
            self.status = "Approved"
            self.approved_by = self.env.user.name
            self.approved_at_date = fields.datetime.now()
        return

    # On Reject button
    def buttonClickEvent2(self):
        call = self.env['cms.info.model']
        callnumber = call.search([('call_no', '=', self.call_no)], limit=1)
        engineerId = callnumber.engineerId
        teamleadId = engineerId.parent_id
        teamlead_role = engineerId.parent_id.role
        if teamlead_role == 'om':
            managerId = teamleadId
            manager_user_id = managerId.user_id
        else:
            managerId = teamleadId.parent_id
            manager_user_id = managerId.user_id

        context = self._context
        current_uid = context.get('uid')
        User = self.env['res.users']
        current_user = User.browse(current_uid)
        current_role = current_user.employee_id.role
        # check for manager role
        if not (current_role == 'tl' or current_role == 'om' or current_role == 'ad'):
            raise ValidationError(
                _("You should be Operation manager or Team lead to Approve/Reject , Contact admin")
            )
            return

        # if not (manager_user_id == current_user or current_role == 'ad'):
        #     raise ValidationError(
        #         _("You are not authorised to Approve/Reject other territory calls")
        #     )
        #
        #     return

        s = callnumber.update({'change_call_type': False, 'change_call_type_notes': False})
        self.status = "Rejected"
        self.approved_by = self.env.user.name
        self.approved_at_date = fields.datetime.now()
        return
