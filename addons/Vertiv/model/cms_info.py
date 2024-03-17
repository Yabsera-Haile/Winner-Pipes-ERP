from odoo import fields, models, api
from datetime import datetime, timedelta
import time
import logging
import pymssql
import random
import threading
from datetime import date, datetime, timedelta
from psycopg2 import sql
import requests
import json
from odoo import tools
from requests import Request, Session
import os
import sys
from sys import path, argv
from odoo.exceptions import ValidationError
# from ..utils.db_sync import save_report


HTML = ''
TOKEN=""
QUERY=""
CALL_TYPE=""

_logger = logging.getLogger(__name__)

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.osv import expression
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError
from odoo.addons.phone_validation.tools import phone_validation
from collections import OrderedDict, defaultdict


class cms_info(models.Model):
    _name = "cms.info.model"
    _description = "FSM Call Details"
    _rec_name = 'call_no'

    call_no = fields.Char("Call No")
    call_type = fields.Char("Call Type")
    change_call_type = fields.Char("New call type")
    change_call_type_notes = fields.Text('Call type notes')
    call_severity = fields.Char("Severity")
    call_status = fields.Selection([
        ('Unassigned', 'Unassigned'),
        ('Open', 'Open'),
        ('Accepted', 'Accepted'),
        ('Working', 'Working'),
        ('Attended', 'Attended'),
        ('Completed', 'Completed'),('Cancelled', 'Cancelled'),
        ('Closed', 'Closed')], store=1, default='Open',inverse='_on_change_call_status')
    response_time = fields.Float('Response time(HH:MM)',compute='_get_response_time')
    equipment_facetime = fields.Float('Equipment time', compute='_get_equipment_time')
    autoclose_time=fields.Char('Auto Close in',compute='_get_autoclose_time')
    rt_time = fields.Datetime('Response time')
    tat = fields.Float('TAT')
    tat_time = fields.Datetime('Tat time')
    call_log_date = fields.Datetime('Call Log Date')
    call_incident_date = fields.Datetime('Call Incident Date')
    call_assignment_date = fields.Datetime('Call Assigned Date')
    call_accepted_date = fields.Datetime('Call Accepted Date')
    call_sla = fields.Integer(compute="_checksla")
    call_planned_start_date = fields.Datetime("Planned Start Date")
    call_planned_end_date = fields.Datetime("Planned End date")
    call_schedule_startdate = fields.Datetime("Schedule Start Date")
    call_schedule_enddate = fields.Datetime("Schedule End Date")
    call_actual_startdate = fields.Datetime("Actual Start Date")
    call_actual_enddate = fields.Datetime("Actual End Date")
    call_attended_date = fields.Datetime("Attended Date")
    call_closed_date = fields.Datetime("Call Close Date")
    sr_group = fields.Char("Sr Group")
    sr_owner = fields.Char("Sr Owner")
    zone = fields.Char("Zone")
    service_channel = fields.Char('Service channel')
    engineerId = fields.Many2one("hr.employee", "Engineer")
    engineeruserid = fields.Char(related='engineerId.user_id.name')
    teamlead = fields.Char(related='engineerId.parent_id.name',string="Teamlead")
    enpi_eng_id = fields.Char()
    call_engineer_mobilenumber = fields.Char()
    fault_reported = fields.Char("Fault reported")
    alarmcodeid = fields.Char("Alarm code Id")
    chat_iframe = fields.Html("Notes", sanitize=False, compute='_get_html')
    support_iframe = fields.Html("Support", sanitize=False, compute='get_html2')
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
                                                  domain="[('lov_name','=','Problem Code Desc')]", store=1)
    resolution_code_description_id = fields.Many2one("lov.master", string="Resolution code",
                                                     domain="[('lov_name','=','Resolution Code')]", store=1)
    reason_of_pending_id = fields.Many2one("lov.master", string="Reason of pending",
                                           domain="[('lov_name','=','Reason of pending')]", store=1)

    resolution_summary = fields.Char("Resolution Summary")
    cancellation_reason = fields.Char()
    cancelled_by = fields.Many2one('res.users', store=1)
    task_no = fields.Integer()
    task_subject = fields.Char()
    task_owner_type = fields.Char()
    task_assignee_type = fields.Char()
    sp_eng_name = fields.Char()
    reschedule_reason = fields.Char()
    field_service_report_no = fields.Char()
    call_closed_approvedby = fields.Char()
    no_of_visits = fields.Integer(compute='_compute_visit_count')
    distance_category = fields.Char()
    status_of_call = fields.Char()
    call_punch_time = fields.Float()
    call_face_time = fields.Float()
    params = fields.Text()
    # todo on delete cascade has to be added

    call_material_ids = fields.One2many('call.material.activities', 'call_id')
    call_workbench_ids = fields.One2many('workbench.info', 'call_id')
    call_workbench_observation_ids = fields.One2many('workbench.observation.info', 'call_id',compute="compute_workbench_data_indo")
    call_workbench_action_taken_ids = fields.One2many('workbench.action.taken.info', 'call_id',compute="compute_workbench_data_indo")
    call_workbench_recomendatio_ids = fields.One2many('workbench.recommendation.info', 'call_id',compute="compute_workbench_data_indo")
    call_timesheet_ids = fields.One2many('call.timesheet.info', 'call_id')
    call_partorder_ids = fields.One2many('call.material.orders', 'call_id')
    call_schedule_id = fields.One2many('calendar.event', 'call_id')
    call_time_ids = fields.One2many('call.timesheet.info', 'call_id', compute='_get_otherevents_ids')
    call_labour_ids = fields.One2many('call.timesheet.info', 'call_id', compute='_get_labourevents_ids')
    fsr_attachment = fields.Binary('FSR',compute='compute_fsr_attachment')
    fsr_attachment_bool = fields.Binary('FSR Bool',compute='compute_fsr_attachment')

    @api.depends('call_no','write_date')
    def compute_fsr_attachment(self):
        for rec in self:
            fsr_ids = self.env['report.record'].sudo().search([('call_no','=',rec.call_no)])
            if fsr_ids:
                rec.fsr_attachment = fsr_ids[0].FileContent
                rec.fsr_attachment_bool = True

            else:
                rec.fsr_attachment = False
                rec.fsr_attachment_bool = False

    def compute_workbench_data_indo(self):
        for rec in self:
            if rec.call_workbench_ids:
                observation_ids = rec.call_workbench_ids.filtered(lambda a:a.activity_type and 'Observation' in a.activity_type.lov_value)
                if observation_ids:
                    for obj in observation_ids:
                        rec.call_workbench_observation_ids.create({
                            'call_id': rec.id,
                            'activity_type': obj.activity_type.id,
                            'activity_notes': obj.activity_notes,
                            'activity_date': obj.activity_date,
                        })
                else:
                    rec.call_workbench_observation_ids = [(6, 0, [])]

                action_taken_ids = rec.call_workbench_ids.filtered(lambda a:a.activity_type and 'action taken' in a.activity_type.lov_value)
                if action_taken_ids:
                    for action_taken in action_taken_ids:
                        rec.call_workbench_action_taken_ids.create({
                            'call_id': rec.id,
                            'activity_type': action_taken.activity_type.id,
                            'activity_notes': action_taken.activity_notes,
                            'activity_date': action_taken.activity_date,
                        })
                else:
                    rec.call_workbench_action_taken_ids = [(6, 0, [])]
                recommendation_ids = rec.call_workbench_ids.filtered(
                    lambda a:a.activity_type and 'Recommendation' in a.activity_type.lov_value)

                if recommendation_ids:
                    for recommendation in recommendation_ids:
                        rec.call_workbench_recomendatio_ids.create({
                            'call_id': rec.id,
                            'activity_type': recommendation.activity_type.id,
                            'activity_notes': recommendation.activity_notes,
                            'activity_date': recommendation.activity_date,
                        })
                else:
                    rec.call_workbench_recomendatio_ids = [(6, 0, [])]
            else:
                rec.call_workbench_observation_ids = [(6, 0, [])]
                rec.call_workbench_action_taken_ids = [(6, 0, [])]
                rec.call_workbench_recomendatio_ids = [(6, 0, [])]


    @api.onchange('change_call_type')
    def onchange_method(self):
        if self.change_call_type:
            _logger.info("\n Call type change call no ")
            change_call_no = self.call_no
            old_call_type = self.call_type
            new_call_type = self.change_call_type
            new_call_notes = self.change_call_type_notes

            changelog = self.env['change.request']
            newrecord = changelog.sudo().create(
                {'call_no': change_call_no, 'call_id': self._origin.id, 'inital_call_type': old_call_type,
                 'change_call_type': new_call_type,
                 'request_notes': new_call_notes})

            return

    def _get_autoclose_time(self):
        total_duration = 0.0

        if self.call_status == 'Completed' and self.call_type == 'PM_ENPI' and self.call_actual_enddate:
            duration = datetime.now() - self.call_actual_enddate
            d_sec = duration.total_seconds()
            total_duration = total_duration + d_sec
            if total_duration < 32400:
                total_duration = 32400 - total_duration
                hour = divmod(total_duration, 3600)[0]
                minute = divmod(total_duration, 60)[0]
                d_string = ''
                if total_duration < 60:
                    d_string = str(int(total_duration)) + ' Second'
                elif total_duration > 60 and minute < 60:
                    d_string = str(int(minute)) + ' Minutes'
                elif total_duration > 60 and minute > 60 and hour <= 24:
                    d_string = str(int(hour)) + ' Hour'
            else:
                d_string = "Not Autoclosed"
        else:
            d_string = "N.A"
        self.autoclose_time = d_string

    def _get_equipment_time(self):
        total_duration = 0.0
        for record in self.call_time_ids:
            if record.punch_category == 'Equipmentfacetime':
                if record.end_time and record.start_time:
                    duration = record.end_time - record.start_time
                    d_sec = duration.total_seconds()
                    total_duration = total_duration + d_sec
                else:
                    total_duration = 0
        years = divmod(total_duration, 31536000)[0]
        days = divmod(total_duration, 86400)[0]
        hour = divmod(total_duration, 3600)[0]
        minute = divmod(total_duration, 60)[0]
        d_string = ''
        if total_duration < 60:
            d_string = str(int(total_duration)) + ' Second'
        elif total_duration > 60 and minute < 60:
            d_string = str(int(minute)) + ' Minute Ago'
        elif total_duration > 60 and minute > 60 and hour <= 24:
            d_string = str(int(hour)) + ' Hour'
        elif total_duration > 60 and minute > 60 and hour > 24 and days <= 31:
            d_string = str(int(days)) + ' Days'
        elif total_duration > 60 and minute > 60 and hour > 24 and days <= 365:
            d_string = str(int(days / 31)) + ' Month'
        else:
            d_string = str(int(years)) + ' Years'
        self.equipment_facetime = total_duration / 3600

    def _get_response_time(self):
        for record in self:
            if record.call_accepted_date and record.call_log_date:
                duration = record.call_accepted_date - record.call_log_date
                d_sec = duration.total_seconds()
                record.response_time = d_sec / 3600
            else:
                record.response_time = 0

    @api.model
    # @api.onchange('call_status')
    def _get_query(self):
        global QUERY,CALL_TYPE
        folder_found = False
        addons_path = tools.config['addons_path'].split(',')

        for addons_folder in addons_path:
            readme_path = addons_folder + '\\Vertiv'

            if os.path.isdir(readme_path):
                folder_found = True
                try:
                    _logger.info(readme_path)
                    f = open(readme_path + '/fsm.conf', "r")

                    f.close()
                except:
                    # TODO to be removed for production

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

        QUERY = fsmvars['query']
        CALL_TYPE=fsmvars['call_type_list']
        myfile.close()

    def _on_change_call_status(self):
        """ On change status to closed report is generated"""
        global QUERY
        if (self.call_status != 'Completed'):
            return
        return
        _logger.info("\nOn change status\n")
        self._get_query()
        _logger.info(QUERY)
        query = (QUERY.format(self.call_no))
        if query == "":
            raise ValidationError("Execution details missing. Contact admin")
            # query="select row_to_json(cms) from (select cm.customer_email as to,concat('Automated Field Service report for your call no:', cm.call_no) subject,concat('Please find the call report for ',cm.call_no) as text,            cm.id, cm.call_no,cm.\"engineerId\",hr.name as engineername,cm.call_engineer_mobilenumber,cm.customer_name,concat(cm.customer_contact_person,':',cm.customer_contact_mobile) contact,cm.alarmcodeid serviceprovider,cm.alarmcodeid servicetype,cm.customer_address1,cm.customer_address2,cm.customer_address3,cm.customer_state,cm.call_log_date,cm.contract_status,cm.contract_no,cm.warranty_status equipment_status,cm.sr_group as servicebranch,cm.call_type as faultcode,cm.fault_reported as problemstatement,cm.customer_pincode,cm.product_code,cm.product_model,cm.product_group,cm.product_rating,cm.product_serialno,cm.customer_email,to_char(to_timestamp((cm.tat)), 'D, HH:MI:SS') as break_time,cm.call_actual_startdate as reporting_date,cm.call_actual_enddate as completion_date,cm.params,(( travetime.duration)) travel_time ,(( travetime.tst)) travel_start_time ,(( onsite.tst)) on_site_time ,(( face_time.tst)) equipment_facetime_info,(( visit.visits)) visits,((( onsite.tst+travetime.duration))) total_time ,to_json(array_agg(distinct t.*)) timesheet,to_json(array_agg(distinct m.*)) material,to_json(array_agg(distinct w.*)) workbench from cms_info_model cm ,hr_employee hr,call_timesheet_info t,call_material_activities m ,workbench_info w ,(SELECT v.call_id,v.call_no,count(*) AS visits FROM call_timesheet_info v WHERE (v.punch_category = 'Callpunchin') group by v.call_id,v.call_no) visit,(select tsc.call_id,sum(duration)tst  from   (select    t.punch_category,   t.call_id,(t.end_time-t.start_time) duration from call_timesheet_info t where t.punch_category ='Callpunchin') tsc group by tsc.call_id)onsite,(select tsc.call_id,sum(duration)tst from (select t.punch_category,   t.call_id,   (t.end_time-t.start_time) duration from  call_timesheet_info t where t.punch_category ='Equipmentfacetime') tsc group by  tsc.call_id)face_time,(select travetime.call_id, sum(travetime. duration) duration, min(travetime.start_time) as tst from (select start_notes,  punch_category, start_time,(t.end_time-t.start_time) duration, call_id from  call_timesheet_info t)travetime where punch_category='Labourtime' and start_notes = 'TIME-ON THE ROAD FOR ENPI'  group by travetime.call_id)travetime where cm.id=t.call_id and cm.id=w.call_id and cm.id=m.call_id and cm.call_no=\'%s\' and  hr.id=cm.\"engineerId\" and cm.id=travetime.call_id and cm.id=onsite.call_id and cm.id=face_time.call_id and cm.id=visit.call_id group by hr.name,visits,total_time,equipment_facetime_info, on_site_time,travel_start_time,travel_time ,cm.id) cms" % self.call_no
        self.env.cr.execute(query)
        _logger.info("\nquery :%s", query)
        calldata = self.env.cr.dictfetchone()

        if calldata == None:
            raise ValidationError("Mandatory Data not available to generate report")
            return
        _logger.info("\n\nQuery result %s \n", calldata)
        payload = json.dumps(calldata['row_to_json'])
        _logger.info("\n\nQuery result %s \n", calldata)

        Parameters = self.env['ir.config_parameter'].sudo()
        HTML = Parameters.get_param('vertiv_collab_reference_id')
        report_endpoint = HTML + "/api/v1/notification.report"
        report_headers = {'Content-Type': 'application/json'}

        try:
            report_res = requests.request("POST", report_endpoint, headers=report_headers, data=payload)
        except Exception as e:
            raise ValidationError(_("Error , Contact admin \n %s ", e))
            _logger.info("Report email not sent %s", response.json)
            return
        _logger.info("\n\n Report: %s", report_res)
        return



    def gen_report(self, query):

        _logger.info("\nGen report\n")

        if query == "":
            raise ValidationError("Execution details missing. Contact admin")
        self.env.cr.execute(query)

        calldata = self.env.cr.dictfetchone()

        if calldata == None:
            raise ValidationError("Sufficient Data not captured to generate report")
            return

        payload = json.dumps(calldata['row_to_json'])

        Parameters = self.env['ir.config_parameter'].sudo()
        HTML = Parameters.get_param('vertiv_collab_reference_id')
        report_endpoint = HTML + "/api/v1/notification.report"
        report_headers = {'Content-Type': 'application/json'}

        try:
            report_res = requests.request("POST", report_endpoint, headers=report_headers, data=payload)
            result = report_res.json()
        except Exception as e:
            raise ValidationError(_("Error , Contact admin \n %s ", e))
            _logger.info("Report email not sent %s", response.json)
            return

        _logger.info("\n\n Report: %s", report_res.json())
        return(result)

    @api.depends('call_log_date')
    @api.model
    def _checksla(self):
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

    def _get_html(self):
        global TOKEN, HTML
        Users = self.env['res.users']
        collab = self.env['collab']
        Parameters = self.env['ir.config_parameter'].sudo()
        # HTML = tools.config['html']
        HTML = Parameters.get_param('vertiv_collab_reference_id')

        userid = self.env.user.id
        user = Users.browse(userid)
        # _logger.info("\n\n Token %s", TOKEN)
        # if TOKEN == '':
        #     userid,TOKEN = collab._get_user_token(user.email)
        #     _logger.info("\n\n Token %s", TOKEN)
        #     _logger.info("\n\n Token %s", user.email)

        username = (user.email).split('@')[0].lower()
        for record in self:
            record.chat_iframe = f'<iframe src="{HTML}/group/{record.call_no.lower()}" height="400px" width="100%"/iframe>'

    def get_html2(self):
        global TOKEN, HTML
        Users = self.env['res.users']
        collab = self.env['collab']
        Parameters = self.env['ir.config_parameter'].sudo()
        HTML = Parameters.get_param('vertiv_collab_reference_id')
        # HTML = tools.config['html']

        userid = self.env.user.id
        user = Users.browse(userid)

        for record in self:
            record.support_iframe = f'<iframe src="{HTML}/group/{record.call_no.lower()}_{record.product_group.lower()}" height="400px" width="100%"/iframe>'


    def _compute_visit_count(self):
        for rec in self:
            self.no_of_visits = len(rec.call_timesheet_ids.filtered(lambda r: r.punch_category == 'Callpunchin'))

    def _get_labourevents_ids(self):
        for i in self:
            i.call_labour_ids = i.call_timesheet_ids.search(
                ['&', ('punch_category', '=', 'Labourtime'), ('call_id', '=', i.id)])

    def _get_otherevents_ids(self):
        for i in self:
            i.call_time_ids = i.call_timesheet_ids.search(
                ['&', ('punch_category', '!=', 'Labourtime'), ('call_id', '=', i.id)])

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):

        res = super(cms_info, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)

        return res

    @api.model
    def generate_number(self, group):
        # method to generate serial number for reports.
        # example:generate_number("AIR")

        generator = self.env['report.serial.generator'].search([('group_name', '=', group)])

        # Check if group name exists pervous
        if (len(generator) == 0):
            generator.create({'group_name': group, 'last_gen_date': datetime.now()})
            generator = self.env['report.serial.generator'].search([('group_name', '=', group)])

        lastdate = generator.last_gen_date
        lastnumber = generator.last_used_number
        currentdate = datetime.now().date()

        #reset daily

        if lastdate != (currentdate):

            lastdate = currentdate
            lastnumber = 1

        else:
            lastnumber = lastnumber + 1

        month = lastdate.strftime('%m')
        day=lastdate.strftime('%d')
        year = lastdate.strftime('%y')
        lastnumber_s = str(lastnumber).zfill(4)
        fsrnumber = f'{group[0:2]}{year}{month}{day}{lastnumber_s}'
        m = generator.write({'last_gen_date': lastdate, 'last_used_number': lastnumber})
        _logger.info("Fsr number %s",fsrnumber)
        return (fsrnumber)

    @api.onchange('engineerId')
    def _engineerchange(self):
        self.call_status = 'Open'
        return
    def ensure_one(self):
        return self

    # actions
    def toggle_active(self):
        return self

    def edit_schedule(self):
        wizard_id = self.env['schedule.edit'].create({'call_id': self.id,'call_planned_start_date':self.call_planned_start_date,'call_planned_end_date':self.call_planned_end_date,'call_schedule_startdate':self.call_schedule_startdate,'call_schedule_enddate':self.call_schedule_enddate})
        return {
            'name': _('Edit'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'schedule.edit',
            'res_id': wizard_id.id,
            'target': 'new',
        }


    def cancel_call(self):
        wizard_id = self.env['cancel.call'].create({
            'call_id': self.id, 'engineer_id': self.engineerId.id,
            'call_status': self.call_status, 'cancelled_by':self.cancelled_by.id,'cancellation_reason':self.cancellation_reason
        })
        return {
            'name': _('Edit'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cancel.call',
            'res_id': wizard_id.id,
            'target': 'new',
        }


    def change_engineer(self):
        lov_master=self.env['lov.master']
        sr_owner = self.env['cms.managers'].sudo().search([('resource_name','=',self.sr_owner)],limit=1)
        sr_group = self.env['branch.info'].sudo().search([('branch_name','=',self.sr_group)],limit=1)
        product_model = self.env['product.model'].sudo().search([('model','=',self.product_model)],limit=1)
        product_rating = self.env['product.rating'].sudo().search([('rating','=',self.product_rating)],limit=1)
        reason_of_pending_id = lov_master.sudo().search([('lov_value','=',self.reason_of_pending)],limit=1)
        problem_code_description_id = self.env['cms.problem.setup'].sudo().search([('problem_type','=',self.problem_code_description)],limit=1)
        resolutions_code_description_id = self.env['cms.problem.setup'].sudo().search([('resolution_type','=',self.resolution_code_description)],limit=1)
        # distance_category=fields.Many2one('lov.master',domain="[('lov_value','=',self.customer_distance_category)]")
        wizard_id = self.env['engineer.change'].create({'call_id': self.id,'sr_owner':sr_owner.id,'engineer_id':self.engineerId.id,'call_status':self.call_status,'customer_contact_mobile':self.customer_contact_mobile,'customer_email': self.customer_email,'distance_category':self.customer_distance_category,
            'customer_contact_person':self.customer_contact_person,'resolution_summary':self.resolution_summary,
            'customer_address1':self.customer_address1,
            'customer_address2':self.customer_address2,
            'customer_address3':self.customer_address3,'customer_city':self.customer_city,
            'customer_state':self.customer_state,
            'product_model':product_model.id,
            'product_rating':product_rating.id,
            'problem_code_description':self.problem_code_description,
            'resolution_code_description':self.resolution_code_description,
            'reason_of_pending_id':reason_of_pending_id.id,
            'problem_code_description_id':problem_code_description_id.id,
            'resolutions_code_description_id':resolutions_code_description_id.id,
            'sr_group': sr_group.id,
                                                        })
        return {
            'name': _('Edit'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'engineer.change',
            'res_id': wizard_id.id,
            'target': 'new',
        }

    def change_status(self):
        wizard_id = self.env['approve.call'].create({'call_id': self.id,})
        return {
            'name': _('Edit'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'approve.call',
            'res_id': wizard_id.id,
            'target': 'new',
        }
    def buttonClickEvent(self):
        c=self.env['collab']
        if self.change_call_type==False:
            punchin=completion=workbench=s=""
            if(self.field_service_report_no=='Failed' or self.field_service_report_no==False or self.field_service_report_no=='0'):
                if (self._check_punchin == False or self._check_facetime==False or self._check_labourtime==False):
                    punchin="Punch in, Equipment Facetime, Labour time "
                if (self.call_actual_enddate == False):
                    completion="Call completion date "
                if (len(self.call_workbench_ids) == False):
                    workbench="Work bench"
                s="Report not generated for call no "+self.call_no+" will not be able to close until the following mandatory fields are updated \n"+punchin+","+workbench+','+completion
                c.post_msg('#fsr_status',s)
                raise UserError(s)
            else:
                self._close_call()
        else:
            raise UserError("Call type change is pending for approval/rejection")
            return()
        return

    def sla_value(self):
        return

    @api.model
    # def autoclose(self):
    #     current_time = datetime.now()
    #     completed_time = datetime.now() - timedelta(hours=8)
    #     completed_time_range = completed_time - timedelta(hours=1)
    #     calls = self.search(['&', '&', '&', ('call_actual_enddate', '>', completed_time_range),
    #                          ('call_actual_enddate', '<', completed_time), ('call_type', '=', 'PM_ENPI'),
    #                          ('call_status', '=', 'Completed')])
    #     _logger.info("\nAuto closing %s calls", len(calls))
    #     _logger.info(calls)
    #     for i in calls:
    #         i.call_status = 'Closed'
    #         _logger.info("Call no %s closed", i.call_no)

    def _close_call(self,caller='Manager'):
        c=self.env['collab']
        self.call_status = 'Closed'
        self.call_closed_date = datetime.now()
        self.call_closed_approvedby = self.env.uid
        if caller=='Manager':
            c.post_msg("#fsr_status","Call no"+self.call_no+" is closed")
        elif caller=='Auto':
            c.post_msg("#fsr_status", "Call no " + self.call_no + " is auto closed")
        _logger.debug("Call no %s closed", self.call_no)

    def autoclose(self):
        current_time=datetime.now()
        completed_time=datetime.now()-timedelta(hours=8)
        completed_time_range=completed_time-timedelta(hours=1)
        notify = self.env['notification']
        calls=self.search(['&','&','&','&','|',('field_service_report_no','!=','0'),'|',('field_service_report_no','!=','Failed'),('field_service_report_no','!=',False),('call_actual_enddate','>',completed_time_range),('call_actual_enddate','<',completed_time),('call_type','=','PM_ENPI'),('call_status','=','Completed')])
        _logger.info("\nAuto closing %s calls %s %s",completed_time,completed_time_range,len(calls))
        _logger.info(calls)

        for i in calls:
            i._close_call(caller='Auto')
            body="PM Call Call No "+i.call_no+" has been Closed Automatically"
            # _logger.info("role %s\n ",i.engineerId.parent_id.role)
            if(i.engineerId.parent_id.role=='om'):
                vals = {'notification_type': 'Email', 'notification_from': 'FSM', 'body':body ,
                        'subject': 'Call No '+i.call_no+' is Autoclosed',
                        'notification_to':i.engineerId.parent_id.work_email, 'sent_time': datetime.now()}
                s = notify.sudo().create(vals)
            elif(i.engineerId.parent_id.role=='tl'):
                # _logger.info("role %s\n ", i.engineerId.parent_id.role)
                vals = {'notification_type': 'Email', 'notification_from': 'FSM', 'body': body,
                        'subject': 'Call No ' + i.call_no + ' is Autoclosed',
                        'notification_to': i.engineerId.parent_id.parent_id.work_email, 'sent_time': datetime.now()}
                _logger.debug("Value %s",vals)
                s = notify.sudo().create(vals)
                # _logger.info("Value %s",s)
                # _logger.info("role %s\n ", i.engineerId.parent_id.parent_id.role)
                vals = {'notification_type': 'Email', 'notification_from': 'FSM', 'body': body,
                        'subject': 'Call No ' + i.call_no + ' is Autoclosed',
                        'notification_to': i.engineerId.parent_id.work_email, 'sent_time': datetime.now()}
                s = notify.sudo().create(vals)




    def newcall_notification(self, minute=5):
        current_time = datetime.now()
        last_created_time = datetime.now() - timedelta(minutes=minute)
        calls = self.search(
            ['&', '&', '&', ('engineerId', '!=', False), ('write_uid', '=', False), ('write_date', '<', current_time),
             ('write_date', '>', last_created_time)])
        c = self.env['collab']
        for i in calls:
            email = i.engineerId.work_email
            c.post_msg(email, 'New call no ' + i.call_no + ' assigned to you')

    def gen_online_fsr(self):
        s=self.params
        newfsrvalue=False
        fsrstarting = s.find('fsr_number')
        fsrvalue = s[fsrstarting + 13:-2]
        _logger.info("fsr value %s",fsrvalue)
        newfsrvalue = fsrvalue
        fsrend = fsrvalue.find('\"')-1
        fsrvalue = s[fsrstarting + 13:fsrend]
        _logger.info("fsr value %s", fsrvalue)

        if fsrvalue.startswith("OFF_"):
            newfsrvalue = self.generate_number(self.product_group)
            new_param = s.replace(fsrvalue, newfsrvalue, 1)
            _logger.info("\n new_param")

            _logger.info(new_param)
            self.params = new_param
        return(newfsrvalue)

    @property
    def _check_punchin(self):
       i=self.call_timesheet_ids

       listofcalls=i.filtered(lambda r:r.punch_category=='Callpunchin')
       if (len(listofcalls) == 0):
            return (False)
       for s in listofcalls:
           if(s.start_time==False or s.end_time==False):
              return (False)

       return (True)

    @property
    def _check_facetime(self):

        i = self.call_timesheet_ids

        listofcalls = i.filtered(lambda r: r.punch_category == 'Equipmentfacetime')
        if (len(listofcalls)==0):
            return(False)
        for s in listofcalls:

            if (s.start_time == False or s.end_time == False):
                return False

        return True

    @property
    def _check_labourtime(self):

        i = self.call_timesheet_ids

        listofcalls = i.filtered(lambda r: r.punch_category == 'Labourtime')
        if (len(listofcalls) == 0):
             return (False)
        for s in listofcalls:

            if (s.start_time == False or s.end_time == False):
                _logger.info("Labour time failed")
                return False

        return True

    def process_generate_report_record(self):
        current_time = datetime.today().date()
        calls = self.env['cms.info.model'].search(
            ['&', '&', '&', ('write_date', '>=', current_time), ('call_status', '=', 'Completed'), '|',
             ('field_service_report_no', '!=', 'Failed'),
             ('field_service_report_no', '!=', '0'), ('field_service_report_no', '!=', False)])
        _logger.info("\n Executing server call")
        conn = pymssql.connect(server='10.114.14.33:58188', user='FSMApp01', password='Welcome@1234#',
                               database='CMSFieldServiceApp_UAT')
        mycursor = conn.cursor()
        _logger.info(mycursor)

        c = self.env['collab']
        _logger.info(calls)
        for i in calls:
            try:
                pdf_content = c.generate_report(i.call_no)
                if 'success' in pdf_content:
                    _logger.info("Report not found for %s", i.call_no)
                    continue
                _logger.info("\n\npdf_content")
                _logger.info(pdf_content)
                document_id = self.env['report.record'].sudo().search([('call_no', '=', i.call_no)])
                _logger.info("\n Report already generated boolean %s", document_id)
                if not len(document_id):
                    document_id = self.env['report.record'].sudo().create({
                        'call_no': i.call_no,
                        'FSRNo': i.field_service_report_no,
                        'FileName': pdf_content['filename'],
                        'FileContent': pdf_content['content'],
                        'DocType': pdf_content['contentType'],
                        'report_sent': False
                    })
                    call_no = i.call_no
                    FSRNo = i.field_service_report_no
                    FileName = pdf_content['filename']
                    FileContent = pdf_content['content']
                    DocType = pdf_content['contentType']
                    _logger.info(call_no, FSRNo, FileName, DocType)
                    sql = "SELECT COUNT(*) FROM [dbo].[CMS_Call_Documents];"
                    mycursor.execute(sql)
                    last_id = mycursor.fetchone()
                    id = str(int(last_id[0]) + 1)
                    sql = "insert into CMS_Call_Documents(ID, Call_No, DocType, FileName,  FileContent , FSRNo) values('" + id + "','" + call_no + "','" + DocType + "','" + FileName + "',CAST('" + FileContent + "' AS xml).value('xs:base64Binary(.)', 'varbinary(max)'),'" + FSRNo + "')"
                    mycursor.execute(sql)
                    conn.commit()
                    c.delete_report(i.call_no)
                # else:
                #     _logger.info("Elso flow")
                #     _logger.info("Elso flow %s",pdf_content)
                #     call_no=i.call_no
                #     FSRNo=i.field_service_report_no
                #     FileName=pdf_content['filename']
                #     FileContent=pdf_content['content']
                #     DocType=pdf_content['contentType']
                #     _logger.info("\n %s %s\n%s %s",call_no,FSRNo,FileName,DocType)
                #     sql = "SELECT COUNT(*) FROM [dbo].[CMS_Call_Documents];"
                #     mycursor.execute(sql)
                #     last_id = mycursor.fetchone()
                #     _logger.info("\nLast id %s",last_id)
                #     id = str(int(last_id[0]) + 1)
                #     _logger.info("\n New id %s %s",id,type(id))
                #     sql = "insert into CMS_Call_Documents(ID, Call_No, DocType, FileName,  FileContent , FSRNo) values('" + id + "','" + call_no+ "','" + DocType + "','" + FileName + "',CAST('" + FileContent + "' AS xml).value('xs:base64Binary(.)', 'varbinary(max)'),'" + FSRNo + "')"
                #     _logger.info(sql)
                #     mycursor.execute(sql)
                #     _logger.info("sql commit")
                #     conn.commit()
                #     c.delete_report(i.call_no)

            except Exception as e:
                _logger.info("Exception %s", e)
        conn.close()
        # current_time = datetime.today().date()
        # calls = self.env['cms.info.model'].search(
        #     ['&', '&', '&', ('write_date', '>=', current_time), ('call_status', '=', 'Completed'), '|',
        #      ('field_service_report_no', '!=', 'Failed'),
        #      ('field_service_report_no', '!=', '0'), ('field_service_report_no', '!=', False)])

        # c=self.env['collab']
        # _logger.info(calls)
        # for i in calls:
        #     try:
        #         pdf_content = c.generate_report(i.call_no)
        #         if 'success' in pdf_content:
        #             _logger.info("Report not found for %s",i.call_no)
        #             continue
        #         _logger.info("pdf_content")
        #         _logger.info(pdf_content)
        #         document_id = self.env['report.record'].sudo().search([('call_no', '=', i.call_no)])
        #         _logger.info("\n Report already generated boolean %s", document_id)
        #         if not len(document_id):
        #             document_id = self.env['report.record'].sudo().create({
        #                 'call_no': i.call_no,
        #                 'FSRNo': i.field_service_report_no,
        #                 'FileName': pdf_content['filename'],
        #                 'FileContent': pdf_content['content'],
        #                 'DocType': pdf_content['contentType'],
        #                 'report_sent': False
        #             })
        #             c.delete_report(i.call_no)

        #     except Exception as e:
        #         _logger.info("Exception %s", e)

    def reportgen(self,minute=5,email_list=['cm.customer_email','hr.work_email'],call_list=False):
        """ To Generate report on call closure
            Params
            \nminute - interval to generate report [currently default 5]
            \nemail_list-list of members email id to send FSR Report variables cm.customer_email & hr.work_email
                if new email id to be added use the following format "'\'xyz@xyz.com\''"
            \ncall_list-list of calls report to be generated -currently only one call can be sent """

        current_time=datetime.today().date()
        _logger.info(current_time)
        completed_time=datetime.now()-timedelta(minutes=minute)
        c = self.env['collab']
        msg='Posting message'
        _logger.debug("post message checking")
        # c.post_msg('#fsr_status',msg)
        self._get_query()

        if call_list==False:
            calls=self.search(['&','&',('write_date','>=',current_time),('call_status','=','Completed'),'|',('field_service_report_no','=','0'),('field_service_report_no','=',False)])
            _logger.info("\n%s\n%s",calls,current_time)
            # c.post_msg('#fsr_status', str(len(calls)))
        else:
            calls=self.search([('call_no','=',call_list)])
        email_to_be_sent=email_list
        for i in calls:
            try:
                punchin= i._check_punchin
                laborin=i._check_labourtime
                facetime=i._check_facetime

                if((punchin and laborin and facetime)==False):
                    _logger.info("Mandatory field in timesheet not set")
                    msg='Time sheet information missing for call_no '+i.call_no
                    c.post_msg('#fsr_status',msg)
                    # i.field_service_report_no = "Not Generated"
                    continue
                elif(( i.call_actual_startdate and i.call_actual_enddate)==False and i.call_closed_date==False and i.call_attended_date==False):
                    _logger.info("call no fields %s,_check_labour_time result %s", i.call_no, i.call_actual_startdate)
                    # i.field_service_report_no = "Not Generated"
                    msg = 'Date information missing for call_no ' + i.call_no
                    c.post_msg('#fsr_status',msg)
                    continue
                elif (i.params == False):
                    _logger.info("Params field not set")

                    msg = 'Params information missing for call_no ' + i.call_no
                    c.post_msg('#fsr_status', msg)
                    continue
                else:
                    fsr_number=i.gen_online_fsr()
                    _logger.info("Fsr number %s",fsr_number)
                    materials=len(i.call_material_ids)

                    if (materials) == 0:
                        material_field="concat('') material"
                    else:
                        material_field="coalesce(to_json(array_agg(distinct m. *)), null) material"

                    for email_to in email_to_be_sent:
                        call_type_list=json.loads(CALL_TYPE)
                        servicetype=call_type_list[i.call_type]

                        query = (QUERY.format(email_to,servicetype,material_field,i.call_no))
                        _logger.info("\n\n %s",query)
                        report_result=i.gen_report(query)
                        report_success=report_result['success']
                        _logger.debug("result of report %s",report_success)
                        if (i.field_service_report_no=='0' or i.field_service_report_no==False and report_success):
                            i.field_service_report_no=fsr_number
                            pdf_content = c.generate_report(i.call_no)
                            _logger.info("Pdf contetnt %s", pdf_content)
                            document_id=self.env['report.record'].sudo().search([('call_no','=',i.call_no)])
                            _logger.info("\n Report already generated boolean %s",document_id)
                            # if not len(document_id):
                            #     document_id = self.env['report.record'].sudo().create({
                            #         'call_no': i.call_no,
                            #         'FSRNo': fsr_number,
                            #         'FileName': pdf_content['filename'],
                            #         'FileContent': pdf_content['content'],
                            #         'DocType': pdf_content['contentType'],
                            #         'report_sent': False
                            #     })
                            #     delete_content = c.delete_report(i.call_no)
                                # save_report({'call_no': [i.call_no], 'FSRNo': [
                                #     fsr_number], 'FileName': [pdf_content['filename']],
                                #              'FileContent': pdf_content['content'],
                                #              'DocType': [pdf_content['DocType']]})
                            _logger.debug("fsr number %s %s", i.field_service_report_no, report_success)
                            c.post_msg("fsr_status", "Report has been sent to " + email_to + " for call no " + i.call_no)

                    if(report_success==False):
                            i.field_service_report_no = "Failed"
                            c.post_msg("fsr_status","Report has not been sent to " + email_to + " for call no " + i.call_no)

            except:
                i.field_service_report_no = "Failed"
                c.post_msg("fsr_status", "Report has been  failed for for call no " + i.call_no)

                continue


#Blog view
class metabase_view(models.Model):
    _name = "metabase.view"
    _description = "Metabase Reports"

    metabase_iframe = fields.Html()
    equipment_tl_iframe = fields.Html("Notes", sanitize=False, compute='get_html')

    def get_html(self):
        for record in self:
            record.chat_iframe = f'<iframe src="https://reports.fsm.vertivco.com/public/dashboard/509c3405-7c04-4d8b-af05-5cfbd88446f0" frameborder="0"     width="100%"     height="600"></iframe>'


class rsReportView(models.Model):
    _name = "rs.report.view"
    _description = "RS Reports"

    manager = fields.Char(string="manager", compute='get_html2')

    def get_html2(self):
        context = self._context
        current_uid = context.get('uid')
        User = self.env['res.users']
        current_user = User.browse(current_uid)
        current_role = current_user.employee_id.role
        user_name = current_user.name

        for record in self:
            self.manager = user_name
            return

    manager_iframe = fields.Html("RT & TAT", sanitize=False, compute='_compute_manager_iframe')

    @api.model
    def _compute_manager_iframe(self):

        report = self.env['rs.report.view']
        current_rec = report.browse(1)

        context = self._context
        current_uid = context.get('uid')
        User = self.env['res.users']
        current_user = User.browse(current_uid)
        current_role = (current_user.employee_id.role).strip()
        user_name = current_user.name
        report.manager = user_name

        if (current_role == 'ad'):
            manager_iframe = f'<iframe    src="https://reports.fsmbeta.vertivco.com/public/question/1d779286-b8fa-4626-9adb-4e56a7566b60?manager={user_name}&teamlead={user_name}#hide_parameters=manager,teamlead"    frameborder="0"    width="100%"    height="600"    ></iframe>'
            # manager_iframe = f'https://reports.fsmbeta.vertivco.com/public/question/1d779286-b8fa-4626-9adb-4e56a7566b60?manager={user_name}&teamlead={user_name}#hide_parameters=manager,teamlead'


            for record in report:
                record.manager_iframe = f'<iframe    src="https://reports.fsmbeta.vertivco.com/public/question/1d779286-b8fa-4626-9adb-4e56a7566b60?manager={user_name}&teamlead={user_name}#hide_parameters=manager,teamlead"    frameborder="0"    width="100%"    height="600"    ></iframe>'
                record.manager = current_user.name


class ReportRecord(models.Model):
    _name = "report.record"
    _description = "CMS Documents"


    call_no = fields.Char('call_no')
    FSRNo = fields.Char('field_service_report_no')
    FileName = fields.Char('FileName')
    FileContent = fields.Binary('FileContent')
    DocType = fields.Char('DocType')
    UploadedDate = fields.Datetime(string='write_date', default=datetime.today())
    report_sent =fields.Boolean()

