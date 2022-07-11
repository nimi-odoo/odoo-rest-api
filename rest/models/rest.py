# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Rest(models.Model):
    _name = "rest.endpoint"
    _description = "Odoo Rest API"

    name = fields.Char(string="API Name")
    base_url = fields.Char(string="Endpoint URL")
    specified_model_id = fields.Many2one(comodel_name="ir.model")
    model_path_url = fields.Char(string="Model Path", help="The models id in the URL")
    specified_model_technical_name = fields.Char(related="specified_model_id.model", help="Technical name of the model")
    field_ids = fields.Many2many(comodel_name="ir.model.fields", domain="[('model', '=', specified_model_technical_name)]", help="Fields to be returned in the response")
    required_field_ids = fields.Many2many(comodel_name="ir.model.fields", compute="_compute_required_fields", help="Fields required for creation of this model")
    final_url = fields.Char(string="Final URL", compute="_compute_final_url", help="Computed final URL using the base URL and model path")
    schema = fields.Text(string="Schema", compute="_compute_schema", help="Record schema")
    #removed ondelete param from schema


    @api.onchange("specified_model_id")
    def field_filter(self):
        for record in self:
            record.field_ids = [(5,0,0)] # Empty the field_ids Many2many field
            record.required_field_ids = [(5,0,0)]
            if record.specified_model_id and not record.model_path_url: # Set the Model Path to the model's name if none is already specified
                record.model_path_url = record.specified_model_id.name
                record.model_path_url = "".join(s.lower() for s in record.model_path_url.split(" ")) # Remove whitespace and make lowercase


    @api.onchange("base_url")
    def append_forward_slash(self):
        for record in self:
            if record.base_url:
                print(f"\n\nLast char: {record.base_url[-1]}\n")
                if record.base_url[-1] != "/":
                    record.base_url += "/"


    @api.depends("base_url", "model_path_url")
    def _compute_final_url(self):
        for record in self:
            if record.base_url and record.model_path_url:
                record.final_url = record.base_url + record.model_path_url
                print(f"\n\nUpdated Final URL: {record.final_url}\n")
            else:
                record.final_url = ""


    @api.depends("specified_model_id")
    def _compute_required_fields(self):
        for record in self:
            all_field_ids = self.env["ir.model.fields"].search([('model', '=', record.specified_model_technical_name)])
            record.required_field_ids = all_field_ids.filtered(lambda f: f["required"])
    

    @api.depends("required_field_ids", "field_ids")
    def _compute_schema(self):
        for record in self:
            build = "{\n"
            for required in record.required_field_ids:
                build += f'\t"{required.name}" : "Your_{required.ttype}_Data",\n'
            for field in record.field_ids:
                build +=f'\t"{field.name}" : "Your_{field.ttype}_Data",\n'
            build = build[:-2:] # Remove the last comma and newline
            build += "\n}"
            record.schema = build


    # @api.model
    # def default_get(self, fields=[]):
    #     print("getting, fields:")
    #     vars = super(Rest, self).default_get(fields)
    #     for v in vars: print(v)
