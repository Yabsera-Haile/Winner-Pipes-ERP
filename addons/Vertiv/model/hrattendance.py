from odoo import fields, models, api,exceptions, _
from datetime import datetime
from odoo.tools import format_datetime
from odoo.exceptions import ValidationError
import requests
import json

import logging

_logger = logging.getLogger(__name__)

HTML = ''
PASS_WORD = ''


class HrAttendance(models.Model):
    _inherit = ['hr.attendance']

    break_id=fields.One2many('attendance.break','attendance_id',ondelete='cascade')
    total_break_hrs=fields.Float('Break Hours',compute='_compute_break_hours',)
    total_hours=fields.Float('Worked Hours',compute='_compute_total_hours')

    #Fetch all the corresponding break records for a given attendance record

    @api.depends('break_id.break_hours')
    def _compute_break_hours(self):
        breaktime = 0.0
        for record in self:
            for line in record.break_id:
                breaktime += line.break_hours
            record.total_break_hrs = breaktime


    @api.depends('total_break_hrs','worked_hours')
    def _compute_total_hours(self):
        for records in self:
            if (records.check_out != False):
                records.total_hours=records.worked_hours-records.total_break_hrs
            else:
                records.total_hours=False

class HrAttendanceBreak(models.Model):
    _name = "attendance.break"
    _description='Attendance break details'

    attendance_id=fields.Many2one('hr.attendance',store=1)
    break_in=fields.Datetime()
    employee_id = fields.Many2one(related='attendance_id.employee_id')
    break_out = fields.Datetime()
    break_type=fields.Char("Type")
    break_hours = fields.Float(string='Break Duration', compute='_compute_worked_hours', store=True, readonly=True)
    break_display=fields.Char()
    break_notes=fields.Text()



    @api.onchange('break_in')
    def onchange_method(self):
        self.break_display = 'in'
        for attendance in self:
            if attendance.break_in < attendance.attendance_id.check_in:
                raise exceptions.ValidationError(_('"Break in" time cannot be earlier than "Check In" time.'))



    @api.onchange('break_out')
    def onchange_breakout(self):
        self.break_display =  self.break_display+'- out'
        for attendance in self:
            if attendance.break_out and attendance.break_in ==False:
                raise exceptions.ValidationError(_('"Break in" time not found'))

    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.break_out:
                result.append((attendance.id, _("%(from)s %(break_in)s") % {
                    'break_in': format_datetime(self.env, attendance.break_in, dt_format='hh:mm a'),
                    'from':attendance.break_type,
                }))
            else:
                result.append((attendance.id, _("%(from)s %(break_in)s - %(break_out)s") % {
                    'break_in': format_datetime(self.env, attendance.break_in, dt_format='hh:mm a'),
                    'break_out': format_datetime(self.env, attendance.break_out, dt_format='hh:mm a'),
                    'from':attendance.break_type
                }))

        return result

    @api.depends('break_in', 'break_out')
    def _compute_worked_hours(self):
        """ Calculates break duration. """
        for attendance in self:
            if attendance.break_out and attendance.break_in:
                delta = attendance.break_out - attendance.break_in
                attendance.break_hours = delta.total_seconds() / 3600.0
            else:
                attendance.break_hours = False

    @api.constrains('break_in', 'break_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.break_in and attendance.break_out:
                if attendance.break_out < attendance.break_in:
                    raise exceptions.ValidationError(_('"Break Out" time cannot be earlier than "Break In" time.'))



