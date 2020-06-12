# Part of Odoo. See LICENSE file for full copyright and licensing details.
from . import controllers
from . import models

from odoo import api, SUPERUSER_ID


def _set_default_tax_group_for_public_portal_users(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.users'].with_context(active_test=False).search([])._l10n_ar_update_portal_public_user_tax_group()
