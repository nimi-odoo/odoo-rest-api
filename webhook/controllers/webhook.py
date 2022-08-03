# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response

import json
import ast
from json.decoder import JSONDecodeError
from odoo.exceptions import ValidationError, UserError, AccessError


class Webhook(http.Controller):
    @http.route('/my/webhook/', type='http', auth="user", website=True)
    def MyWebhook(self, **post):
        return request.render("webhook.portal_my_webhook")

    def subscribe(self, uid, webhook_url, webhook_ids):
        webhook_ids = [(4,int(webhook_id)) for webhook_id in webhook_ids]
        vals = {
            'subscriber' : int(uid),
            'webhook_url' : webhook_url,
            'automated_actions' : webhook_ids
        }
        request.env['webhook_subscription'].sudo().create(vals)

    @http.route('/webhook', auth="public", csrf= False)
    def index(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']

