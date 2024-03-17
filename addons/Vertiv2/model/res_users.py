from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError
import requests
import json

import logging
from PIL import Image


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
    user_avatar_image_url = fields.Char("Image Avatar Url",compute="compute_user_avatar_url")

    def compute_user_avatar_url(self):
        for rec in self:
            Parameters = self.env['ir.config_parameter'].sudo()
            url = Parameters.get_param('vertiv_collab_reference_id')
            user_name = rec.login.split('@')[0]
            rec.user_avatar_image_url = url +'/avatar/'+ user_name

    ################Actions
    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        """Overload _login to lowercase the `login` before passing to the
        super"""
        login = login.lower()
        return super(ResUsers, cls)._login(
            db, login, password, user_agent_env=user_agent_env
        )
