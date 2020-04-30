# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.l10n_latam_website_sale.controllers.portal import L10nLatamCustomerPortal
from odoo.http import request, route

class L10nARCustomerPortal(L10nLatamCustomerPortal):

    OPTIONAL_BILLING_FIELDS = L10nLatamCustomerPortal.OPTIONAL_BILLING_FIELDS + ["l10n_ar_afip_responsibility_type_id"]

    @route()
    def account(self, redirect=None, **post):
        if post and request.httprequest.method == 'POST':
            post.update({'l10n_ar_afip_responsibility_type_id': int(post.pop('l10n_ar_afip_responsibility_type_id') or False) or False})

        response = super().account(redirect=redirect, **post)

        responsibility_types = request.env['l10n_ar.afip.responsibility.type'].sudo().search([])
        response.qcontext.update({'responsibility_types': responsibility_types})
        return response
