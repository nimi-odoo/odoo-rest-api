# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.http import request
from odoo.exceptions import AccessError

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    # TODO :
    # change print() into raise()
    @classmethod
    def _auth_method_check_api_key(cls):
        api_key = request.httprequest.headers.get("Authorization")
        if not api_key:
            raise AccessError("Authorization header with API key missing")
        else:
            user_id = request.env['res.users.apikeys']._check_credentials( scope="rpc", key=api_key)
            if not user_id :
                raise AccessError("Invalid API Key")
            else:
                request.uid = user_id