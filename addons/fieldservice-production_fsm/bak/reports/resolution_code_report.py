from odoo import fields, models, api,tools

class Engg_resolution_report(models.Model):
    _name="resolution.report"
    _auto=False
    _description="Resolution report"
    _rec_name = "id"

    engineerId = fields.Many2one("hr.employee", "Engineer")
    resolution_code_description = fields.Char()
    call_type = fields.Char("Call Type")
    attended_date = fields.Date('Attended Date')
    product_model = fields.Char('Model')
    product_group = fields.Char()
    zone = fields.Char("Zone")
    sr_group = fields.Char("SR Group")
    calls = fields.Integer("No. of Calls", group_operator='sum')

    # occupied_time2 = fields.Char()

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(""" CREATE OR REPLACE VIEW %s AS (SELECT 
           row_number() OVER () as id,   zone,
        "cms_info_model"."engineerId" AS "engineerId",
        resolution_code_description,
        product_group,
        product_model,
        sr_group,
        date_trunc('month',
        call_closed_date) as attended_date,
        count(*) as calls 
    from
        cms_info_model 
    where
         (
            call_status='Completed' 
            or call_status='Closed'
        )  
    group by
        zone,
        product_group,
        resolution_code_description,
        product_model,
        sr_group,
        call_closed_date,
        "cms_info_model"."engineerId" 
    order by
        Zone,
        product_group,
        calls,
        resolution_code_description
                        )""" % (self._table))


class zone_resolution_report(models.Model):
    _name = "zone.resolution.report"
    _auto = False
    _description = "Resolution report"
    _rec_name = "id"

    resolution_code_description = fields.Char()
    # call_type=fields.Char("Call Type")
    attended_date = fields.Date('Attended Date')
    product_model = fields.Char('Model')
    product_group = fields.Char('Product Group')
    zone = fields.Char("Zone")
    sr_group = fields.Char("SR Group")
    calls = fields.Integer("No. of Calls", group_operator='sum')

    # occupied_time2 = fields.Char()


    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(""" CREATE OR REPLACE VIEW %s AS (SELECT 
           row_number() OVER () as id, zone,
        resolution_code_description,
        product_group,
        product_model,
        sr_group,
        date_trunc('month',
        call_closed_date) as attended_date,
        count(*) as calls 
    from
        cms_info_model  
    where
        (
            call_status='Completed' 
            or call_status='Closed'
        )  
    group by
        zone,
        product_group,
        resolution_code_description,
        product_model,
        sr_group,
        call_closed_date 
    order by
        Zone,
        product_group,
        calls,
        resolution_code_description
                        )""" % (self._table))
