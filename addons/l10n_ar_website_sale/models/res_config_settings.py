# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    l10n_ar_show_line_subtotals_tax_selection = fields.Selection([
        ('responsibility_type', 'Regarding Responsibility Type'),
        ('tax_excluded', 'Tax-Excluded (B2B)'),
        ('tax_included', 'Tax-Included (B2C)')],
        string="Line Subtotals Tax Display", default='responsibility_type',
        config_parameter='l10n_ar_website_sale.show_line_subtotals_tax_selection')

    def set_values(self):
        """ When changing setting for how to display the prices in Argentinian company we also update all the related
        portal and public users """
        res = super().set_values()
        company_tax_config = self.env['ir.config_parameter'].sudo().get_param('l10n_ar_website_sale.show_line_subtotals_tax_selection')
        if company_tax_config != self.l10n_ar_show_line_subtotals_tax_selection:
            self.env['res.users'].search([])._l10n_ar_update_user_tax_group()
        return res
