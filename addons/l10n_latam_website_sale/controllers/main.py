# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request, route
from odoo.exceptions import ValidationError
from odoo import _


class L10nLatamCustomerPortal(CustomerPortal):

    OPTIONAL_BILLING_FIELDS = CustomerPortal.OPTIONAL_BILLING_FIELDS + [
        "l10n_latam_identification_type_id",
    ]

    @route()
    def account(self, redirect=None, **post):
        if post and request.httprequest.method == 'POST':
            post.update({'l10n_latam_identification_type_id': int(post.pop('l10n_latam_identification_type_id') or False) or False})

        response = super().account(redirect=redirect, **post)

        identification_types = request.env['l10n_latam.identification.type'].sudo().search([])
        response.qcontext.update({'identification_types': identification_types})
        return response

    def details_form_validate(self, data):
        error, error_message = super().details_form_validate(data)

        # identification type validation
        partner = request.env.user.partner_id
        if data.get("l10n_latam_identification_type_id") and data.get("vat") and partner and \
           partner.l10n_latam_identification_type_id.id != data.get("l10n_latam_identification_type_id"):
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
                error_message.append(_('Changing VAT number is not allowed once document(s) have been issued for your account. Please contact us directly for this operation.'))

        return error, error_message

# from odoo.addons.website_sale.controllers.main import WebsiteSale
# class L10nLatamWebsiteSale(WebsiteSale):

#     def _get_mandatory_billing_fields(self):
#         """Inherit method in order to do not break Odoo tests"""
#         res = super()._get_mandatory_billing_fields()

#         # if not config['test_enable']:
#         #     res += ["zip"]

#         return res + [
#             "l10n_latam_identification_type_id",
#             # "main_id_number",
#             # "afip_responsability_type_id",
#         ]

#     @route()
#     def address(self, **kw):
#         response = super().address(**kw)
#         document_categories = request.env['l10n_latam.identification.type'].sudo().search([])
#         # afip_responsabilities = request.env['afip.responsability.type'].sudo().search([])
#         uid = request.session.uid or request.env.ref('base.public_user').id
#         Partner = request.env['res.users'].browse(uid).partner_id
#         Partner = Partner.with_context(show_address=1).sudo()
#         response.qcontext.update({
#             'document_categories': document_categories,
#             # 'afip_responsabilities': afip_responsabilities,
#             # 'partner': Partner,
#         })
#         return response

#     # def _checkout_form_save(self, mode, checkout, all_values):
#     #     if all_values.get('commercial_partner_id', False):
#     #         commercial_fields = [
#     #             'l10n_latam_identification_type_id',
#     #             # 'main_id_number',
#     #             # 'afip_responsability_type_id'
#     #             ]
#     #         for item in commercial_fields:
#     #             checkout.pop(item, False)
#     #             all_values.pop(item, False)
#     #     res = super()._checkout_form_save(
#     #         mode=mode, checkout=checkout, all_values=all_values)
#     #     return res

#     # def checkout_form_validate(self, mode, all_form_values, data):
#     #     error, error_message = super().checkout_form_validate(mode=mode, all_form_values=all_form_values, data=data)
#     #     write_error, write_message = request.env['res.partner'].sudo().try_write_commercial(all_form_values)
#     #     if write_error:
#     #         error.update(write_error)
#     #         error_message.extend(write_message)
#     #     return error, error_message

#     # NOTE this a copy of original odoo code that was added and edited here
#     # because it was not able to inherit in other way.
#     # @route()
#     # def checkout(self, **post):
#     #     super().checkout(**post)

#     #     order = request.website.sale_get_order()

#     #     redirection = self.checkout_redirection(order)
#     #     if redirection:
#     #         return redirection

#     #     if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
#     #         return request.redirect('/shop/address')

#     #     # ODOO ORIGINAL CODE
#     #     """
#     #     for f in self._get_mandatory_billing_fields():
#     #         if not order.partner_id[f]:
#     #             return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)
#     #     """
#     #     # OUR CODE START
#     #     mandatory_billing_fields = self._get_mandatory_billing_fields()
#     #     commercial_billing_fields = ["l10n_latam_identification_type_id",
#     #                                  # "main_id_number",
#     #                                  #  "afip_responsability_type_id"
#     #                                 ]
#     #     for item in commercial_billing_fields:
#     #         mandatory_billing_fields.pop(mandatory_billing_fields.index(item))

#     #     for f in mandatory_billing_fields:
#     #         if not order.partner_id[f]:
#     #             return request.redirect(
#     #                 '/shop/address?partner_id=%d' % order.partner_id.id)
#     #     for f in commercial_billing_fields:
#     #         if not order.partner_id.commercial_partner_id[f]:
#     #             return request.redirect(
#     #                 '/shop/address?partner_id=%d' % order.partner_id.id)
#     #     # OUR CODE END

#     #     values = self.checkout_values(**post)

#     #     if post.get('express'):
#     #         return request.redirect('/shop/confirm_order')

#     #     values.update({'website_sale_order': order})

#     #     # Avoid useless rendering if called in ajax
#     #     if post.get('xhr'):
#     #         return 'ok'
#     #     return request.render("website_sale.checkout", values)
