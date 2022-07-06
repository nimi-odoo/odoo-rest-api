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

    @api.model
    def create(self, vals):
        # When user confirms creating the api endpoint,
        # we will make the api endpoint.
        template = 'website_studio.default_form_page'
        model_id = vals["specified_model_id"]
        fields = vals["field_ids"]
        new_page = self.env['website'].new_page(
            name = "api/Test",
            add_menu = False,
            ispage = True,
            namespace = "website",
        )
        print(new_page)
        # new_page['url'] = xml_id of the website
        return super().create(vals)