from odoo import fields, models, api

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    employee_id=fields.Many2one('hr.employee',related='user_id.employee_id', readonly=True)
    call_id=fields.Many2one('cms.info.model')


