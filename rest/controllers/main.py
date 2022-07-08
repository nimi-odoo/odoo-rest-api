# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.http import Response
import json
from odoo.exceptions import ValidationError, UserError, AccessError


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
        elif request_method == "DELETE" or request_method == "UNLINK":
            return self.remove(kw)
        elif request_method == "PUT" or request_method == "PATCH":
            return self.update(kw)
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
        data = json.loads(http.request.httprequest.data)["data"]

        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return request.not_found("Page not found.\n Check your url path or the id you entered exists.")

        api_model = api.specified_model_id

        try:
            request.env[api_model.model].create(data)
        except ValueError:
            return request.make_response(json.dumps({"message" : ValueError}), headers)

        return request.make_response(json.dumps({"message" : "Succesfully created a record."}), headers)

    def remove(self, kw):
        headers = [("Content-Type", "application/json")]
        data = json.loads(http.request.httprequest.data)

        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return request.not_found("Page not found.\n Check your url path or the id you entered exists.")

        api_model = api.specified_model_id

        try:
            if not "id" in data:
                raise UserError(f'We need id')

            record_id_to_delete = data["id"]

            if isinstance(record_id_to_delete, str):
                if record_id_to_delete.isnumeric():
                    record_id_to_delete = int(record_id_to_delete)
            if not isinstance(record_id_to_delete, int):
                raise UserError(f'The id must be an integer.')

            record = request.env[api_model.model].search([('id','=',record_id_to_delete)])
            if not record:
                raise UserError(f'The id you entered does not exist in the model: {api_model.model}')
            else:
                record.unlink()
        except (UserError, ValidationError, AccessError) as e:
            return self.make_response_with_status_code(data = json.dumps({"message":str(e)}), status_code=400, headers=headers)
        else:
            return request.make_response(json.dumps({"message": "Succesfully delete a record."}), headers)



    # @data : a type of json.dumps( dictionary_object )
    def make_response_with_status_code(self, data, status_code = 400, headers=None, cookies=None):
        response = Response(data, headers=headers)
        response.status_code = status_code
        if cookies:
            for k, v in cookies.items():
                response.set_cookie(k, v)
        return response



    # Still working on
    def update(self, kw):
        headers = [("Content-Type", "application/json")]
        data = json.loads(http.request.httprequest.data)

        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return request.not_found("Page not found.\n Check your url path or the id you entered exists.")

        api_model = api.specified_model_id

        try:
            if not "id" in data:
                raise UserError(f'We need id')
            record_id_to_update = data["id"]
            record = request.env[api_model.model].search([('id','=',record_id_to_update)])

            if not record:
                raise UserError(f'The id you entered does not exist in the model: {api_model.model}')
            else:
                for key, value in data.items():
                    current_field = http.request.env['ir.model.fields'].search([('model', '=', 'res.partner'), ('name', '=', key)])

        except (UserError, ValidationError, AccessError) as e:
            return self.make_response_with_status_code(data = json.dumps({"message":str(e)}), status_code=400, headers=headers)
        else:
            return request.make_response(json.dumps({"message": "Succesfully delete a record."}), headers)