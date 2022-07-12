# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.http import request
from odoo.exceptions import AccessError
from odoo import SUPERUSER_ID

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"
    @classmethod
    def _auth_method_check_api_key(cls):
        is_admin = False
        if request.httprequest.session.uid:
            uid = request.httprequest.session.uid
            request.uid = uid # Move login information from odoo to our http.request

            # "res.users"._is_superuser() or "res.users".has_group('base.group_erp_manager')
            # This is for later reference, it is not in use currently.
            is_admin = request.env['res.users'].search([('id', '=', uid)])._is_admin()
        else:
            api_key = request.httprequest.headers.get("Authorization")
            if not api_key:
                raise AccessError("Authorization header with API key missing")
            else:
                user_id = request.env['res.users.apikeys']._check_credentials( scope="rpc", key=api_key)
                if not user_id :
                    raise AccessError("Invalid API Key")
                else:
                    request.uid = user_id
