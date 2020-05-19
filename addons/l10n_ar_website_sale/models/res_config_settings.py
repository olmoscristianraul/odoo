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

    def set_values(self):
        """ When changing setting we also update all the portal users """
        res = super().set_values()
        # TODO compare between the saved and the ir.config.parameter?
        if self.l10n_ar_show_line_subtotals_tax_selection:
            self.env['res.users'].search([])._l10n_ar_update_tax_group_portal_user()
        return res
