from odoo import fields, models, api
from datetime import datetime


class WebhookLog(models.Model):
    _name = 'webhook_log'
    _description = "Webhook Log"
    _order = 'create_date desc'

    webhook_subscription = fields.Many2one(comodel_name="webhook_subscription", string="Webhook subscription", required = True, readonly = True)
    subscriber = fields.Many2one(comodel_name="res.users", string="Subscriber", store = "True", compute = "_compute_subscriber", readonly = True)

    webhook = fields.Many2one(comodel_name="base.automation", string="Webhook event", required=False, compute = "_compute_webhook", store = "True",readonly = True)

    webhook_url = fields.Char(string="Webhook callback URL", required=False, compute = "_compute_webhook_url", store = "True",readonly = True)

    request_header = fields.Char(string="Request header", required=False,readonly = True)
    request_body = fields.Char(string="Request body ( Sent data )", required=False,readonly = True)
    response_header = fields.Char(string="Response header", required=False,readonly = True)
    response_body = fields.Char(string="Response body", required=False,readonly = True)
    status_code = fields.Char(string="Status code", required=False,readonly = True )

    @api.depends("webhook_subscription")
    def _compute_webhook_url(self):
        for log in self:
            log.webhook_url = log.webhook_subscription.webhook_url

    @api.depends("webhook_subscription")
    def _compute_webhook(self):
        for log in self:
            log.webhook = log.webhook_subscription.webhook.id

    @api.depends("webhook_subscription")
    def _compute_subscriber(self):
        for log in self:
            log.subscriber = log.webhook_subscription.subscriber

    @api.model
    def create(self, vals):
        rec = super(WebhookLog,self).create(vals)
        return rec







