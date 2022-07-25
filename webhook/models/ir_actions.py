from odoo import fields, models, api


class IrActionsServerInherit(models.Model):
    _inherit = "ir.actions.server"
    _description = 'Server Actions'

    state = fields.Selection(selection_add=[
        ('webhook', 'Webhook'),
    ], ondelete={'webhook': 'cascade'})



