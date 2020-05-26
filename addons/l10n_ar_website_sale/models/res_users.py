from odoo import models, api
from odoo.addons.base.models.res_users import name_selection_groups


class ResUsers(models.Model):

    _inherit = 'res.users'

    def _l10n_ar_is_portal_public(self):
        """ Return True of False if the user is a portal or public user and belongs to an Argentinian Company """
        self.ensure_one()
        if (self.has_group('base.group_portal') or self._is_public()) and \
           self.company_ids.filtered(lambda x: x.country_id == self.env.ref('base.ar')):
            return True
        return False

    def is_user_type(self):
        """ Let us know the name of the sel_groups related to the modification of the user/type
        this is: internal / portal / public """
        internal = self.env.ref('base.group_user')
        portal = self.env.ref('base.group_portal')
        public = self.env.ref('base.group_public')
        return name_selection_groups([internal.id, portal.id, public.id])

    def write(self, values):
        """ If user type has been change then update the user tax group """
        res = super().write(values)
        if self.is_user_type() in values:
            self._l10n_ar_update_user_tax_group()
        return res

    @api.model
    def create(self, values):
        """ when a user is created re compute the tax groups """
        res = super().create(values)
        res._l10n_ar_update_user_tax_group()
        return res

    def _get_company_public_user(self):
        all_public = self.with_context(active_test=False).search([]).filtered(lambda x: x._is_public())
        company_public_users = all_public.filtered(lambda x: x.company_id == self.env.company)
        return company_public_users or all_public[0]

    def _l10n_ar_update_user_tax_group(self):
        """ Will move the user to the correspond tax group depending of the configuration defined in the global settings
        NOTE: This will only applies to portal and public users """

        tax_included = self.env.ref('account.group_show_line_subtotals_tax_included')
        tax_excluded = self.env.ref('account.group_show_line_subtotals_tax_excluded')
        company_tax_config = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_ar_website_sale.l10n_ar_tax_groups') or 'responsibility_type'

        portal_and_public_users = self.filtered(lambda x: x._l10n_ar_is_portal_public())
        public_user = self._get_company_public_user()

        for user in portal_and_public_users:
            b2c = (user.l10n_ar_afip_responsibility_type_id or public_user.l10n_ar_afip_responsibility_type_id) == self.env.ref('l10n_ar.res_CF')
            if company_tax_config == 'tax_included' or (company_tax_config == 'responsibility_type' and b2c):
                tax_excluded.users -= user
                tax_included.users |= user
            else:
                # company_tax_config == 'tax_excluded' or (company_tax_config == 'responsibility_type'
                # and not b2c)
                tax_included.users -= user
                tax_excluded.users |= user
