# -*- coding: utf-8 -*-

from odoo import api, fields, models

class WebhookSubscription(models.Model):
    _name = "webhook_subscription"
    _description = "webhook_subscription"
    _order = 'create_date desc'
    name = fields.Char(string="Subscription name", required=False, )
    subscriber = fields.Many2one(comodel_name="res.users", string="Subscriber", required = True)
    subscriber_name = fields.Char(string = "Subscriber's name", compute = "_compute_subscriber_name", readonly = True, store = True)
    webhook = fields.Many2one(comodel_name="base.automation", string="Event", required=True, domain = "[('is_webhook','=',True)]")
    webhook_url = fields.Char( string="Webhook URL", required = True)
    description = fields.Char( string="Description", default = "", required = False)
    logs = fields.One2many(comodel_name="webhook_log", inverse_name="webhook_subscription", string="Logs", required=False, readonly=True )

    @api.model
    def create(self, vals):
        if not vals.get('subscriber'):
            vals.update({'subscriber': self.env.uid})
        rec = super(WebhookSubscription,self).create(vals)
        return rec

    def unlink(self):
        return super(WebhookSubscription,self).unlink()


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


