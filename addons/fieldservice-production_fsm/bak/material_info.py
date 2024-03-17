from odoo import fields, models, api

class material_info(models.Model):
    _name = "material.info"
    _description = "Material details"
    _rec_name = "call_id"

    call_id = fields.Many2one('cms.info.model')
    task_id=fields.Char(related='call_id.task_no')
    part_activity=fields.Char()
    part_replace_date=fields.Datetime()
    eng_subinventory=fields.Char()
    eng_locator=fields.Char()
    part_code=fields.Char()
    part_description=fields.Char()
    part_qty=fields.Char()
    product_serialno=fields.Char()