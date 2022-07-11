# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response

import json
from odoo.exceptions import ValidationError, UserError, AccessError



class RestController(http.Controller):

    @http.route('/api/<string:str>/', auth="public", csrf= False)
    def index(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']
        headers = [("Content-Type", "application/json")]
        print("Headers\n", headers)

        # TODO:
        # Before we execute methods,
        # we need to check if current user(res.user or res.partner) has access
        # to the model he wants to access.

        # For GET method, we might want it to be available for everyone
        # For other methods, we can follow record rules or access rights.

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


    @http.route('/api/<string:str>/<int:id>', auth="public", csrf= False)
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
        # Added default = str
        # because json.dumps does not support for datetime type
        data = json.dumps(model_ids.read([field.name for field in api_fields]), default=str)
        return request.make_response(data, headers)


    def post(self, kw):
        headers = [("Content-Type", "application/json")]
        data = json.loads(http.request.httprequest.data)

        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return request.not_found("Page not found.\n Check your url path or the id you entered exists.")

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

    def remove(self, kw):
        headers = [("Content-Type", "application/json")]
        try:

            data = json.loads(http.request.httprequest.data)

            url_path = kw["str"]
            api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

            if not api.ids:
                return request.not_found("Page not found.\n Check your url path or the id you entered exists.")

            api_model = api.specified_model_id

            if not "id" in data:
                raise UserError(f"We need id")

            record_id_to_delete = data["id"]

            if isinstance(record_id_to_delete, str):
                if record_id_to_delete.isnumeric():
                    record_id_to_delete = int(record_id_to_delete)
            if not isinstance(record_id_to_delete, int):
                raise UserError(f"The id must be an integer.")

            record = request.env[api_model.model].search([('id','=',record_id_to_delete)])
            if not record:
                raise UserError(f"The id you entered does not exist in the model: {api_model.model}")
            else:
                record.unlink()
        except (UserError, ValidationError, AccessError, json.decoder.JSONDecodeError) as e:
            return self.response_400(str(e))

        return request.make_response(json.dumps({"message": "Succesfully delete a record."}), headers)

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
                raise UserError(f'You did not input id')
            record_id_to_update = data["id"]
            record = request.env[api_model.model].search([('id','=',record_id_to_update)])

            if not record:
                raise UserError(f'The id you entered does not exist in the model: {api_model.model}')
            else:
                for key, value in data.items():
                    current_field = http.request.env['ir.model.fields'].search([('model', '=', api_model.model), ('name', '=', key)])
                    if current_field.name:
                        # Following RESTful API convention
                        if (current_field.readonly or current_field.compute or current_field.name == "create_date") :
                            print("This attribute of the field will NOT be updated: ", current_field.name)
                        else:
                            record.write({current_field.name : value})
                            print("This attribute of the field will be updated field: ", current_field.name)

        except (UserError, ValidationError, AccessError) as e:
            return self.make_response_with_status_code(data = json.dumps({"message":str(e)}, default=str), status_code=400, headers=headers)
        else:
            return request.make_response(json.dumps({"message": "Succesfully updated a record."}), headers)


    def response_400(self, message="400 Bad Request", mimetype="text/plain"):
        return Response(response=message, status=400, mimetype=mimetype)

    def response_404(self, message="404 Not Found", mimetype="text/plain"):
        return Response(response=message, status=404, mimetype=mimetype)