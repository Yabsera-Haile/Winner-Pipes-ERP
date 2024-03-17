
from odoo import fields, models, api


class zone_info(models.Model):
    _name = "zone.info"
    _description = "zone details"
    _rec_name='zone_name'

    zone_id=fields.Integer()
    zone_name=fields.Char()
    is_active=fields.Boolean()



class branch_info(models.Model):
    _name = "branch.info"
    _description = "Branch details"
    _rec_name='branch_name'

    branch_name = fields.Char()
    branch_id = fields.Integer()
    branch_description=fields.Char()
    branch_isactive=fields.Boolean()

class lov_master(models.Model):
    _name = "lov.master"
    _description = "List of values"
    _rec_name="lov_value"


    lov_no = fields.Integer('Lov number')
    lov_name = fields.Char('Name')
    lov_value=fields.Char('Value')
    is_enable=fields.Boolean()

class sla_master(models.Model):
    _name = "sla.master"
    _description = "SLA Values"
    _rec_name="product_group"

    #product_id = fields.Many2one("product.info.model",string="Product",store=1)
    product_group=fields.Many2one("lov.master",string="Category",domain="[('lov_name','=','Product Group')]")
    distance_category=fields.Many2one("lov.master",string="Distance",domain="[('lov_name','=','Distance Category')]")
    target_response_hrs = fields.Integer("Target Hours")
    alert_hrs=fields.Integer("Alert Hours")

    #TODO SQL CONSTRAINTS HAS TO BE VERIFIED FOR UNIQUE RECORDS.
#other code
    _sql_constraints = [ ('check_existance', 'unique(product_group, distance_category)', 'Cannot Use one tracker twice!\nPlease, select a different product')	]

    def check_existance(self, cr, uid, ids, context=None):
        self_obj = self.browse(cr, uid, ids[0], context=context)
        productname = self_obj.product_group
        distance = self_obj.distance_category
        search_ids = self.search(cr, uid, [('distance', '=', distance), ('product_group', '=', productname)], context=context)
        res = True
        if len(search_ids) > 1:
            res = False
        return res

