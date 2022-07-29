from odoo import fields, models, api


class RestEndpointInherit(models.Model):
    _inherit = 'rest.endpoint'
    _description = 'Description'

    webhooks = fields.One2many(comodel_name="base.automation", inverse_name="endpoint", string="Automated actions subscribed to this endpoint", required=False )
