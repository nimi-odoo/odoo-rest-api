# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.http import request
from odoo.exceptions import AccessError
from odoo import SUPERUSER_ID

import socket

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _auth_method_check_api_key(cls):
        is_admin = False
        # check if user was logged in
        if request.httprequest.session.uid:
            uid = request.httprequest.session.uid
            request.uid = uid
        else:
            api_key = request.httprequest.headers.get("Authorization") or request.params['Authorization']
            if not api_key:
                raise AccessError("Authorization header with API key missing")
            else:
                user_id = request.env['res.users.apikeys']._check_credentials( scope = "rpc", key = api_key )
                if not user_id :
                    raise AccessError("Invalid API Key")
                else:
                    request.uid = user_id

    def is_request_sent_from_server(self):
        hostName = request.httprequest.environ['HTTP_HOST'].split(":")[0] # host name requested by the client.
        if hostName == "localhost":
            return True
        return False
