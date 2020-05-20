from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, values):
        """ If a partner in argentinian company context the afip responsibility has been change then update the groups
        of the user that let us to show or not taxes included/excluded """
        res = super().write(values)
        if self.env.company.country_id == self.env.ref('base.ar') and values.get('l10n_ar_afip_responsibility_type_id'):
            self.user_ids._l10n_ar_update_user_tax_group()
        return res
