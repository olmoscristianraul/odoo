from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, values):
        """ If a partner in argentinian company context the afip responsibility has been change then update the groups
        of the user that let us to show or not tax_included """
        res = super().write(values)

        if self.env.company.country_id == self.env.ref('base.ar') and 'l10n_ar_afip_responsibility_type_id' in values:

            tax_included = self.env.ref('account.group_show_line_subtotals_tax_included')
            tax_excluded = self.env.ref('account.group_show_line_subtotals_tax_excluded')
            company_tax_config = self.env['ir.config_parameter'].sudo().get_param('l10n_ar_website_sale.show_line_subtotals_tax_selection')

            portal_users = self.user_ids.filtered(lambda x: x.is_ar_portal_user())
            for user in portal_users:
                if company_tax_config == 'responsibility_type':
                    final_consumer = values.get('l10n_ar_afip_responsibility_type_id') == self.env.ref('l10n_ar.res_CF').id
                    user.write({'groups_id': [(4 if final_consumer else 3, tax_included.id),
                                              (3 if final_consumer else 4, tax_excluded.id)]})
                else:
                    user.write({'groups_id': [(4 if company_tax_config == 'tax_included' else 3, tax_included.id),
                                              (4 if company_tax_config == 'tax_excluded' else 3, tax_excluded.id)]})
        return res
