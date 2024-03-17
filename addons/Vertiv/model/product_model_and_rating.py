from odoo import fields, models, api
from odoo.osv import expression

class ProductModel(models.Model):
    _name = 'product.model'
    _description = 'Product Model'
    _rec_name = 'model'

    product_group = fields.Char('Product Group')
    model = fields.Char('Model')

    def name_get(self):
        res = []
        for rec in self:
            model_name = str(rec.product_group.upper() if rec.product_group else '') + '.' + str(rec.model.upper() if rec.model else '')
            res.append((rec.id, str(model_name)))
        return res

class ProductRating(models.Model):
    _name = 'product.rating'
    _description = 'Product Rating'
    _rec_name = 'rating'

    model = fields.Char('Model')
    rating = fields.Char('Rating')


    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        ctx = self._context
        args = args or []
        domain = []
        if ctx.get('product_rating',False):
            model_id = self.env['product.model'].sudo().browse(ctx.get('product_rating', False))
            if model_id:
                model_name = str(model_id.product_group.upper())+'.'+str(model_id.model.upper())
                domain += [('model', '=', model_name)]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return super(ProductRating, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        ctx = self._context
        domain = []
        if ctx.get('product_rating', False):
            model_id = self.env['product.model'].sudo().browse(ctx.get('product_rating', False))
            if model_id:
                model_name = str(model_id.product_group.upper())+'.'+str(model_id.model.upper())
                domain += [('model', '=', model_name)]
        return super(ProductRating, self).search_read(domain, fields, offset, limit, order)
