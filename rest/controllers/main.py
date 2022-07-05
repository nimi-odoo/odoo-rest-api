# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class RestController(http.Controller):
    @http.route('/api_endpoint', auth="public")
    def index(self, **kw):
        response = "<ul>"
        # all_items = http.request.env["rest"].model.search([])
        # for item in all_items:
        #     print(item)
        print("\n\n\ntest\n\n\n")
        model_ids = http.request.env["ir.model"].search([])
        for m in model_ids:
            response += f"<li>{m.name}</li>"
        response += "</ul>"
        return(response)


