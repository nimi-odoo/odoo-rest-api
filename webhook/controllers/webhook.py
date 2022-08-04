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

    @http.route('/webhook', auth="check_api_key", csrf= False, methods=["GET", "POST"])
    def webhook(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']
        headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Methods", "GET,POST")]
        if request_method == "GET":
            data = self.get()
        elif request_method == "POST":
            data = self.post(**kw)
        return request.make_response(json.dumps(data, default=str), headers)

    # Return client's existing webhooks.
    def get(self, **kw):
        uid = http.request.uid
        user = http.request.env['res.users'].search([('id', '=', uid)])
        user_webhook_subscriptions = user.webhook_subscriptions
        data = user_webhook_subscriptions.read(['id', 'webhook', 'webhook_url'])
        return data

    # Retrieve details of a client's existing webhook.
    def get_one(self, **kw):
        uid = http.request.uid
        user = http.request.env['res.users'].search([('id', '=', uid)])
        webhook_subscription = http.request.env['webhook_subscription'].search([('id','=',kw.get('id'))])
        data = webhook_subscription.read()
        return data

    def post(self, **kw):
        data = json.loads(http.request.httprequest.data)
        uid = http.request.uid
        webhook_url = data.get('webhook_url', None)
        webhook = data.get('webhook', None)
        if not data.get('subscriber'):
            data.update({'subscriber' : uid})
        try :
            request.env['webhook_subscription'].sudo().create(data)
        except ValueError:
            return RestController.response_400(RestController, ValueError)
        except:
            return RestController.response_400(RestController)
        return data

    def delete(self, **kw):
        uid = http.request.uid
        user = http.request.env['res.users'].search([('id', '=', uid)])
        webhook_subscription = http.request.env['webhook_subscription'].search([('id','=',kw.get('id'))])
        if not webhook_subscription:
            return False
        return webhook_subscription.unlink()

    # Update existing webhook subscription
    def update(self, **kw):
        data = json.loads(http.request.httprequest.data)
        uid = http.request.uid
        user = http.request.env['res.users'].search([('id', '=', uid)])
        webhook_subscription = http.request.env['webhook_subscription'].search([('id', '=', kw.get('id'))])
        if not webhook_subscription:
            return False
        return webhook_subscription.write(data)

    # Users have access only for their own webhook subscriptions.
    # Admins can access all webhook subscriptions.
    @http.route('/webhook/<int:id>', auth="check_api_key", csrf=False, methods=["GET", "DELETE", "UNLINK", "PUT", "PATCH", "OPTIONS"])
    def webhook_id(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']
        headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Methods", "GET,DELETE, PUT")]

        if request_method == "GET":
            data = self.get_one(**kw)
        elif request_method == "DELETE":
            data = self.delete(**kw)
        elif request_method == "PUT":
            data = self.update(**kw)
        if not data:
            return RestController.response_404(RestController, "Record not found. The path or id may not exist.")
        return request.make_response(json.dumps(data, default=str), headers)

    # Return all available webhook events.
    @http.route('/webhook/events', auth="check_api_key", csrf= False, methods=["GET"])
    def webhook_events(self, **kw):
        headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Methods", "GET")]
        data = request.env['base.automation'].sudo().search([('is_webhook','=',True)]).read(["id","display_name","trigger","model_name","endpoint"])
        return request.make_response(json.dumps(data, default=str), headers)
