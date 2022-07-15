# -*- coding: utf-8 -*-

from odoo import api, fields, models

class WebhookSubscription(models.Model):
    _name = "webhook_subscription"
    _description = "webhook_subscription"
    subscriber = fields.Many2one(comodel_name="res.user", string="Subscriber's id in server", required = False)
    webhook_url = fields.Char( string="Webhook URL", required = True)
    automated_actions = fields.Many2many(comodel_name="base.automation", relation="", column1="", column2="" )

    @api.model
    def create(self):
        print("create")

    @api.model
    def edit(self):
        print("edit")

    @api.model
    def delete(self):
        print("delete")


