# -*- coding: utf-8 -*-

from odoo import api, fields, models

# TODO ::
# Do I need this ? No
class Webhook(models.Model):
    _name = "webhook"
    _description = "Webhook"
    name = fields.Char(string="Webhook's name", required=False )
    url = fields.Char(string="Custom webhook URL", required=False)
    condition = fields.Selection(string="condition", selection=[('one', 'One'), ('two', 'Two'), ], required= True )
    request_method = fields.Selection(string="Request Method", selection=[('GET', 'GET'), ('POST', 'POST'), ], required = True)
    request_body = fields.Char(string="Request Body", required=False )

