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
            headers = {"Authorization": "8b0138967140c765469a3d12a5c30a8bf77f46cb"}
            #TODO:
            #Get Real api key
            try :
                endpoint_response = requests.get( webhook_endpoint_url, headers )
                webhook_post = requests.post(webhook_subscription.webhook_url, data=json.dumps(json.loads(endpoint_response.text)),
                                  headers={'Content-Type': 'application/json'})
                print(webhook_post)
            except:
                _logger.warning("Warning!!!!")


