from odoo import fields, models, api
from odoo.exceptions import ValidationError

class IrModelFieldsInherit(models.Model):
    _inherit = "ir.model.fields"
    _description = 'Description'

    button_domain = fields.Boolean(compute = "_compute_button_domain")
    path = fields.Char(string="Path to get to current field", required=False, default = "", compute = "_compute_path", readonly=True)
    parent = fields.One2many(comodel_name="ir.model.fields", inverse_name="children", string="Parent", required=False, )
    children = fields.Many2one(comodel_name="ir.model.fields", string="Children", required=False, )

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

    @api.model
    def test(self):
        active_ids = self.env.context.get('active_ids',[])
        print("ASD")

    def children_show(self):
        model_id = self.env['ir.model'].search([('model','=',self.relation)])
        domain = [('model_id','=',model_id.id)]
        self.test()
        if self.is_visited(self.relation):
            raise ValidationError("The same model can only be added once")
        else:
            return {'type': 'ir.actions.act_window',
                    'res_model' : 'ir.model.fields',
                    'target' : 'new',
                    'view_id' : self.env.ref('rest.children_tree').id,
                    'view_mode' : 'tree',
                    'context' : {'button_domain' : self.button_domain,
                                 'path' : self._context.get('path') + '>' + self.relation
                                 },
                    'domain' : domain,
                    }
