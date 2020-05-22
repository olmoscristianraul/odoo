from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, values):
        """ If the afip responsibility of a partner has been change (In argentinian company context) then update the
        tax group of the user will be updated """
        res = super().write(values)
        if self.env.company.country_id == self.env.ref('base.ar') and values.get('l10n_ar_afip_responsibility_type_id'):
            self.user_ids._l10n_ar_update_user_tax_group()
        return res

    # TODO defined in base_vat, leave it here or move it to l10n_ar? review if needed after the last changes
    # def _split_vat(self, vat):
    #     import pdb; pdb.set_trace()
    #     country = self.country_id or self.env.company.country_id
    #     if country != self.env.ref('base.ar'):
    #         return super()._split_vat(vat)
    #     return country.code.lower(), vat

    def _fix_vat_number(self, vat, country_id):
        """ This method add as prefix the country code to the vat name, we do not want this for Argentinan Companies """
        if self.env.company.country_id == self.env.ref('base.ar'):
            return vat
        return super()._fix_vat_number(vat, country_id)
