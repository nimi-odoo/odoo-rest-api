# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response

import json
import ast
from json.decoder import JSONDecodeError
from odoo.exceptions import ValidationError, UserError, AccessError


class RestController(http.Controller):

    @http.route('/api/swagger', type="http", auth="public", csrf=False, cors="*")
    def swagger(self, **kw):
        endpoints = http.request.env["rest.endpoint"].sudo().search([])
        values = {"endpoints" : endpoints}
        return request.render("rest.rest_swagger", values)

    @http.route('/api/<string:str>/', auth="check_api_key", csrf=False, cors="*")
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

        for p in params:
            search_domain.append(p)

        api = http.request.env["rest.endpoint"].search([("model_path_url", "=", url_path)])

        if not api.ids:
            return self.response_404("Record not found. The path or id may not exist.")

        api_model = api.specified_model_id

        if api.filter_domain == False or api.filter_domain == "":
            model_ids = http.request.env[api_model.model].search(search_domain)
        else:
            model_ids = http.request.env[api_model.model].search(ast.literal_eval(api.filter_domain) + search_domain)

        data = self.compute_response_data(model_ids, api.field_ids, api.rest_field_ids)
        
        return request.make_response(json.dumps(data, default=str), headers)


    def compute_response_data(self, records, all_ir_fields, nested_fields):
        output = []
        normal_fields = [f for f in all_ir_fields if f.ttype not in ("many2one", "many2many", "one2many")]

        for record in records:
            data = {}
            if normal_fields:
                data = record.read([f.name for f in normal_fields])[0] # Read non-m2x fields from a single record

            for field in nested_fields:
                if field.ir_field_id.ttype in ("many2one", "many2many"):
                    record_id = http.request.env[field.model_id.model].search([("id", "=", record[field.name].id)]) # Get the record that the relation is pointing to
                    data[field.name] = self.process_child(record_id, field.children_field_ids, field.nested_fields) # Begin obtaining data recursively
                elif field.ir_field_id.ttype == "one2many":
                    record_ids = http.request.env[field.ir_field_id.relation].search([("id", "in", record[field.name].ids)])
                    o2m_data = self.compute_response_data(record_ids, field.children_field_ids, field.nested_fields)
                    data[field.name] = o2m_data

            if data:
                output.append(data)

        return output


    def process_child(self, record, children_field_ids, nested_fields):
        """
        Recursive function for reading data from nested fields.
        Each m2x field has its name as a key and its value is all its nested fields in a dict.
        Base cases: 
            Record doesn't exist or no nested fields are specified -> return empty dict
            Only non-m2x fields are in nested fields -> return dict in format {field_name: value,}
        """
        if not record: return {}

        normal_fields = [f for f in children_field_ids if f.ttype not in ("many2one", "many2many", "one2many")]
        m2x_fields = [f for f in nested_fields if f.ir_field_id.ttype in ("many2one", "many2many")]

        data = {}
        if normal_fields:
            data = record.read([f.name for f in normal_fields])[0]
        if m2x_fields:
            for f in m2x_fields:
                record_id = http.request.env[f.model_id.model].search([("id", "=", record[f.name].id)])
                data[f.name] = self.process_child(record_id, f.children_field_ids, f.nested_fields)

        return data


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



