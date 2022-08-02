from odoo import fields, models, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class IrActionsServerInherit(models.Model):
    _inherit = "ir.actions.server"
    _description = 'Server Actions'

    state = fields.Selection(selection_add=[
        ('webhook', 'Webhook'),
    ], ondelete={'webhook': 'cascade'})

    def _run_action_webhook(self, eval_context = None):
        webhook = self.env['base.automation'].search([('action_server_id', '=', self.id)])
        webhook_subscriptions = webhook.webhook_subscriptions
        webhook_endpoint_path_url = webhook.endpoint.model_path_url
        webhook_endpoint_url = f'{self.env["ir.config_parameter"].sudo().get_param("web.base.url")}/api/{webhook_endpoint_path_url}'

        for webhook_subscription in webhook_subscriptions:
            try :
                api = self.env["rest.endpoint"].search([("model_path_url", "=", webhook_endpoint_path_url)])

                if not api.ids:
                    return self.response_404("Record not found. The path or id may not exist.")

                api_model = api.specified_model_id
                api_fields = api.field_ids
                model_ids = self.env[api_model.model].search([])
                data = json.dumps(model_ids.read([field.name for field in api_fields]), default=str)

                webhook_post = requests.post(webhook_subscription.webhook_url, data=data,
                                  headers={'Content-Type': 'application/json'})
            except:
                _logger.warning("Warning!!!!")