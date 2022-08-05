from odoo import fields, models, api

import requests
import json
import logging

from odoo.addons.rest.controllers.main import RestController

_logger = logging.getLogger(__name__)

#TODO:
#Exception handling for different exceptions..
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
                model_ids = self.env[api_model.model].search([])
                data = RestController.compute_response_data(RestController, model_ids, api.field_ids, api.rest_field_ids)

                response = requests.post(webhook_subscription.webhook_url, data=json.dumps(data, default=str),
                                  headers={'Content-Type': 'application/json'})

                webhook_log_response_header = response.headers
                webhook_log_response_body = response.content
                webhook_log_request_header = response.request.headers
                webhook_log_request_body = json.dumps(json.loads(response.request.body), indent=2,sort_keys=True)
                webhook_log_status_code = response.status_code
            except Exception as e:
                webhook_log_response_header = ""
                webhook_log_response_body = e
                webhook_log_request_header = e.request.headers
                webhook_log_request_body = json.dumps(json.loads(e.request.body), indent=2,sort_keys=True)
                webhook_log_status_code = "400"


            webhook_log_webhook_subscription = webhook_subscription.id

            webhook_log_vals = {
                "webhook_subscription": webhook_log_webhook_subscription,
                "response_header": webhook_log_response_header,
                "response_body": webhook_log_response_body,
                "request_header": webhook_log_request_header,
                "request_body": webhook_log_request_body,
                "status_code" : webhook_log_status_code
            }
            self.env['webhook_log'].sudo().create(webhook_log_vals)
