# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    l10n_ar_show_line_subtotals_tax_selection = fields.Selection([
        ('responsibility_type', 'Regarding Responsibility Type'),
        ('tax_excluded', 'Tax-Excluded'),
        ('tax_included', 'Tax-Included')], string="Line Subtotals Tax Display",
        required=True, default='tax_excluded',
        config_parameter='account.show_line_subtotals_tax_selection')

    # TODO we need to change this method to work as we need
    @api.onchange('show_line_subtotals_tax_selection')
    def _onchange_l10n_ar_sale_tax(self):
        if self.show_line_subtotals_tax_selection == "tax_excluded":
            self.update({
                'group_show_line_subtotals_tax_included': False,
                'group_show_line_subtotals_tax_excluded': True,
            })
        else:
            self.update({
                'group_show_line_subtotals_tax_included': True,
                'group_show_line_subtotals_tax_excluded': False,
            })
