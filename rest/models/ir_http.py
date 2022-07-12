# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.http import request
from odoo.exceptions import AccessError
from odoo import SUPERUSER_ID

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    # TODO :
    # change print() into raise()
    @classmethod
    def _auth_method_check_api_key(cls):

        uid = request.httprequest.session.uid
        is_admin = request.env['res.users'].search([('id', '=', uid)])._is_admin() # "res.users"._is_superuser() or "res.users".has_group('base.group_erp_manager')
        print("Is Admin? :", is_admin)
        if not is_admin:
            api_key = request.httprequest.headers.get("Authorization")
            if not api_key:
                raise AccessError("Authorization header with API key missing")
            else:
                user_id = request.env['res.users.apikeys']._check_credentials( scope="rpc", key=api_key)
                if not user_id :
                    raise AccessError("Invalid API Key")
                else:
                    request.uid = user_id
        else:
            request.uid = uid