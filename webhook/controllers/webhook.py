# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response
from odoo.exceptions import ValidationError, UserError, AccessError

from odoo.addons.rest.controllers.main import RestController

import json
import ast
from json.decoder import JSONDecodeError



class Webhook(http.Controller):
    @http.route('/my/webhook/', type='http', auth="user", website=True)
    def my_webhook(self, **post):
        return request.render("webhook.portal_my_webhook")

    # TODO:
    # delete below function after checking this is not used.

    # def subscribe(self, uid, webhook_url, webhook_ids):
    #     webhook_ids = [(4,int(webhook_id)) for webhook_id in webhook_ids]
    #     vals = {
    #         'subscriber' : int(uid),
    #         'webhook_url' : webhook_url,
    #         'automated_actions' : webhook_ids
    #     }
    #     try:
    #         request.env['webhook_subscription'].sudo().create(vals)
    #     except Exception as e:
    #         print(e)

    @http.route('/webhook', auth="check_api_key", csrf= False)
    def webhook(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']
        headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Methods", "GET,POST,DELETE")]
        if request_method == "GET":
            data = self.get()
        elif request_method == "POST":
            data = self.post(**kw)
        return request.make_response(json.dumps(data, default=str), headers)

    def get(self, **kw):
        uid = http.request.uid
        user = http.request.env['res.users'].search([('id', '=', uid)])
        user_webhook_subscriptions = user.webhook_subscriptions
        data = user_webhook_subscriptions.read(['id', 'webhook', 'webhook_url'])
        return data

    def post(self, **kw):
        data = json.loads(http.request.httprequest.data)
        uid = http.request.uid
        webhook_url = data.get('webhook_url', None)
        webhook = data.get('webhook', None)
        vals = {'subscriber' : uid, 'webhook' : webhook, 'webhook_url' : webhook}
        try :
            request.env['webhook_subscription'].sudo().create(vals)
        except ValueError:
            data = RestController.response_400(RestController, ValueError)
        except:
            data = RestController.response_400(RestController)
        return data

    @http.route('/webhook/<int:id>', auth="check_api_key", csrf=False,methods=["GET", "POST", "DELETE", "UNLINK", "PUT", "PATCH", "OPTIONS"])
    def webhook_id(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']
        headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Methods", "GET,POST,DELETE")]
        if request_method == "GET":
            data = self.get()
        elif request_method == "POST":
            data = self.post()
        return request.make_response(json.dumps(data, default=str), headers)

