# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response

import json
from json.decoder import JSONDecodeError
from odoo.exceptions import ValidationError, UserError, AccessError


class RestController(http.Controller):
    @http.route('/api/<string:str>/', auth="check_api_key", csrf=False, cors="*")
    # @http.route('/api/<string:str>/', auth="public", csrf= False)
    def index(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']
        try:
            if request_method == "GET":
                return self.get(**kw)
            elif request_method == "POST":
                return self.post(**kw)
            elif request_method =="OPTIONS":
                pass
            else:
                return self.response_404("Invalid request method")

        except (UserError, ValidationError) as e:
            return self.response_400(str(e))
        except JSONDecodeError as e:
            return self.response_400(f"Invalid JSON formatting\n{e}")
        except (AccessError) as e:
            return self.response_403(str(e))


    @http.route('/api/<string:str>/<int:id>', auth="check_api_key",csrf= False, cors="*",methods=["GET", "POST", "DELETE", "UNLINK", "PUT", "PATCH", "OPTIONS"])
    def index_id(self, **kw):
        request_method = http.request.httprequest.headers.environ['REQUEST_METHOD']
        try:
            if request_method == "GET":
                return self.get_one(**kw)
            elif request_method == "DELETE" or request_method == "UNLINK":
                return self.delete_one(**kw)
            elif request_method == "PUT" or request_method == "PATCH":
                return self.update_one(**kw)
            elif request_method =="OPTIONS":
                pass
            else: 
                return self.response_404("Invalid request method")

        except (UserError, ValidationError) as e:
            return self.response_400(str(e))
        except JSONDecodeError as e:
            return self.response_400(f"Invalid JSON formatting\n{e}")
        except (AccessError) as e:
            return self.response_403(str(e))


    def get_one(self, **kw):
        headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Methods", "GET,POST,DELETE")]
        record_id = self.retrieve_record_id(**kw)
        if not record_id:
            return self.response_404("Record not found. The path or id may not exist.")
        data = self.retrieve_record_data(record_id, **kw)
        return request.make_response(data, headers)


    def delete_one(self, **kw):
        headers = [("Content-Type", "application/json")]
        record_id = self.retrieve_record_id(**kw)
        if not record_id:
            return self.response_204("Record not found. The record may have already been deleted or the path and id may not exist.")
        data = self.retrieve_record_data(record_id, **kw)
        record_id.unlink()
        return request.make_response(data, headers)


    def update_one(self, **kw):
        headers = [("Content-Type", "application/json")]
        update_data = json.loads(http.request.httprequest.data)

        record_id = self.retrieve_record_id(**kw)
        if not record_id:
            return self.response_404("Record not found. The path or id may not exist.")
        model_id = http.request.env["rest.endpoint"].search([("model_path_url", "=", kw["str"])]).specified_model_id
        
        for key, value in update_data.items():
            current_field = http.request.env['ir.model.fields'].search([('model', '=', model_id.model), ('name', '=', key)])
            if current_field.name:
                if (current_field.readonly or current_field.compute or current_field.name == "create_date"):
                    return self.response_400(f"The field {current_field.name} can't be updated. It is either a readonly, computed or create_date field.")
                else:
                    record_id.write({current_field.name : value})
        record_data = self.retrieve_record_data(record_id, **kw)
        return request.make_response(record_data, headers)


    def get(self, **kw):
        headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Methods", "GET,POST,DELETE")]
        url_path = kw["str"]
        search_domain = []
        params = self.convert_dict_to_domain(http.request.params, **kw)
        search_type = "="

        for p in params:
            if p[0] == "search_type":
                search_type = p[2]
            else:
                search_domain.append(p)

        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return self.response_404("Record not found. The path or id may not exist.")

        api_model = api.specified_model_id
        api_fields = api.field_ids
        model_ids = http.request.env[api_model.model].search(search_domain)
        
        data = json.dumps(model_ids.read([field.name for field in api_fields]), default=str)
        return request.make_response(data, headers)


    def post(self, **kw):
        headers = [("Content-Type", "application/json")]
        data = json.loads(http.request.httprequest.data)

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

    
    def convert_dict_to_domain(self, params, **kw):
        domain = []
        search_type = "=ilike"
        if (params.get("search_type")):
            search_type = params.get("search_type")

        for k,v in params.items():
            if not k or not v:
                if not k: raise UserError("Parameter must have a key")
                if not v: raise UserError("Parameter must have a value")
            if self.is_field_computed_and_nonstored(k, **kw):
                raise UserError(f"Non-stored field {k} can't be searched")
            if k == "search_type":
                continue
            
            param_type = self.retrieve_param_type(k, **kw)
            
            if param_type in ("integer", "many2one"):
                domain.append((k, "=", int(v)))

            elif param_type == "boolean":
                if v in ("False", "0"):
                    v = False
                domain.append((k, "=", bool(v)))

            elif param_type in ("float", "monetary"):
                domain.append((k, "=", float(v)))

            elif param_type == "one2many":
                domain = self.field_to_domain_many2many(domain, k, v)

            elif param_type == "many2many":
                domain = self.field_to_domain_many2many(domain, k, v)

            else:
                domain.append((k, search_type, v))

        return domain


    def retrieve_param_type(self, param, **kw):
        api_fields = http.request.env["rest.endpoint"].search([("model_path_url", "=", kw["str"])]).field_ids
        param_type = "char"
        for f in api_fields:
            if f.name == param:
                param_type = f.ttype
        return param_type


    def field_to_domain_one2many(self, domain, key, value):
        record_ids = value.replace("[","").replace("]", "").strip().split(",")
        one2many_array = [int(record_id) for record_id in record_ids if record_id]
        domain.append((key, "=", one2many_array))
        return domain


    def field_to_domain_many2many(self, domain, key, value):
        record_ids = value.replace("[","").replace("]", "").strip().split(",")
        many2many_array = [int(record_id) for record_id in record_ids if record_id]
        for i in range(0, len(many2many_array)):
            if i % 2 == 0 and i < len(many2many_array) - 1:
                domain.append("&")
            domain.append((key, "in", many2many_array[i]))
        return domain


    def is_field_computed_and_nonstored(self, field_name, **kw):
        api_fields = http.request.env["rest.endpoint"].search([("model_path_url", "=", kw["str"])]).field_ids
        for f in api_fields:
            if f.name == field_name:
                model = http.request.env[f.model]
                field = model._fields.get(f.name)
                if not field.store and not field.search:
                    return True  
        return False


    def response_204(self, body="204 No Content", mimetype="text/plain"):
        return Response(response=body, status=404, mimetype=mimetype)


    def response_400(self, body="400 Bad Request", mimetype="text/plain"):
        return Response(response=body, status=400, mimetype=mimetype)


    def response_403(self, body="403 Forbidden", mimetype="text/plain"):
        return Response(response=body, status=403, mimetype=mimetype)


    def response_404(self, body="404 Not Found", mimetype="text/plain"):
        return Response(response=body, status=404, mimetype=mimetype)
