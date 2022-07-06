# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Rest(models.Model):
    _name = "rest.endpoint"
    _description = "Odoo Rest API"

    name = fields.Char(string="API Name")
    base_url = fields.Char(string="Endpoint URL")
    specified_model_id = fields.Many2one(comodel_name="ir.model")
    model_path_url = fields.Char(string="Model Path", help="The models id in the URL", default=specified_model_id)
    specified_model_technical_name = fields.Char(related="specified_model_id.model", help="Technical name of the model")
    field_ids = fields.Many2many(comodel_name="ir.model.fields", domain="[('model', '=', specified_model_technical_name)]", help="Fields to be returned in the response")
    final_url = fields.Char(string="Final URL", compute="_compute_final_url", help="Computed final URL using the base URL and model path")


    @api.onchange("specified_model_id")
    def field_filter(self):
        for record in self:
            record.field_ids = [(5,0,0)] # Empty the field_ids Many2many field
            print(f"Model: {record.specified_model_id.model}");print(f'\n\n\n{record.specified_model_id.name}\n\n=== Fields ===');
            for f in record.field_ids: print(f.name, f.model);print("==============")

    @api.onchange("base_url")
    def append_forward_slash(self):
        for record in self:
            print(f"\n\nLast char: {record.base_url[-1]}\n")
            if record.base_url[-1] != "/":
                record.base_url += "/"

    @api.depends("base_url", "model_path_url")
    def _compute_final_url(self):
        for record in self:
            record.final_url = record.base_url + record.model_path_url
            print(f"\n\nUpdated Final URL: {record.final_url}\n")
