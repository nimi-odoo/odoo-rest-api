# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response

import json
import ast
from json.decoder import JSONDecodeError
from odoo.exceptions import ValidationError, UserError, AccessError


#TODO:
#display errors
#When user didn't choose webhook
#When user didn't input webhook_url
class Webhook(http.Controller):
    @http.route('/my/webhook/', type='http', auth="user", website=True, methods=['GET', 'POST'])
    def index(self, **post):
        webhooks = request.env['base.automation'].sudo().search([('is_webhook','=','True')])
        webhook_subscriptions = request.env.user.webhook_subscriptions
        selected_webhooks = []
        values = {"webhooks" : webhooks, "webhook_subscriptions" : webhook_subscriptions, "selected_webhooks" : []}

        if request.httprequest.method == "POST":
            if "submit" in post:
                uid = post.get('uid').strip()
                webhook_url = post.get('webhook_url').strip()

                if 'previous_selected_webhooks' in post and post.get('previous_selected_webhooks') != "":
                    previous_selected_webhooks = ast.literal_eval(post.get('previous_selected_webhooks'))
                else:
                    previous_selected_webhooks = []

                if webhook_url == "" or previous_selected_webhooks == []:
                    raise ValidationError("Please fill all field.")
                else:
                    self.subscribe(uid, webhook_url, previous_selected_webhooks)
            else:
                # selected_webhooks = post.get(selected_webhooks)
                # update subscriptions... with current id...
                if "addRow" in post:
                    if 'previous_selected_webhooks' in post and post.get('previous_selected_webhooks') != "":
                        previous_selected_webhooks = ast.literal_eval(post.get('previous_selected_webhooks'))
                    else:
                        previous_selected_webhooks = []
                    previous_selected_webhooks.append(post['webhook_id'])
                    updated_webhooks = webhooks.search([('is_webhook','=','True'),('id','not in', previous_selected_webhooks)])
                    values['webhooks'] = updated_webhooks
                    values["selected_webhooks"] = previous_selected_webhooks
                elif "deleteRow" in post:
                    print(post)


        return request.render("webhook.portal_my_webhook", values, headers={
            'X-Frame-Options': 'DENY'
        })
    def subscribe(self, uid, webhook_url, webhook_ids):
        webhook_ids = [(4,int(webhook_id)) for webhook_id in webhook_ids]
        vals = {
            'subscriber' : int(uid),
            'webhook_url' : webhook_url,
            'automated_actions' : webhook_ids
        }
        request.env['webhook_subscription'].sudo().create(vals)
