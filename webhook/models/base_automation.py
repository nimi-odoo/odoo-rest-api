from odoo import fields, models, api


class BaseAutomationInherit(models.Model):
    _inherit = 'base.automation'
    _description = 'Automated Action'
    is_webhook = fields.Boolean(default=False, compute="_compute_is_webhook", store = True)
    webhook_subscriptions = fields.One2many(comodel_name="webhook_subscription", inverse_name="webhook", string="Subscriptions", required=False, )
    endpoint = fields.Many2one(comodel_name="rest.endpoint", string="Endpoint to fetch data from", required=False)
    logs = fields.One2many(comodel_name="webhook_log", inverse_name="webhook", string="Webhook log", required=False, readonly=True)

    @api.depends("state")
    def _compute_is_webhook(self):
        for action in self:
            action.is_webhook = (action.state == "webhook")

    @api.onchange('state')
    def _onchange_is_webhook(self):
        for action in self:
            action.is_webhook = (action.state == "webhook")

    def _process(self, records, domain_post=None):
        super(BaseAutomationInherit, self)._process(records, domain_post)

