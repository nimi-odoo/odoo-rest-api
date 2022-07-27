# -*- coding: utf-8 -*-

from odoo import api, fields, models

class WebhookSubscription(models.Model):
    _name = "webhook_subscription"
    _description = "webhook_subscription"
    subscriber = fields.Many2one(comodel_name="res.users", string="Subscriber", required = False)
    subscriber_name = fields.Char(string = "Subscriber's name", compute = "_compute_subscriber_name", readonly = True, store = True)
    webhook_url = fields.Char( string="Webhook URL", required = True)
    webhook = fields.Many2one(comodel_name="base.automation", string="Webhook", required=False)

    @api.model
    def create(self, vals):
        vals.update({'subscriber':self.env.uid})
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

    def edit_subscription_wizard(self):
        print("Wizard method")
        return ("ASDASDAS")

    def edit_subscription(self, new_webhook_id, new_webhook_url):
        self.webhook_url = new_webhook_url
        self.webhook = int(new_webhook_id)
        return


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


