# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'LATAM Localization Website',
    'version': '1.0',
    'category': 'Localization',
    'sequence': 14,
    'author': 'Odoo, ADHOC SA',
    'summary': 'LATAM Identification Types in Portal and website',
    'description': """
""",
    'depends': [
        'portal',
        # 'website_sale',
    ],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
