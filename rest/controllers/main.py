# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class RestController(http.Controller):
    @http.route('/api/<string:str>', auth="public")
    def index(self, **kw):
        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])
        api_model = api.specified_model_id
        model_ids = http.request.env[api_model.model].search([])

        print(f"\napi {url_path} {api_model.name}\n")
        for m in model_ids:
            print(m.name)

        response = f"<h1>{api.name}</h1><p>Model: {api_model.name}</p><ul>"
        for m in model_ids:
            response += f"<li>{m.name}</li>"
        response += "</ul>"
        return(response)

