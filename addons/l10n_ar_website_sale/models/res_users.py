from odoo import models
from odoo.addons.base.models.res_users import name_selection_groups


class ResUsers(models.Model):

    _inherit = 'res.users'

    def _l10n_ar_is_portal_public(self):
        """ Return True of False if the user is a portal or public user and belongs to an Argentinian Company """
        self.ensure_one()
        if (self.has_group('base.group_portal') or self._is_public() and \
           self.company_ids.filtered(lambda x: x.country_id == self.env.ref('base.ar')):
            return True
        return False

    def is_user_type(self):
        internal = self.env.ref('base.group_user')
        portal = self.env.ref('base.group_portal')
        public = self.env.ref('base.group_public')
        return name_selection_groups([internal.id, portal.id, public.id])

    def write(self, values):
        res = super().write(values)
        if self.is_user_type() in values:
            self._l10n_ar_update_tax_group_portal_user()
        return res

    # TODO test
    # def create(self, values):
    #     res = super().create(values)
    #     if self.is_user_type() in values:
    #         self._l10n_ar_update_tax_group_portal_user()
    #     return res

    def _l10n_ar_update_tax_group_portal_user(self):
        # TODO we need default for non portal users
        # B2B is the default for new users (portal and internal)

        tax_included = self.env.ref('account.group_show_line_subtotals_tax_included')
        tax_excluded = self.env.ref('account.group_show_line_subtotals_tax_excluded')
        company_tax_config = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_ar_website_sale.show_line_subtotals_tax_selection') or 'responsibility_type'

        portal_and_public_users = self.filtered(lambda x: x._l10n_ar_is_portal_public())
        for user in portal_and_public_users:
            final_consumer = user.l10n_ar_afip_responsibility_type_id == self.env.ref('l10n_ar.res_CF')
            if company_tax_config == 'tax_included' or (company_tax_config == 'responsibility_type' and final_consumer):
                tax_excluded.users -= user
                tax_included.users |= user
            else:
                # company_tax_config == 'tax_excluded' or (company_tax_config == 'responsibility_type' and not final_consumer)
                tax_included.users -= user
                tax_excluded.users |= user
