# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response

import json
from json.decoder import JSONDecodeError
from odoo.exceptions import ValidationError, UserError, AccessError


class Webhook(http.Controller):
    @http.route('/my/webhook/', type='http', auth="user", website=True)
    def index(self):
        return request.render("webhook.portal_my_webhook", {})