from odoo import fields, models, api


class BaseAutomationInherit(models.Model):
    _inherit = 'base.automation'
    _description = 'Automated Action'
    is_webhook = fields.Boolean(default=False, compute="_compute_is_webhook", store = True)
    webhook_subscriptions = fields.One2many(comodel_name="webhook_subscription", inverse_name="webhook", string="", required=False, )

    @api.depends("state")
    def _compute_is_webhook(self):
        for action in self:
            action.is_webhook = (action.state == "webhook")

    @api.onchange('state')
    def _onchange_is_webhook(self):
        for action in self:
            action.is_webhook = (action.state == "webhook")


