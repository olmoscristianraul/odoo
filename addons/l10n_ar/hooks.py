# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.api import Environment, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def update_tax_calculation_rounding_method(cr, registry):
    _logger.info('Update _tax_calculation_rounding_method = round_globally for Argentinian companies')
    env = Environment(cr, SUPERUSER_ID, {})
    country_ar = env.ref('base.ar').id
    env['res.company'].search( [('partner_id.country_id', '=', country_ar)]).write(
        {'tax_calculation_rounding_method': 'round_globally'})


def post_init_hook(cr, registry):
    _logger.info('Post init hook initialized')
    update_tax_calculation_rounding_method(cr, registry)
