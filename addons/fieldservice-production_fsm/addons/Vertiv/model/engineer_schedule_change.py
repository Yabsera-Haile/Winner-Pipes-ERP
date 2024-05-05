from odoo import fields, models, api
from datetime import datetime, timedelta,date
import logging

_logger = logging.getLogger(__name__)

class EngineerScheduleEdit(models.TransientModel):
    _name = 'schedule.edit'
    _description = 'Edit Schedule change plan for engineer'

    call_id = fields.Many2one('cms.info.model')
 
    call_schedule_startdate = fields.Datetime("Schedule Start Date")
    call_schedule_enddate = fields.Datetime("Schedule End Date")
    call_planned_start_date = fields.Datetime("Planned Start Date")
    call_planned_end_date = fields.Datetime("Planned End date")

    def edit_schedule_change(self):
        self.call_id.with_context({'edit_schedule_change': 1}).edit_schedule()
        call=self.call_id
        call.call_schedule_startdate=self.call_schedule_startdate
        call.call_schedule_enddate=self.call_schedule_enddate
        call.call_planned_start_date = self.call_planned_start_date
        call.call_planned_end_date = self.call_planned_end_date
        
class Rolechange(models.TransientModel):
    _name='role.change'
    _description='Change role'

    list_id= fields.Many2one('user.approval')
    role = fields.Selection([
        ('Engineer', 'Engineer'),
        ('Team leader', 'Team leader'),
        ('Operations Manager', 'Operations Manager'),
        ('Territory Manager', 'Territory Manager'),
        ('Zonal Manager', 'Zonal Manager'),
        ('Technical Support', 'Technical Support'),
        ('Warehouse Manager', 'Warehouse Manager'),
        ('Tech Support Manager', 'Tech Support Manager'),
      ], store=1)

    def change_role(self):
        self.list_id.with_context({'change_role': 1}).change_role()
        engineerlist=self.list_id
        engineerlist.role =dict(self._fields['role'].selection).get(self.role)

class ChangeEngineer(models.TransientModel):
    _name = 'engineer.change'
    _description = 'Change Engineer'

    call_id = fields.Many2one('cms.info.model')
    engineer_id=fields.Many2one("hr.employee", "Engineer")
    call_status = fields.Selection([
        ('Unassigned', 'Unassigned'),
        ('Open', 'Open'),
        ('Accepted', 'Accepted'),
        ('Working', 'Working'),
        ('Attended', 'Attended'),
        ('Completed', 'Completed'),
        ('Closed', 'Closed')], store=1, default='Open')
    customer_email = fields.Char()
    customer_contact_person = fields.Char("Contact person")
    customer_contact_mobile=fields.Char()
    distance_category=fields.Char()
    sr_owner = fields.Many2one('cms.managers',"Sr Owner")
    sr_group = fields.Many2one('branch.info',"Sr Group")
    distance_category_values=fields.Many2one("lov.master", string="New Distance Category",context="{'lov_value':distance_category}",
                                                 domain="[('lov_name','=','Distance Category')]", store=1)

    resolution_summary = fields.Char("Resolution Summary")
    customer_address1 = fields.Char("Address1")
    customer_address2 = fields.Char("Address2")
    customer_address3 = fields.Char("Address3")
    call_activity = fields.Char("Activity Note")
    product_model = fields.Many2one('product.model','Model')
    product_rating = fields.Many2one('product.rating','Rating')
    customer_city = fields.Char("City")
    customer_state = fields.Char("State")
    reason_of_pending_id = fields.Many2one("lov.master", string="Reason of pending",domain="[('lov_name','=','Reason of pending')]", store=1)

    def _default_pcd(self):
        s = self.env['lov.master'].search([('lov_value', '=', self.problem_code_description)], limit=1)
        _logger.info("Lov vlu %s", s)
        return

    # problem_code_description_id = fields.Many2one("lov.master", string="New Problem code",
    #                                               domain="[('lov_name','=','Problem Code Desc')]", store=1)
    problem_code_description_id = fields.Many2one("cms.problem.setup", string="New Problem code")
    resolutions_code_description_id = fields.Many2one("cms.problem.setup", string="New Resolution code")
    problem_code_description = fields.Char()
    resolution_code_description = fields.Char()

    @api.onchange('product_model')
    def onchange_product_model(self):
        for rec in self:
            if rec.product_model:
                rec.product_rating = False
            #     return {'domain': {'product_rating': [('model', '=', rec.product_model.model)]}}
            # return {'domain': {'product_rating': [('model', '=', '')]}}

    @api.model
    def _default_value(self):
        return self.env['lov.master'].search([('lov_name','=',self.distance_category)], limit=1)





    def change_engineer(self):
        self.call_id.with_context({'change_engineer': 1}).change_engineer()

        call = self.call_id
        call.engineerId = self.engineer_id
        call.call_status=self.call_status
        call.customer_email = self.customer_email
        call.customer_contact_person = self.customer_contact_person
        call.customer_contact_mobile=self.customer_contact_mobile
        call.customer_distance_category=self.distance_category if self.distance_category_values.lov_value==False else self.distance_category_values.lov_value
        call.sr_owner = self.sr_owner.resource_name
        call.sr_group = self.sr_group.branch_name
        # call.problem_code_description = self.problem_code_description if self.problem_code_description_id.lov_value==False else self.problem_code_description_id.lov_value
        call.problem_code_description = self.problem_code_description if self.problem_code_description_id.problem_type==False else self.problem_code_description_id.problem_type
        call.resolution_code_description = self.resolution_code_description if self.resolutions_code_description_id.resolution_type==False else self.resolutions_code_description_id.resolution_type
        call.resolution_summary = self.resolution_summary
        call.customer_address1 = self.customer_address1
        call.customer_address2 = self.customer_address2
        call.customer_address3 = self.customer_address3
        call.call_activity = self.call_activity
        model = str(self.product_model.product_group.upper() if self.product_model.product_group else '') + '.' + str(self.product_model.model.upper() if self.product_model.model else '')
        call.product_model = model
        call.product_rating = self.product_rating.rating
        call.reason_of_pending = self.reason_of_pending_id.lov_value


class ApproveCall(models.TransientModel):
    _name = 'approve.call'
    _description = 'Approve Call'

    call_id = fields.Many2one('cms.info.model')
    call_status = fields.Selection([
        ('Unassigned', 'Unassigned'),
        ('Open', 'Open'),
        ('Accepted', 'Accepted'),
        ('Working', 'Working'),
        ('Attended', 'Attended'),
        ('Completed', 'Completed'),
        ('Closed', 'Closed')], store=1, default='Open')


    def change_status(self):
        self.call_id.with_context({'change_status': 1}).change_status()
    
        call = self.call_id
        call.engineerId = self.engineer_id

class CancelCall(models.TransientModel):
    _name = 'cancel.call'
    _description = 'Cancel Call'

    call_id = fields.Many2one('cms.info.model')
    call_status = fields.Selection([
        ('Cancelled', 'Cancelled'),
        ('Open', 'Open')
      ], store=1, default='Cancelled')
    cancellation_reason = fields.Char()
    cancelled_by = fields.Many2one('res.users', store=1)
    engineer_id=fields.Many2one("hr.employee", "Engineer")

    def cancel_call(self):
        self.call_id.with_context({'cancel_cal': 1}).cancel_call()

        call = self.call_id
        call.engineerId = False
        call.call_status=self.call_status
        call.cancellation_reason=self.cancellation_reason
        call.cancelled_by = self.env.uid


