# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

import json
from werkzeug.wrappers import Request, Response

class RestController(http.Controller):
    @http.route('/api/<string:str>', auth="public")
    def index(self, **kw):
        # headers = {"Content-Type":"application/json"}
        headers = [("Content-Type", "application/json")]
        print(headers)

        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])
        api_model = api.specified_model_id
        api_fields = api.field_ids
        model_ids = http.request.env[api_model.model].search([])

        print(f"\napi {url_path} {api_model.name}\n")
        # for m in model_ids:
        #     print(m.name)

        for field in api_fields:
            print(field.name)
        data = json.dumps(model_ids.read([field.name for field in api_fields]))
        return request.make_response(data, headers)
        # return Response(json.dumps(model_ids.read(["name"])), headers=headers)

        # response = f"<h1>{api.name}</h1><p>Model: {api_model.name}</p><ul>"
        # for m in model_ids:
        #     response += f"<li>{m.name}</li>"
        # response += "</ul>"
        # return(response)

    def pack_data(self):
        pass