from odoo import fields, models, api


class FieldWrapper(models.Model):
    _name = 'rest.field_wrapper'
    _description = 'ir.model.fields wrapper for rest api'

    name = fields.Char(string = "Field Wrapper Name")
    endpoint = fields.Many2one(comodel_name="rest.endpoint", string="", required=False)
    field = fields.Many2one(comodel_name="ir.model.fields", string="", required=False)
    field_children = fields.Many2many(comodel_name="ir.model.fields", domain = "[('model','=',endpoint.specified_model_technical_name)]")


