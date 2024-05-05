from odoo import api,models,fields

class LaborTimesheet(models.Transientmodel)
    _name='Labortimesheet view'

    noofvisists=fields.Integer()