from odoo import _, _lt, api, fields, models
from odoo.osv.expression import AND, TRUE_DOMAIN, normalize_domain
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


SEARCH_PANEL_ERROR_MESSAGE = _lt("Too many items to display.")

class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        field = self._fields[field_name]
        supported_types = ['many2one', 'selection']
        if field.type not in supported_types:
            types = dict(self.env["ir.model.fields"]._fields["ttype"]._description_selection(self.env))
            raise UserError(_(
                'Only types %(supported_types)s are supported for category (found type %(field_type)s)',
                supported_types=", ".join(types[t] for t in supported_types),
                field_type=types[field.type],
            ))

        model_domain = kwargs.get('search_domain', [])
        extra_domain = AND([
            kwargs.get('category_domain', []),
            kwargs.get('filter_domain', []),
        ])
        if field.type == 'selection':
            return {
                'parent_field': False,
                'values': self._search_panel_selection_range(field_name, model_domain=model_domain,
                                                             extra_domain=extra_domain, **kwargs
                                                             ),
            }
        Comodel = self.env[field.comodel_name].with_context(hierarchical_naming=False)
        field_names = ['display_name']
        hierarchize = kwargs.get('hierarchize', True)
        parent_name = False
        if hierarchize and Comodel._parent_name in Comodel._fields:
            parent_name = Comodel._parent_name
            field_names.append(parent_name)

            def get_parent_id(record):
                value = record[parent_name]
                return value and value[0]
        else:
            hierarchize = False
        comodel_domain = kwargs.get('comodel_domain', [])
        enable_counters = kwargs.get('enable_counters')
        expand = kwargs.get('expand')
        limit = kwargs.get('limit')
        if enable_counters or not expand:
            domain_image = self._search_panel_field_image(field_name,
                                                          model_domain=model_domain, extra_domain=extra_domain,
                                                          only_counters=expand,
                                                          set_limit=limit and not (
                                                                      expand or hierarchize or comodel_domain), **kwargs
                                                          )

        if not (expand or hierarchize or comodel_domain):
            values = list(domain_image.values())
            if limit and len(values) == limit:
                return {'error_msg': str(SEARCH_PANEL_ERROR_MESSAGE)}
            return {
                'parent_field': parent_name,
                'values': values,
            }

        if not expand:
            image_element_ids = list(domain_image.keys())
            if hierarchize:
                condition = [('id', 'parent_of', image_element_ids)]
            else:
                condition = [('id', 'in', image_element_ids)]
            comodel_domain = AND([comodel_domain, condition])
            try:
                comodel_records = Comodel.sudo().search_read(comodel_domain, field_names, limit=limit)
            except Exception as e:
                raise ValidationError(_("Hierarchy of employee is not properly set"))
            if hierarchize:
                ids = [rec['id'] for rec in comodel_records] if expand else image_element_ids
                comodel_records = self._search_panel_sanitized_parent_hierarchy(comodel_records, parent_name, ids)

            # if limit and len(comodel_records) == limit:
            #     return {'error_msg': str(SEARCH_PANEL_ERROR_MESSAGE)}

            field_range = {}
            for record in comodel_records:
                record_id = record['id']
                values = {
                    'id': record_id,
                    'display_name': record['display_name'],
                }
                if hierarchize:
                    values[parent_name] = get_parent_id(record)
                if enable_counters:
                    image_element = domain_image.get(record_id)
                    values['__count'] = image_element['__count'] if image_element else 0
                field_range[record_id] = values

            if hierarchize and enable_counters:
                self._search_panel_global_counters(field_range, parent_name)
            return {
                'parent_field': parent_name,
                'values': list(field_range.values()),
            }
