# -*- coding: utf-8 -*-

from odoo import api, fields, models

import json


class Rest(models.Model):
    _name = "rest.endpoint"
    _description = "Odoo Rest API"

    name = fields.Char(string="API Name")
    specified_model_id = fields.Many2one(comodel_name="ir.model")
    model_path_url = fields.Char(string="Model Path", help="The models id in the URL")
    specified_model_technical_name = fields.Char(related="specified_model_id.model", help="Technical name of the model")

    field_ids = fields.Many2many(comodel_name="ir.model.fields", domain="[('model', '=', specified_model_technical_name)]", help="Fields to be returned in the response")
    rest_field_ids = fields.Many2many(comodel_name="rest.field", compute="_compute_rest_fields", store=True)

    required_field_ids = fields.Many2many(comodel_name="ir.model.fields", compute="_compute_required_fields", help="Fields required for creation of this model")
    endpoint_url = fields.Char(string="Endpoint URL", compute="_compute_endpoint_url", help="Computed endpoint URL using the model path name")
    schema = fields.Text(string="Schema", compute="_compute_schema", help="Record schema")
    search_type = fields.Char(string="Search Type", default="=ilike", help="Criteria for which records are returned on a search")

    _sql_constraints = [
        ("model_path_url", "UNIQUE(model_path_url)", "URL paths must be unique")
    ]

    filter_domain = fields.Char(string='Domain applied on',
                                help="If present, only those records satisfying the domain will be returned.")

    @api.onchange("specified_model_id")
    def field_filter(self):
        for record in self:
            record.field_ids = [(5,0,0)] # Empty the field_ids Many2many field
            record.required_field_ids = [(5,0,0)]

            if record.specified_model_id and not record.model_path_url: # Set the Model Path to the model's name if none is already specified
                default_name = "".join(s.lower() for s in record.specified_model_id.name.split(" ")) # Take the model's name, remove whitespace and make lowercase
                path_name = default_name
                endpoint_ids = self.env["rest.endpoint"].search([])
                endpoint_urls = [endpoint.model_path_url for endpoint in endpoint_ids]
                while path_name in endpoint_urls:
                    if len(path_name) == len(default_name):
                        path_name = f"{path_name}1"
                    else:
                        try:
                            number = int(path_name[len(default_name)::])
                            path_name = f"{path_name[:len(default_name):]}{number+1}"
                        except:
                            print("\n\nsomething bad happened while generating the model_path_url\n\n")
                            break
                record.model_path_url = path_name


    @api.depends("model_path_url")
    def _compute_endpoint_url(self):
        for record in self:
            record.endpoint_url = f"/api/{record.model_path_url}"


    @api.depends("specified_model_id")
    def _compute_required_fields(self):
        for record in self:
            all_field_ids = self.env["ir.model.fields"].search([('model', '=', record.specified_model_technical_name)])
            record.required_field_ids = all_field_ids.filtered(lambda f: f["required"])
    

    @api.depends("field_ids", "rest_field_ids")
    def _compute_schema(self):
        for record in self:
            data = self.build_text(record.field_ids, record.rest_field_ids)
            record.schema = json.dumps(data, indent=4)


    def build_text(self, all_ir_fields, nested_fields):
        data = {}
        for field in nested_fields:
            if field.ir_field_id.ttype in ("many2many", "many2one"):
                data[field.name] = self.build_text(field.children_field_ids, field.nested_fields)

            elif field.ir_field_id.ttype == "one2many":
                data[field.name] = [(self.build_text(field.children_field_ids, field.nested_fields))]

        
        normal_fields = [f for f in all_ir_fields if f.ttype not in ("many2one", "many2many", "one2many")]
        for field in normal_fields:
            data[field.name] = f"Your_{field.ttype}_data"
            
        return data
            

    @api.depends("field_ids")
    def _compute_rest_fields(self):
        for record in self:
            if not record.field_ids.ids:
                record.rest_field_ids = False    

            for f in record.field_ids:
                nested_field_names = [nf.name for nf in record.rest_field_ids]
                if f.ttype in ("many2one", "many2many", "one2many") and f.name not in nested_field_names and not isinstance(record.id, models.NewId):
                    if f.ttype == "one2many": print(f"one2many relation: {f.relation}")
                    model = self.env["ir.model"].search([('model', '=', f.relation)])
                    vals = {
                        "ir_field_id": f.id,
                        "name": f.name,
                        "model_id": model.id,
                        "model_technical_name": f.relation
                    }
                    record.rest_field_ids = [(0,0,vals)]

            for field in record.rest_field_ids:
                ir_field_ids = [f.name for f in record.field_ids]
                if field.name not in ir_field_ids:
                    field.unlink()
