from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class MaterialActivity(models.Model):
    _name = "call.material.activities"
    _description = "Call based material details"
    _rec_name = "call_id"

    call_id = fields.Many2one('cms.info.model')
    call_no = fields.Char(related='call_id.call_no', store=1)
    task_no=fields.Integer(related='call_id.task_no', store=1)
    part_activity=fields.Char()
    part_replaced_date=fields.Datetime()
    eng_subinventory=fields.Char()
    eng_locator=fields.Char()
    part_code=fields.Char()
    part_qty=fields.Integer('Quantity')
    product_serialno=fields.Char('Serial No')
    part_description = fields.Char()


class CallPartOrder(models.Model):
    _name = "call.material.orders"
    _description = "Material Order details"
    _rec_name = "order_number"

    call_id = fields.Many2one('cms.info.model')
    call_no=fields.Char(related='call_id.call_no', store=1)
    task_no = fields.Integer(related='call_id.task_no',store=1)
    call_city = fields.Char(related='call_id.customer_city')
    customer_details=fields.Text(compute='_get_customer_details')
    customer_name = fields.Char(related='call_id.customer_name')
    customer_site_address = fields.Char(related='call_id.customer_site_address')
    customer_contact_person = fields.Char(related='call_id.customer_contact_person')
    customer_contact_mobile = fields.Char("Contact number" ,related='call_id.customer_contact_mobile')
    call_state = fields.Char(related='call_id.customer_state',store=1)
    call_engineer = fields.Char(related='call_id.engineerId.name')
    order_number = fields.Char()
    order_date = fields.Date()
    shipping_address = fields.Text()
    order_status = fields.Selection([
        ('Requested', 'Requested'),
        ('Acknowledged', 'Acknowledged'),
        ('Picked', 'Picked'),
        ('Shipped', 'Shipped'),
        ('Received', 'Received')], store=1,inverse="_order_status")
    last_updated_at = fields.Datetime()
    shipped_date = fields.Datetime(store=1)
    received_date = fields.Datetime()
    notes = fields.Char()
    order_expected_date = fields.Date()
    item_number = fields.Many2one("parts.catalog", string="Part code")
    item_desc = fields.Char("Part Description", related="item_number.item_desc")
    qty = fields.Integer("Qty")
    orderlog = fields.One2many('order.activity.log', 'order_id')
    warehouse_id = fields.Many2one('warehouse', string="Warehouse",domain="[('mapped_state','=',call_state)]")
    wh_state = fields.Char('Warehouse State')
    wh_city = fields.Char('Warehouse City')
    wh_contact = fields.Char()
    last_order_status = fields.Selection([
        ('Requested', 'Requested'),
        ('Acknowledged', 'Acknowledged'),
        ('Picked', 'Picked'),
        ('Shipped', 'Shipped'),
        ('Received', 'Received')])

    def part_order_state_cron(self):
        part_order_ids = self.env['call.material.orders'].sudo().search([])
        for rec in part_order_ids:
            if rec.order_status != 'Received':
                if not rec.last_order_status:
                    rec.last_order_status = rec.order_status
                else:
                    if rec.last_order_status == rec.order_status:
                        if rec.call_id:
                            notify = self.env['notification']
                            body = "Part Order status of Call " + str(rec.call_id.call_no)+ " is older, no changes in this call's part order status"
                            notification_type = 'Email'
                            subject = "Part Order Status"
                            curr_time = datetime.now()
                            vals1 = {'notification_type': notification_type, 'notification_from': 'Vertiv team',
                                    'body': body,
                                    'subject': subject,
                                    'notification_to': rec.call_id.engineerId.parent_id.work_email if rec.call_id.engineerId.parent_id else '', 'sent_time': curr_time}
                            notify.sudo().create(vals1)

                            vals = {'notification_type': notification_type, 'notification_from': 'Vertiv team',
                            'body': body,
                            'subject': subject,
                            'notification_to': rec.call_id.engineerId.work_email if rec.call_id.engineerId else '', 'sent_time': curr_time}
                            notify.sudo().create(vals)

                    else:
                        rec.last_order_status = rec.order_status

    @api.model
    def _get_wh_state(self):
        self.wh_state=self.call_state
        return
    def _get_customer_details(self):
        self.customer_details=self.call_id.customer_name+"\n"+(self.call_id.customer_address1 if self.call_id.customer_address1 else "")+"\n"+(self.call_id.customer_address2 if self.call_id.customer_address2 else "")+"\n"+(self.call_id.customer_address3 if self.call_id.customer_address3 else "")+"\n"+(self.call_id.customer_city if self.call_id.customer_city else "")+"\n\nCutomer Contact: "+(self.call_id.customer_contact_person if self.call_id.customer_contact_person else "") +"\nMobile:"+(self.call_id.customer_contact_mobile if self.call_id.customer_contact_mobile else "")
    @api.model
    def create(self, vals):
        log = self.env['order.activity.log']

        vals['order_status']='Requested'

        res = log.sudo().create({'order_id': self.id, 'current_status': self.order_status, 'new_status': 'Requested',
                        'notes': 'Order Created', 'change_done_by': self.env.uid,
                        'change_done_at': fields.datetime.now(), })
        return super(CallPartOrder, self).create(vals)


    def acknowledge_order(self):
        log=self.env['order.activity.log']


        for i in self:
            if len(i.warehouse_id) == 0:
         
                raise ValidationError("Warehouse has to be selected to proceed further")
                return
        s=log.create({'order_id':self.id,'current_status': self.order_status,'new_status':'Acknowledged','notes':'Acknowledged Order','change_done_by':self.env.uid, 'change_done_at':fields.datetime.now(),})
        self.order_status = "Acknowledged"
        self.notes="Order received in warehouse"
        self.last_updated_at=fields.datetime.now()
        self.wh_contact=self.env.user.id
        self.wh_state=self.env.user.employee_id.employee_state
        # self.wh_state=warehouse_id.mapped_state to check and implement. as employee-state is empty.
       
        return
    def picked_order(self):
        log=self.env['order.activity.log']
        s=log.create({'order_id':self.id,'current_status': self.order_status,'new_status':'Picked','notes':'Order picked and ready for delivery','change_done_by':self.env.uid,'change_done_at':fields.datetime.now()})
        self.order_status = "Picked"
        self.notes = "Materials picked up and ready for shipping"+self.notes
        self.last_updated_at = fields.datetime.now()
        return

    def shipped_order(self):
        log = self.env['order.activity.log']
        if self.shipped_date:
            s = log.create({'order_id':self.id,'current_status': self.order_status, 'new_status': 'Shipped',
                         'notes': 'Order Shipped', 'change_done_by': self.env.uid,'change_done_at':fields.datetime.now()})
            self.order_status = "Shipped"
            self.notes = "Order shipped"
            self.last_updated_at = fields.datetime.now()
            return

    def _order_status(self):
        if (self.order_status!='Received'):
            return
        self.received_order()

    def received_order(self):
        log = self.env['order.activity.log']
        s = log.create({'order_id':self.id,'current_status': self.order_status, 'new_status': 'Received',
                         'notes': 'Order Received', 'change_done_at':fields.datetime.now(),'change_done_by': self.env.uid})
        self.order_status = "Received"
        self.notes = "Order Received "
        self.last_updated_at = fields.datetime.now()
        return

class Orderactivitylog(models.Model):
    _name = "order.activity.log"
    _description="Order activity histroy"
    _rec_name="order_id"

    call_id = fields.Many2one('cms.info.model',related="order_id.call_id")
    order_id = fields.Many2one("call.material.orders")
    current_status = fields.Char()
    new_status = fields.Char()
    notes = fields.Char()
    change_done_by = fields.Many2one('res.users')
    change_done_at = fields.Datetime()


class Parts_catalog(models.Model):
    _name = "parts.catalog"
    _description = "Parts Catalog"
    _rec_name = 'item_num'
    organization_code = fields.Char()
    organization_name = fields.Char()
    subinventory_code = fields.Char()
    locator_name = fields.Char()
    item_num = fields.Char("Part code")
    item_desc = fields.Char("Part Description")
    on_hand_qty = fields.Char()
