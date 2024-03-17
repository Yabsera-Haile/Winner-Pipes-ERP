from odoo import fields, models, api

class CmsManagers(models.Model):
    _name = 'cms.managers'
    _description = 'CMS Manager'
    _rec_name = 'resource_name'

    group_name = fields.Char('Group Name')
    resource_name = fields.Char('Resource Name')
    resource_number = fields.Char('Resource Number')


