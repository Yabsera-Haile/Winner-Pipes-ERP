from odoo import fields, models, api


class partcode_info(models.Model):
    _name = "partcode.info"
    _description = "Part details"
    _rec_name='item_number'

    organisation_code=fields.Char()
    organisation_name=fields.Char()
    subinventory=fields.Char()
    locator_name=fields.Char()
    item_number=fields.Char("Part code")
    item_desc=fields.Char("Part Description")
    on_hand_qty=fields.Integer()

