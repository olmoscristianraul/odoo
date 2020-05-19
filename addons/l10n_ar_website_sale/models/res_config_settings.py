# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    l10n_ar_show_line_subtotals_tax_selection = fields.Selection([
        ('responsibility_type', 'Regarding Responsibility Type'),
        ('tax_excluded', 'Tax-Excluded'),
        ('tax_included', 'Tax-Included')], string="Line Subtotals Tax Display",
        required=True, default='responsibility_type',
        config_parameter='l10n_ar_website_sale.show_line_subtotals_tax_selection')

    def write(self, vals):
        """ When changing setting we also update all the portal users """
        res = super().write(vals)
        ar_tax_selection = vals.get('l10n_ar_show_line_subtotals_tax_selection')
        company = self.env.company_id
        if ar_tax_selection and company.country_id == self.env.ref('base.ar'):
            users = self.env['res.users'].search([]).filtered(lambda x: x.is_ar_portal_user())
            print('---- users %s' % users.mapped('name'))
            if users:
                if ar_tax_selection == 'tax_excluded':
                    self.group_show_line_subtotals_tax_included = False
                    self.group_show_line_subtotals_tax_excluded = True
                elif ar_tax_selection == 'tax_included':
                    self.group_show_line_subtotals_tax_included = True
                    self.group_show_line_subtotals_tax_excluded = False
                elif ar_tax_selection == 'responsibility_type':
                    for user in users:
                        final_consumer = user.l10n_ar_afip_responsibility_type_id == self.env.ref('l10n_ar.res_CF')
                        self.group_show_line_subtotals_tax_included = True if final_consumer else False
                        self.group_show_line_subtotals_tax_excluded = False if final_consumer else True
        return res
