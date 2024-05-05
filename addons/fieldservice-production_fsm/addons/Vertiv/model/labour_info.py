from odoo import fields, models, api

class labour_info(models.Model):
    _name = "labour.info"
    _description = "Labour details"
    _rec_name = "call_id"
    
    call_id=fields.Many2one('cms.info.model')
    call_no = fields.Char(related='call_id.call_no', store=1)
    task_no = fields.Integer(related='call_id.task_no')
    labour_activity=fields.Char()
    labour_date=fields.Date()
    labour_item_starttime=fields.Datetime()
    labour_item_endtime=fields.Datetime()
    labour_reason=fields.Char()
    labour_item=fields.Char()
    labour_desc=fields.Char()

