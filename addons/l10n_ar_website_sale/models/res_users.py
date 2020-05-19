from odoo import api, models
from odoo.addons.base.models.res_users import name_selection_groups


class ResUsers(models.Model):

    _inherit = 'res.users'

    def is_ar_portal_user(self):
        """ Is a portal user in an argentinian company """
        self.ensure_one()
        if self.has_group('base.group_portal') and self.company_ids.filtered(lambda x: x.country_id == self.env.ref('base.ar')):
            return True
        return False

    # def write(self, values):
    #     res = super().write(values)
    #     import pdb; pdb.set_trace()

    #     internal = self.env.ref('base.group_user')
    #     portal = self.env.ref('base.group_portal')
    #     public = self.env.ref('base.group_public')
    #     user_type = name_selection_groups([internal.id, portal.id, public.id])

    #     # and values.get('user_type') == portal.id
    #     if user_type in values:
    #         self._l10n_ar_update_tax_group_portal_user()
    #     return res

    def _l10n_ar_update_tax_group_portal_user(self):
        import pdb; pdb.set_trace()

        tax_included = self.env.ref('account.group_show_line_subtotals_tax_included')
        tax_excluded = self.env.ref('account.group_show_line_subtotals_tax_excluded')
        company_tax_config = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_ar_website_sale.show_line_subtotals_tax_selection') or 'responsibility_type'

        portal_users = self.filtered(lambda x: x.is_ar_portal_user())
        for user in portal_users:
            print(' --- before %s' % user.groups_id)

            if company_tax_config == 'responsibility_type':
                final_consumer = user.l10n_ar_afip_responsibility_type_id == self.env.ref('l10n_ar.res_CF')
                new_values = [(4 if final_consumer else 3, tax_included.id),
                              (3 if final_consumer else 4, tax_excluded.id)]
            else:
                new_values = [(4 if company_tax_config == 'tax_included' else 3, tax_included.id),
                              (4 if company_tax_config == 'tax_excluded' else 3, tax_excluded.id)]

            user.write({'groups_id': [(3, tax_included.id), (3, tax_excluded.id)]})
            print(' --- after %s' % user.groups_id)
            user.write({'groups_id': sorted(new_values)})
            print(' --- last %s' % user.groups_id)
        # we need default for non portal user


class ResGroups(models.Model):

    _inherit = 'res.groups'

    def write(self, values):
        res = super().write(values)
        import pdb; pdb.set_trace()
        # sel_groups_1_8_9: 8
        # if 'groups_id' in values:
        #     self._l10n_ar_update_tax_group_portal_user()
        return res
