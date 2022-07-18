# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ChildrenWizard(models.TransientModel):
    _name = "children.wizard"
    _description = "MANN"
    fields_to_display = fields.Many2many(comodel_name="ir.model.fields", string="developer" )