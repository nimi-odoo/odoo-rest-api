# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

from werkzeug.wrappers import Response
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


    def post(self, kw):
        headers = [("Content-Type", "application/json")]
        data = json.loads(http.request.httprequest.data)

        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])
        api_model = api.specified_model_id
        api_fields = api.field_ids
        post_fields = data.keys()

        all_field_ids = http.request.env["ir.model.fields"].search([('model', '=', api_model.model)])
        required_fields = [f for f in all_field_ids if f["required"]]
        unfulfilled_required_fields = [f for f in required_fields if f.name not in post_fields]
        required_field_names = [f.name for f in required_fields]
        default_fields = http.request.env[api_model.model].default_get(required_field_names)

        unfulfilled_needed_fields = [f for f in unfulfilled_required_fields if f.name not in default_fields]
        if unfulfilled_needed_fields:
            return self.response_400(f"The following fields are required: {[f.name for f in unfulfilled_needed_fields]}")

        try:
            request.env[api_model.model].create(data)
        except ValueError:
            return self.response_400(ValueError)
        return request.make_response(json.dumps(data), headers)




    def response_400(self, message="400 Bad Request", mimetype="text/plain"):
        return Response(response=message, status=400, mimetype=mimetype)

    def response_404(self, message="404 Not Found", mimetype="text/plain"):
        return Response(response=message, status=404, mimetype=mimetype)


