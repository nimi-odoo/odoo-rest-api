# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Session
import json

class SessionInherit(Session):
    @http.route('/web/session/authenticate', auth="none", csrf = False)
    def authenticate(self, db, login, password, base_location=None):
        request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()