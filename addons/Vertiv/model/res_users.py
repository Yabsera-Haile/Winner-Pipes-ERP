from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError
import requests
import json

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    HTML = fields.Char(string="Collab Instance", config_parameter='vertiv_collab_reference_id')
   
   

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            HTML = self.env['ir.config_parameter'].sudo().get_param('vertiv_collab_reference_id'),

        )
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.HTML
     

        param.set_param('vertiv_collab_reference_id', field1)

class ResUsers(models.Model):
    _inherit = ['res.users']

    # collab_token = fields.Char(compute='collab_toke')
    login = fields.Char(
        help='Used to log into the system. Case insensitive.',
    )

    ################Actions
    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        """Overload _login to lowercase the `login` before passing to the
        super"""
        login = login.lower()
        return super(ResUsers, cls)._login(
            db, login, password, user_agent_env=user_agent_env
        )
