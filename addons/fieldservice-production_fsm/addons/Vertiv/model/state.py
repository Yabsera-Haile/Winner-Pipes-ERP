
from odoo import fields, models, api

import logging
import json
_logger = logging.getLogger(__name__)

class state_info(models.Model):
    _name = "state.master"
    _description = "State details"
    _rec_name='state_name'

    state_name=fields.Char()
    state_id=fields.Integer()

class  city_info(models.Model):
    _name="city.master"
    _description="city details"

    city_name=fields.Char()
    state_name=fields.Char()
    is_active=fields.Boolean()

class Warehouse(models.Model):
    _name = "warehouse"
    _description = "Warehouse details"
    _rec_name='wh_location'

    wh_location=fields.Char()
    mapped_state=fields.Char()
    contact_ids=fields.Many2many('hr.employee')
    wh_address=fields.Text()
    wh_contact=fields.Char()
    wh_contact_email=fields.Char()
    wh_region=fields.Char()



    @api.onchange('contact_ids')
    def _update_wh_state(self):
        _logger.info("\nWarehouse onchage\n\n ")
        hr_list = self.env['hr.employee']
        for i in self:
            for contact_list in i.contact_ids:
                hr = hr_list.browse(contact_list)




    def write(self, values):
        """Override default Odoo create function and extend."""
        # Do your custom logic here
        hr_list= self.env['hr.employee']

        for i in self:
            for contact_list in i.contact_ids:
         
                hr=hr_list.search([('id','=',contact_list.id) ])
              

                s=hr.write({'wh_state':i.mapped_state})



        return super(Warehouse, self).write(values)

    # order_id = fields.One2many("call.material.orders")