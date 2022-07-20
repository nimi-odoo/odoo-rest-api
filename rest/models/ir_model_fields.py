from odoo import fields, models, api
from odoo.exceptions import ValidationError

import ast

class IrModelFieldsInherit(models.Model):
    _inherit = "ir.model.fields"
    _description = 'Description'

    button_domain = fields.Boolean(compute = "_compute_button_domain")
    path = fields.Char(string="Path to get to current field", required=False, default = "", compute = "_compute_path", readonly=True)
    # parent = fields.One2many(comodel_name="ir.model.fields", inverse_name="children", string="Parent", required=False,readonly = False )
    # children = fields.Many2one(comodel_name="ir.model.fields", string="Children", required=False, readonly = False )

    def _compute_path(self):
        self.path = self._context.get('path', "")

    def _compute_button_domain(self):
        for rec in self:
            if rec.ttype in ["many2one","many2many","one2many"]:
                rec.button_domain = True
            else:
                rec.button_domain = False

    def is_visited(self, model_name):
        path_set = set(self.path.split(">"))
        if model_name in path_set:
            return True
        return False

    def children_show(self, **args):
        model_id = self.env['ir.model'].search([('model','=',self.relation)])
        domain = [('model_id','=',model_id.id)]
        # if self.is_visited(self.relation):
        #     raise ValidationError("The same model can only be added once")
        # else:
            # self.env['ir.config_parameter'].sudo().set_param('current_field', self.id)
        if "params" in self._context:
            rest_current_endpoint_id = self._context['params']['id']
        else:
            rest_current_endpoint_id = self._context['default_endpoint_id']
        self.env['ir.config_parameter'].sudo().set_param('rest_context', {'endpoint_id' : rest_current_endpoint_id, 'current_field' : self.id})
        if not self.env['ir.config_parameter'].sudo().get_param(f'rest_{rest_current_endpoint_id}_relationship'):
            self.env['ir.config_parameter'].sudo().set_param(f'rest_{rest_current_endpoint_id}_relationship', {})
        return {'type': 'ir.actions.act_window',
                'res_model' : 'ir.model.fields',
                'target' : 'current',
                'view_id' : self.env.ref('rest.children_tree').id,
                'view_mode' : 'tree',
                'context' : {'button_domain' : self.button_domain,
                             'path' : self._context.get('path') + '>' + self.relation,
                             'default_endpoint_id' : rest_current_endpoint_id
                             },
                'domain' : domain,
                }

    # Action button's method inside tree view of a wizard
    def save_fields(self, **args):

        selected_fields = self.ids

        rest_context = ast.literal_eval(self.env['ir.config_parameter'].sudo().get_param('rest_context'))
        rest_current_endpoint_id = rest_context["endpoint_id"]
        rest_current_endpoint_relationship = ast.literal_eval(self.env['ir.config_parameter'].sudo().get_param(f'rest_{rest_current_endpoint_id}_relationship'))
        rest_current_field_id = rest_context["current_field"]
        if rest_current_field_id:
            for selected_field in selected_fields:
                if selected_field in rest_current_endpoint_relationship:
                    raise ValidationError(f'Cycle detected: {selected_field}')
            rest_current_endpoint_relationship[rest_current_field_id] = selected_fields
            self.env['ir.config_parameter'].sudo().set_param(f'rest_{rest_current_endpoint_id}_relationship', rest_current_endpoint_relationship)
            # save the relationship dictionary into rest_current_endpoint record.
            self.env['rest.endpoint'].search([('id','=',rest_current_endpoint_id)]).write({'dictionary' : self.env['ir.config_parameter'].sudo().get_param(f'rest_{rest_current_endpoint_id}_relationship'
                                                             )})



