from odoo import fields, models, api
from datetime import datetime


class WebhookLog(models.Model):
    _name = 'webhook_log'
    _description = "Webhook Log"

    webhook_subscription = fields.Many2one(comodel_name="webhook_subscription", string="Webhook subscription", required = True)

    webhook = fields.Many2one(comodel_name="base.automation", string="Webhook event", required=False, compute = "_compute_webhook", store = "True")

    webhook_url = fields.Char(string="Webhook callback URL", required=False, compute = "_compute_webhook_url", store = "True")

    request_header = fields.Char(string="Request header", required=False,)
    request_body = fields.Char(string="Request body ( Sent data )", required=False,)
    response_header = fields.Char(string="Response header", required=False,)
    response_body = fields.Char(string="Response body", required=False, )
    status_code = fields.Char(string="Response status code", required=False, )

    @api.depends("webhook_subscription")
    def _compute_webhook_url(self):
        for log in self:
            log.webhook_url = log.webhook_subscription.webhook_url

    @api.depends("webhook_subscription")
    def _compute_webhook(self):
        for log in self:
            log.webhook = log.webhook_subscription.webhook.id

    @api.model
    def create(self, vals):
        rec = super(WebhookLog,self).create(vals)
        print(rec)
        return rec







