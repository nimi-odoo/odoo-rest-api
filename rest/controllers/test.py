from odoo import http
from odoo.http import request

class RestController(http.Controller):
    @http.route('/api/<string:str>', auth="publgiric")
    def index(self, **kw):
        model_name = kw['str']
        model_id = request.env['ir.model'].search([('model','=',model_name)])
        res = ""
        for field in model_id.field_id:
            res += (field.name + "\n")

        return res
        # search model name from ir.model'
        # print it on page.


