# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Rest(models.Model):
    _name = "rest.endpoint"
    _description = "Odoo Rest API"

    name = fields.Char(string="API Name")
    base_url = fields.Char(string="URL")
    specified_model_id = fields.Many2one(comodel_name="ir.model")
    specified_model_model = fields.Char(related="specified_model_id.model")
    field_ids = fields.Many2many(comodel_name="ir.model.fields", domain="[('model', '=', specified_model_model)]")


    @api.onchange("specified_model_id")
    def field_filter(self):
        for record in self:
            print(f"Model: {record.specified_model_id.model}");print(f'\n\n\n{record.specified_model_id.name}\n\n=== Fields ===');
            for f in record.field_ids: print(f.name, f.model);print("==============")
