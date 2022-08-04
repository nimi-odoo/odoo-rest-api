# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RestField(models.Model):
    _name = "rest.field"
    _description = "Rest field"

    name = fields.Char(string="Field Name")
    ir_field_id = fields.Many2one(comodel_name="ir.model.fields")
    model_id = fields.Many2one(comodel_name="ir.model")
    model_technical_name = fields.Char(help="Technical name of the model")

    children_field_ids = fields.Many2many(string="Nested fields", comodel_name="ir.model.fields", domain="[('model', '=', model_technical_name)]")
    nested_fields = fields.Many2many(string="Nested Rest Fields", comodel_name="rest.field", relation="nested_field", column1="nested_fields", column2="rest_fields", compute="_compute_nested_fields", store=True)
    rest_fields = fields.Many2many(string="temp", comodel_name="rest.field", relation="nested_fields", column1="rest_fields", column2="nested_fields") # Not used for anything, only here so nested_fields can have a separate column in the table


    @api.depends("children_field_ids")
    def _compute_nested_fields(self):
        print("\n\nCOMPUTING NESTED FIELDS\n")
        for record in self:
            if not record.children_field_ids.ids:
                record.nested_fields = False

            for f in record.children_field_ids:
                nested_field_names = [nf.name for nf in record.nested_fields]
                if f.ttype in ("many2one", "many2many") and f.name not in nested_field_names and not isinstance(record.id, models.NewId):
                    model = self.env["ir.model"].search([('model', '=', f.relation)])
                    vals = {
                        "name": f.name,
                        "ir_field_id": f.id,
                        "model_id": model.id,
                        "model_technical_name": model.model
                    }
                    print(f"Created Lower-Level Rest Field {f.name}")
                    record.nested_fields = [(0,0,vals)]

            for field in record.nested_fields:
                ir_field_ids = [f.name for f in record.children_field_ids]
                if field.name not in ir_field_ids:
                    print(f"\nUnlinking lower-rest field: {field.name}")
                    field.unlink()


    def action_save(self):
        print("\nSAVING\n")
        for record in self: 
            for f in record.nested_fields:
                print("saved", f.name, "\t", f.model_technical_name, f"\tModel: {f.model_id.model}")


    # def unlink(self):
    #     """
    #     When a user deletes a field from children_field_ids (ir.model.fields), delete the associated field in nested_fields (rest.field)
    #     """
    #     for rec in self:
    #         for field in rec.nested_fields:
    #             if field.name not in [f.name for f in rec.children_field_ids]:
    #                 print(f"Unlinking Lower-level Rest Field {f.name}")
    #                 field.unlink()

    #     return super().unlink()