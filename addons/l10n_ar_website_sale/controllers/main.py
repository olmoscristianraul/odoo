# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route
from odoo.exceptions import ValidationError
from odoo import _


class L10nARWebsiteSale(WebsiteSale):

    def _get_mandatory_billing_fields(self):
        """Inherit method in order to do not break Odoo tests"""
        res = super()._get_mandatory_billing_fields()
        return res + ["l10n_latam_identification_type_id", "l10n_ar_afip_responsibility_type_id", "vat"]

    @route()
    def address(self, **kw):
        response = super().address(**kw)
        identification_types = request.env['l10n_latam.identification.type'].sudo().search([])
        responsibility_types = request.env['l10n_ar.afip.responsibility.type'].sudo().search([])
        response.qcontext.update({'identification_types': identification_types,
                                  'responsibility_types': responsibility_types})
        return response

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super().checkout_form_validate(mode=mode, all_form_values=all_form_values, data=data)

        # identification type validation
        partner = request.env.user.partner_id
        if data.get("l10n_latam_identification_type_id") and data.get("vat") and partner and \
           (partner.l10n_latam_identification_type_id.id != data.get("l10n_latam_identification_type_id") or
                partner.vat != data.get("vat")):
            if partner.can_edit_vat():
                if hasattr(partner, "check_vat"):
                    partner_dummy = partner.new({
                        'l10n_latam_identification_type_id': data.get('l10n_latam_identification_type_id', False),
                        'vat': data['vat'], 'country_id': (int(data['country_id']) if data.get('country_id') else False)})
                    try:
                        partner_dummy.check_vat()
                    except ValidationError as exception:
                        error["vat"] = 'error'
                        error_message.append(exception.name)
            else:
                error_message.append(_('Changing VAT number and Identification type is not allowed once document(s) have been issued for your account. Please contact us directly for this operation.'))

        return error, error_message
