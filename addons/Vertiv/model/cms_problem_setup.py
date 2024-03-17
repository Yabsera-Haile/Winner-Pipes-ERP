from odoo import fields, models, api
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)
class CmsProblemSetup(models.Model):
    _name = 'cms.problem.setup'
    _description = 'CMS Problem Setup'
    _rec_name = 'problem_type'

    sr_type = fields.Char('Sr Type')
    problem_type = fields.Char('Problem Type')
    resolution_type = fields.Char('Resolution Type')
    active = fields.Boolean('Is Active ?',default=True)


    def name_get(self):
        res = []
        for rec in self:
            ctx = self._context
            _logger.info("Contex %s",ctx)
            if ctx.get('problem_type_name', False):
                res.append((rec.id, str(rec.problem_type)))
            if ctx.get('resolution_type_name', False):
                res.append((rec.id, str(rec.resolution_type)))
        _logger.info("Res on name get %s",res)
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        ctx = self._context
        _logger.info("Contex %s", ctx)
        if ctx.get('call_type', False):
            cms_info_model_id = self.env['cms.info.model'].sudo().browse(ctx.get('call_type', False))
            args = args or []
            domain = []
            if cms_info_model_id and ctx.get('problem_type_name', False):
                domain += [('sr_type', '=', cms_info_model_id.call_type), ('problem_type', '!=', '')]
            if cms_info_model_id and ctx.get('resolution_type_name', False):
                domain += [('sr_type', '=', cms_info_model_id.call_type), ('resolution_type', '!=', '')]
            _logger.info("\nSearc & Model id %s ",
                         self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid))

            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        _logger.info("\nSearc on not if %s ",
                     super(CmsProblemSetup, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                             name_get_uid=name_get_uid))

        return super(CmsProblemSetup, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                       name_get_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        ctx = self._context
        _logger.info("Contex %s", ctx)
        _logger.info("Contex call type %s", ctx.get('call_type', False))
        _logger.info("Contex problem type%s", ctx.get('problem_type_name', False))
        _logger.info("Contex resolution type%s", ctx.get('resolution_type_name', False))
        if ctx.get('call_type', False):
            cms_info_model_id = self.env['cms.info.model'].sudo().browse(ctx.get('call_type', False))
            domain = []
            if cms_info_model_id and ctx.get('problem_type_name', False):
                domain += [('sr_type', '=', cms_info_model_id.call_type),('problem_type','!=','')]
            if cms_info_model_id and ctx.get('resolution_type_name', False):
                domain += [('sr_type', '=', cms_info_model_id.call_type),('resolution_type','!=','')]
        _logger.info("\nSearc on not if %s ",
                     super(CmsProblemSetup, self).search_read(domain, fields, offset, limit, order))

        return super(CmsProblemSetup, self).search_read(domain, fields, offset, limit, order)
