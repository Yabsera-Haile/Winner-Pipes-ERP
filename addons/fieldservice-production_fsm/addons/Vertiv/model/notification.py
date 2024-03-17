from odoo import fields, models, api

class Notification(models.Model):

    _name = "notification"
    _description = "Notification details"

    notification_type=fields.Char()
    notification_from = fields.Char()
    notification_to=fields.Char()
    subject=fields.Char()
    body=fields.Char()
    status=fields.Char()
    sent_time=fields.Datetime()