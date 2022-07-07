# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

import json

class RestController(http.Controller):
    @http.route('/api/<string:str>/', auth="user", csrf= False)
    def index(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']
        headers = [("Content-Type", "application/json")]
        print("Headers\n", headers)

        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return request.not_found("Page not found.\n Check your url path or the id you entered exists.")

        api_model = api.specified_model_id
        api_fields = api.field_ids
        model_ids = http.request.env[api_model.model].search([])

        print(f"\napi {url_path} {api_model.name}\n")
        # for m in model_ids:
        #     print(m.name)
        # for field in api_fields:
        #     print(field.name)

        data = json.dumps(model_ids.read([field.name for field in api_fields]))
        return request.make_response(data, headers)

    @http.route('/api/<string:str>/<int:id>', auth="user", csrf= False)
    def get_one(self, **kw):
        headers = [("Content-Type", "application/json")]
        print("Headers\n", headers)

        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return request.not_found("Page not found.\n Check your url path or the id you entered exists.")

        api_model = api.specified_model_id
        api_fields = api.field_ids
        model_id = http.request.env[api_model.model].search([("id", "=", kw["id"])])

        if not model_id.id:
            return request.not_found("Page not found.\n Check your url path or the id you entered exists.")


        data = json.dumps(model_id.read([field.name for field in api_fields]))
        return request.make_response(data, headers)

