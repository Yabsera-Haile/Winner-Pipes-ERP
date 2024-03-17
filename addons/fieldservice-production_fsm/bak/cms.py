from odoo import fields, models, api
from datetime import datetime, timedelta
import logging
import random
import threading
from datetime import date, datetime, timedelta
from psycopg2 import sql

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.osv import expression
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError
from odoo.addons.phone_validation.tools import phone_validation
from collections import OrderedDict, defaultdict

_logger = logging.getLogger(__name__)

ENGINEER_FIELDS_TO_SYNC = [
    'call_no',
    'call_schedule_starttime',
    'call_schedule_endtime',
    'customer_name',
]


class call_stage(models.Model):
    _name = "call.stage"
    _description = "call stages"
    _rec_name = "stage"

    stage = fields.Char('Stage')


class cms_info(models.Model):
    _name = "cms.info.model"
    _description = "call details"
    _rec_name = 'call_no'

    call_no = fields.Char("Call No")
    call_type = fields.Char("Call Type")
    change_call_type = fields.Char("New call type")

    @api.onchange('change_call_type')
    def onchange_method(self):
        if self.change_call_type:
            change_call_no = self.call_no
            old_call_type = self.call_type
            new_call_type = self.change_call_type
            new_call_notes = self.change_call_type_notes

            changelog = self.env['change.request']
            newrecord = changelog.create(
                {'call_no': change_call_no, 'inital_call_type': old_call_type, 'change_call_type': new_call_type,
                 'request_notes': new_call_notes})
            return

    change_call_type_notes = fields.Text('Call type notes')
    call_severity = fields.Char("Severity")
    call_status = fields.Selection([
        ('Unassigned', 'Unassigned'),
        ('Open', 'Open'),
        ('Accepted', 'Accepted'),
        ('Working', 'Working'),
        ('Attended', 'Attended'),
        ('Completed', 'Completed'),
        ('Closed', 'Closed')], store=1, default='Open', tracking=True)
    response_time = fields.Float('Response time')
    tat = fields.Float('TAT')
    call_log_date = fields.Datetime('Call Log Date')
    call_incident_date = fields.Datetime('Call Incident Date')
    call_assignment_date = fields.Datetime('Call Assigned Date')
    call_accepted_date = fields.Datetime('Call Accepted Date')
    call_sla = fields.Integer(compute="checksla")

    @api.depends('call_log_date')
    @api.model
    def checksla(self):
        # todo default value added check for logic. if passes will all ways be low priority
        for calls in self:
            calls.call_sla = 0
            if calls.call_log_date == False or type(calls.call_log_date) == None:
                calls.call_sla = 2
                print("Check 1 Call log date:", calls.call_log_date)
            elapsedtime = 0
            if calls.call_status != "Completed" or calls.call_status != "Closed":
                productmodel = calls.product_model
                group = calls.product_group
                distance = calls.customer_distance_category
                today = fields.Datetime.to_datetime(fields.Datetime.now())
                calltime = fields.Datetime.to_datetime(calls.call_log_date)
                if calltime == False or calltime == None:
                    calltime = fields.Datetime.to_datetime(fields.Datetime.now())
                    calls.call_sla = 2
                    return
                elapsedtime = today - calltime
                sla_members = self.env['sla.master']
                slamemberslist = sla_members.search(
                    ['&', ('product_group', 'in', group), ('distance_category', 'in', distance)])
                elapsedtime = float(elapsedtime.days) * 24 + (float(elapsedtime.seconds) / 3600)
                if (len(slamemberslist)) < 1:
                    calls.call_sla = 2
                    return
                for i in slamemberslist:
                    if elapsedtime <= (i.target_response_hrs):
                        calls.call_sla = 0
                    elif elapsedtime <= i.target_response_hrs + 2:
                        calls.call_sla = 1
                    else:
                        calls.call_sla = 2
            else:
                calls.call_sla = 0
                return

    call_planned_start_date = fields.Datetime("Planned Start Date")
    call_planned_end_date = fields.Datetime("Planned End date")
    call_schedule_startdate = fields.Datetime("Schedule Start Date")
    call_schedule_enddate = fields.Datetime("Schedule End Date")
    call_actual_startdate = fields.Datetime("Actual Start Date")
    call_actual_enddate = fields.Datetime("Actual End Date")

    # @api.depends("call_actual_startdate", "call_actual_enddate","call_log_date")
    # def _compute_duration(self):
    #     duration = 0.0
    #     for rec in self:
    #         if rec.call_actual_startdate and rec.call_actual_enddate and rec.call_log_date:
    #             start = fields.Datetime.from_string(rec.call_log_date)
    #             end = fields.Datetime.from_string(rec.call_actual_startdate)
    #             delta = end - start
    #             duration = delta.total_seconds() / 3600
    #     rec.response_time = duration
    #
    # @api.depends("call_actual_startdate", "call_actual_enddate", "call_log_date")
    # def _tat_compute_duration(self):
    #     duration = 0.0
    #     for rec in self:
    #         if rec.call_actual_startdate and rec.call_actual_enddate and rec.call_log_date:
    #             start = fields.Datetime.from_string(rec.call_log_date)
    #             end = fields.Datetime.from_string(rec.call_actual_enddate)
    #             delta = end - start
    #             duration = delta.total_seconds() / 3600
    #     self.tat = duration

    call_attended_date = fields.Datetime("Attended Date")
    call_closed_date = fields.Datetime("Call Close Date")
    sr_group = fields.Char("Sr Group")
    sr_owner = fields.Char("Sr Owner")
    zone = fields.Char("Zone")
    service_channel = fields.Char('Service channel')
    engineerId = fields.Many2one("hr.employee", "Engineer")
    engineeruserid = fields.Char(related='engineerId.user_id.name')
    teamlead = fields.Char(related='engineerId.parent_id.name')
    enpi_eng_id = fields.Char()
    call_engineer_mobilenumber = fields.Char()
    fault_reported = fields.Char("Fault reported")
    alarmcodeid = fields.Char("Alarm code Id")
    chat_iframe = fields.Html("Notes", sanitize=False, compute='get_html')

    def get_html(self):
        passdb = self.env['pass.token']
        current_user = self.env.user.email
        passrec = passdb.search([('email', '=', current_user)])
        for record in self:
            record.chat_iframe = f'<iframe src="https://vertiv.mongrov.net/group/{self.call_no.lower()}?layout=embedded" height="400px" width="100%"/iframe>'

    support_iframe = fields.Html("Support", sanitize=False, compute='get_html2')

    def get_html2(self):
        for record in self:
            record.support_iframe = f'<iframe src="https://vertiv.mongrov.net/group/{self.call_no.lower()}_{self.product_group.lower()}?layout=embedded" height="400px" width="100%""/iframe>'

    customer_account_no = fields.Char("Customer Account Number")
    customer_name = fields.Char("Customer Name")
    customer_address1 = fields.Char("Address1")
    customer_address2 = fields.Char("Address2")
    customer_address3 = fields.Char("Address3")
    customer_site_address = fields.Char("Site Address")
    customer_contact_person = fields.Char("Contact person")
    customer_contact_mobile = fields.Char("Contact number")
    customer_distance_category = fields.Char('Distance category')
    customer_contact_landline = fields.Char("Contact landline")
    customer_site_contactno = fields.Char('Site contact no')
    customer_email = fields.Char("Customer Email")
    customer_city = fields.Char("City")
    customer_state = fields.Char("State")
    customer_pincode = fields.Char("Pincode")
    customer_latitude = fields.Char()
    customer_longitude = fields.Char()
    product_group = fields.Char()
    product_code = fields.Char('Product code')
    product_model = fields.Char('Model')
    product_rating = fields.Char('Rating')
    product_serialno = fields.Char('Serial Number')
    product_installation_date = fields.Char()
    product_smartsubcat = fields.Char()
    cms_type = fields.Char('CMS Type')
    warranty_status = fields.Char('Warranty Status')
    warranty_aspercustomer = fields.Char('Warranty as per customer')
    contract_no = fields.Char('Contract number')
    contract_start_date = fields.Datetime('Contract start date')
    contract_end_date = fields.Datetime('Contract end date')
    contract_coverage_description = fields.Char('Contract coverage')
    contract_status = fields.Char('Contract status')
    call_activity = fields.Char()
    call_description = fields.Text()
    problem_code_description = fields.Char()
    resolution_code_description = fields.Char()
    reason_of_pending = fields.Char()
    problem_code_description_id = fields.Many2one("lov.master", string="Problem code",
                                                  domain="[('lov_name','=','Problem Code Desc')]")
    resolution_code_description_id = fields.Many2one("lov.master", string="Resolution code",
                                                     domain="[('lov_name','=','Resolution Code')]")
    reason_of_pending_id = fields.Many2one("lov.master", string="Reason of pending",
                                           domain="[('lov_name','=','Reason of pending')]")

    resolution_summary = fields.Char("Resolution Summary")
    cancellation_reason = fields.Char()
    task_no = fields.Integer()
    task_subject = fields.Char()
    task_owner_type = fields.Char()
    task_assignee_type = fields.Char()
    sp_eng_name = fields.Char()
    reschedule_reason = fields.Char()
    field_service_report_no = fields.Char()
    call_closed_approvedby = fields.Char()
    no_of_visits = fields.Integer(compute='_compute_visit_count')

    def _compute_visit_count(self):
        for rec in self:
            self.no_of_visits = len(rec.call_timesheet_ids.filtered(lambda r: r.punch_category == 'Callpunchin'))

    distance_category = fields.Char()
    status_of_call = fields.Char()
    call_punch_time = fields.Float()
    call_face_time = fields.Float()
    params = fields.Text()

    call_material_ids = fields.One2many('call.material.activities', 'call_id')
    call_workbench_ids = fields.One2many('workbench.info', 'call_id')
    # call_facetime_ids = fields.One2many('equipment.facetime.info', 'call_id')
    call_timesheet_ids = fields.One2many('call.timesheet.info', 'call_id')
    call_partorder_ids = fields.One2many('call.material.orders', 'call_id')
    call_schedule_id = fields.One2many('calendar.event', 'call_id')
    call_time_ids = fields.One2many('call.timesheet.info', 'call_id', compute='_get_otherevents_ids')
    call_labour_ids = fields.One2many('call.timesheet.info', 'call_id', compute='_get_labourevents_ids')

    def _get_labourevents_ids(self):
        self.call_labour_ids = self.call_timesheet_ids.search(
            ['&', ('punch_category', '=', 'Labourtime'), ('call_id', '=', self.id)])

    def _get_otherevents_ids(self):
        self.call_time_ids = self.call_timesheet_ids.search(
            ['&', ('punch_category', '!=', 'Labourtime'), ('call_id', '=', self.id)])

    # def _creation_subtype(self) -> object:
    #     return self.env.ref('vertiv.mt_create')
    #
    # def _track_subtype(self, init_values):
    #     self.ensure_one()
    #     if 'call_status' in init_values:
    #         return 'vertiv.mt_state_change'
    #     return super(cms_info,self)._track_subtype(init_values)

    @api.onchange('engineerId')
    def engineerchange(self):
        self.call_status = 'Open'
        return

        # test_record = self.env['hr.employee'].search(['name','=','Manikandhanathan'])
        # now = datetime.now()
        # test_user = self.env['res.users'].search([('login', '=', 'mani@mongrov.com')])
        # test_name, test_description, test_description2 = self.call_no, self.call_type, 'NotTest'
        # test_note, test_note2 = '<p>Test-Description</p>', '<p>NotTest</p>'
        #
        # # create using default_* keys
        # test_event = self.env['calendar.event'].with_user(self.engineerId.user_id.id).create({
        #     'name': self.call_no,
        #     'description': self.call_type + "\n" + self.fault_reported + "\n" + self.customer_name,
        #     'start': fields.Datetime.to_string(self.call_schedule_startdate),
        #     'stop': fields.Datetime.to_string(self.call_schedule_enddate),
        #     'user_id': self.engineerId.user_id.id,
        # })

    def ensure_one(self):
        return self

    # actions
    def toggle_active(self):
        return self

    def buttonClickEvent(self):
        self.call_status = 'Closed'
        self.call_closed_approvedby = self.env.uid
        return

    def sla_value(self):
        return


class collab_view(models.Model):
    _name = "collab.view"
    _description = "Power group link "

    power_iframe = fields.Html("Power", sanitize=False)
    dcps_iframe = fields.Html("DCPS", sanitize=False)
    dpg_iframe = fields.Html("DPG", sanitize=False)


class metabase_view(models.Model):
    _name = "metabase.view"
    _description = "Reprots"

    metabase_iframe = fields.Html()
    equipment_tl_iframe = fields.Html("Notes", sanitize=False, compute='get_html')

    def get_html(self):
        for record in self:
            record.chat_iframe = f'<iframe src="https://dash.in.mongrov.com/public/dashboard/509c3405-7c04-4d8b-af05-5cfbd88446f0" frameborder="0"     width="100%"     height="600"></iframe>'


class Passtoken(models.Model):
    _name = "pass.token"
    _rec_name = "email"

    email = fields.Char()
    passtoken = fields.Char()