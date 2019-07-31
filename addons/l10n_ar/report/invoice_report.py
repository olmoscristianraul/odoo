# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    state_id = fields.Many2one('res.country.state', 'State', readonly=True)
    _depends = {
        'account.move': ['partner_id'],
        'res.partner': ['state_id'],
    }

    def _select(self):
        return super()._select() + ", contact_partner.state_id"

    def _group_by(self):
        return super()._group_by() + ", contact_partner.state_id"

    def _from(self):
        return super()._from() + " LEFT JOIN res_partner contact_partner ON contact_partner.id = move.partner_id"
