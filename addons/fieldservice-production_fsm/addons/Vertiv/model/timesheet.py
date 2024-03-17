from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)




class Call_Timesheet(models.Model):
    _name = "call.timesheet.info"
    _description = "Call related time sheet activities"
    _order="start_time"
    _rec_name="punch_category"
    
    call_id = fields.Many2one('cms.info.model')
    call_no = fields.Char(related='call_id.call_no', store=1)
    task_no = fields.Integer(related='call_id.task_no', store=1)

    # punch_category=fields.Many2one('timepunch.category')

    punch_category=fields.Selection([
        ('Callpunchin', 'Punch Time'),
        ('Equipmentfacetime', 'Equipment Facetime'),
        ('Labourtime', 'Labour Activity')], default='Callpunchin',store=1)
    punch_type = fields.Char()
    start_time = fields.Datetime()
    end_time = fields.Datetime()
    #Stat notes used to collect labour description for labor table
    start_notes = fields.Text()
    close_notes = fields.Text()
    punch_in_latitude = fields.Char()
    punch_in_longitude = fields.Char()
    punch_out_latitude = fields.Char()
    punch_out_longitude = fields.Char()


   
