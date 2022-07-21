from odoo import fields, models, api


class FieldWrapper(models.Model):
    _name = 'rest.field_wrapper'
    _description = 'ir.model.fields wrapper for rest api'

    endpoint = fields.Many2one(comodel_name="rest.endpoint", string="", required=False)
    field = fields.Many2one(comodel_name="ir.model.fields", string="", required=False,
                            domain = "[('model', '=', endpoint.specified_model_technical_name)]")
    wrapper_parent = fields.Many2one(comodel_name="rest.field_wrapper", string="wrapper_parent", required=False, )
    wrapper_children = fields.One2many(comodel_name="rest.field_wrapper", inverse_name="wrapper_parent", string="wrapper_children", required=False, )

    @api.onchange('endpoint')
    def test(self):
        for rec in self :
            print("ASD")