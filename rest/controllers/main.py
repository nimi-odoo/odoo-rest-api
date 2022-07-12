# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response

import json
from json.decoder import JSONDecodeError
from odoo.exceptions import ValidationError, UserError, AccessError


class RestController(http.Controller):
    @http.route('/api/<string:str>/', auth="check_api_key", csrf=False)
    # @http.route('/api/<string:str>/', auth="public", csrf= False)
    def index(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']

        try :
            if request_method == "GET":
                return self.get(**kw)
            elif request_method == "POST":
                return self.post(**kw)
            else:
                return self.response_404("Invalid request method")
        except (UserError, ValidationError, json.decoder.JSONDecodeError) as e:
            return self.response_400(str(e))
        except (AccessError) as e:
            return self.response_403(str(e))


    @http.route('/api/<string:str>/<int:id>', auth="public", csrf= False)
    def index_id(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']

        if request_method == "GET":
            return self.get_one(**kw)
        elif request_method == "DELETE" or request_method == "UNLINK":
            return self.delete_one(**kw)
        elif request_method == "PUT" or request_method == "PATCH":
            return self.update_one(**kw)
        else: 
            return self.response_404("Invalid request method")


    def get_one(self, **kw):
        headers = [("Content-Type", "application/json")]
        record_id = self.retrieve_record_id(**kw)
        if not record_id:
            return self.response_404("Record not found. The path or id may not exist.")
        data = self.retrieve_record_data(record_id, **kw)
        return request.make_response(data, headers)


    def delete_one(self, **kw):
        headers = [("Content-Type", "application/json")]
        record_id = self.retrieve_record_id(**kw)
        if not record_id:
            return self.response_404("Record not found. The path or id may not exist.")
        data = self.retrieve_record_data(record_id, **kw)
        record_id.unlink()
        return request.make_response(data, headers)


    def update_one(self, **kw):
        headers = [("Content-Type", "application/json")]
        try:
            update_data = json.loads(http.request.httprequest.data)
        except JSONDecodeError as e:
            return self.response_400(f"Invalid JSON formatting\n{e}")

        record_id = self.retrieve_record_id(**kw)
        if not record_id:
            return self.response_404("Record not found. The path or id may not exist.")
        model_id = http.request.env["rest.endpoint"].search([("model_path_url", "=", kw["str"])]).specified_model_id
        
        for key, value in update_data.items():
            print(key, value,'\n')
            current_field = http.request.env['ir.model.fields'].search([('model', '=', model_id.model), ('name', '=', key)])
            if current_field.name:
                if (current_field.readonly or current_field.compute or current_field.name == "create_date"):
                    return self.response_400(f"The field {current_field.name} can't be updated. It is either a readonly, computed or create_date field.")
                else:
                    record_id.write({current_field.name : value})
        record_data = self.retrieve_record_data(record_id, **kw)
        return request.make_response(record_data, headers)


    def get(self, **kw):
        headers = [("Content-Type", "application/json")]
        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return self.response_404("Record not found. The path or id may not exist.")

        api_model = api.specified_model_id
        api_fields = api.field_ids
        model_ids = http.request.env[api_model.model].search([])
        data = json.dumps(model_ids.read([field.name for field in api_fields]), default=str)
        return request.make_response(data, headers)


    def post(self, **kw):
        headers = [("Content-Type", "application/json")]
        try:
            data = json.loads(http.request.httprequest.data)
        except JSONDecodeError as e:
            return self.response_400(f"Invalid JSON formatting\n{e}")

        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return self.response_404("Record not found. The path or id may not exist.")

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
        except:
            return self.response_400()
        return request.make_response(json.dumps(data, default=str), headers)



    def response_400(self, body="400 Bad Request", mimetype="text/plain"):
        return Response(response=body, status=400, mimetype=mimetype)


    def response_404(self, body="404 Not Found", mimetype="text/plain"):
        return Response(response=body, status=404, mimetype=mimetype)


    def response_200(self, body="200 OK", mimetype="application/json"):
        return Response(response=body, status=200, mimetype=mimetype)


    def retrieve_record_id(self, **kw):
        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return False

        api_model = api.specified_model_id
        record_id = http.request.env[api_model.model].search([("id", "=", kw["id"])])

        if not record_id.id:
            return False
        return record_id

    
    def retrieve_record_data(self, record_id, **kw):
        url_path = kw["str"]
        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])
        api_fields = api.field_ids

        return (json.dumps(record_id.read([field.name for field in api_fields])[0], default=str))
