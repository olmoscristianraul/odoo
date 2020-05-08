# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Argentinian Website',
    'version': '1.0',
    'category': 'Localization',
    'sequence': 14,
    'author': 'Odoo, ADHOC SA',
    'description': """

* Be able to see Identification Type and AFIP Responsibility in both portal and shop check address.
* Show shop taxes included/excluded with a new option that depends on the partner responsibility.

""",
    'depends': [
        'website_sale',
        'l10n_ar',
    ],
    'data': [
        'views/templates.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
