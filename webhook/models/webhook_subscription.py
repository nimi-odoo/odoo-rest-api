# -*- coding: utf-8 -*-

from odoo import api, fields, models

class WebhookSubscription(models.Model):
    _name = "webhook_subscription"
    _description = "webhook_subscription"
    subscriber = fields.Many2one(comodel_name="res.users", string="Subscriber", required = False)
    subscriber_name = fields.Char(string = "Subscriber's name", compute = "_compute_subscriber_name", readonly = True, store = True)
    webhook_url = fields.Char( string="Webhook URL", required = True)
    automated_actions = fields.Many2many(comodel_name="base.automation", relation="webhook_rel", column1 = 'base_automation_id', column2 = "webhook_subscription_id", string = "Subscribed Actions")

    @api.model
    def create(self, vals):
        rec = super(WebhookSubscription,self).create(vals)
        return rec


    @api.depends("subscriber")
    def _compute_subscriber_name(self):
        for rec in self :
            if rec.subscriber.name :
                rec.subscriber_name = rec.subscriber.name

    @api.onchange("subscriber")
    def _on_change_subscriber_name(self):
        for rec in self:
            if rec.subscriber.name:
                rec.subscriber_name = rec.subscriber.name


    # @api.model
    # def create(self):
    #     print("create")
    #
    # @api.model
    # def edit(self):
    #     print("edit")
    #
    # @api.model
    # def delete(self):
    #     print("delete")


