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

        if request_method == "GET":
            return self.get(kw)
        elif request_method == "POST":
            return self.post(kw)
        else:
            print("WHY")
        return self.get(kw)

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


    def get(self, kw):
        headers = [("Content-Type", "application/json")]
        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return request.not_found("Page not found.\n Check your url path or the id you entered exists.")

        api_model = api.specified_model_id
        api_fields = api.field_ids
        model_ids = http.request.env[api_model.model].search([])

        data = json.dumps(model_ids.read([field.name for field in api_fields]))
        return request.make_response(data, headers)


    # @data : http.request.httprequest.data
    # Just a stream of bytes
    def post(self, kw):
        headers = [("Content-Type", "application/json")]
        data = json.loads(http.request.httprequest.data)["data"]

        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])
        api_model = api.specified_model_id

        try:
            request.env[api_model.model].create(data)
        except ValueError:
            return request.make_response(json.dumps({"message" : ValueError.args[0]}), headers)

        return request.make_response(json.dumps({"message" : "Succesfully created a record."}), headers)



