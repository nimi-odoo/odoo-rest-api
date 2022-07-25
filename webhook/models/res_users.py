# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = "res.users"
    webhook_subscriptions = fields.One2many(comodel_name="webhook_subscription", inverse_name="subscriber", string="Webhook Subscriptions")
