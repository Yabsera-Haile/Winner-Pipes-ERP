from odoo import fields, models, api


class partorder_info(models.Model):
    _name = "partorder.info"
    _description = "Part Order details"
    _rec_name="order_number"
    

    call_id = fields.Many2one('cms.info.model')
    task_id = fields.Char(related='call_id.task_no')
    call_city=fields.Char(related='call_id.customer_city')
    call_engineer = fields.Char(related='call_id.engineerId.name')
    order_number=fields.Char()
    order_date=fields.Date()
    shipping_address=fields.Text()
    order_status=fields.Char()
    shipped_date=fields.Char()
    order_expected_date=fields.Date()
    item_ids=fields.One2many('parts.item.info','order_number')

class parts_info(models.Model):
    _name = "parts.item.info"
    _description = "Part item details"
    _rec_name='item_number'

    order_number=fields.Many2one('partorder.info')
    item_number = fields.Char("Part code")
    item_desc = fields.Char("Part Description")
    qty=fields.Integer("Qty")

    # todo to be cleaned FROM CALL.TIMESHEET.INFO
    # class Equipment_facetime(models.Model):
    #     _name = "equipment.facetime.info"
    #     _description = "Equipment facetime details"
    #
    #     call_id=fields.Many2one('cms.info.model')
    #     task_no=fields.Integer(related='call_id.task_no')
    #     punch_type=fields.Char()
    #     punch_in=fields.Datetime()
    #     punch_out=fields.Datetime()
    #     punch_in_notes=fields.Char()
    #     punch_out_notes=fields.Char()
    #
    # class Call_Punchtime(models.Model):
    #     _name = "call.punchtime.info"
    #     _description = "Call punch time details"
    #
    #     call_id=fields.Many2one('cms.info.model')
    #     task_no = fields.Integer(related='call_id.task_no')
    #     punch_in=fields.Datetime()
    #     punch_out=fields.Datetime()
    #     punch_in_notes=fields.Char()
    #     punch_out_notes=fields.Char()
    #     punch_in_latitude=fields.Char()
    #     punch_in_longitude=fields.Char()
    #     punch_out_latitude=fields.Char()
    #     punch_out_longitude=fields.Char()


