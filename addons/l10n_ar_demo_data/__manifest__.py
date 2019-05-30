{
    'name': 'Argentinian demo data',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'account_accountant',
        'l10n_ar',
        # 'l10n_ar_afipws_fe',
        # 'l10n_ar_chart',
        # 'l10n_ar_account_tax_settlement',
        # 'l10n_ar_account_withholding',
    ],
    # 'data': [
    # ],
    'data': [
        'demo/account_tax_template_demo.xml',
        'demo/res_company_demo.xml',
        'demo/product_product_demo.xml',
        'demo/partner_demo.xml',
        'demo/account_customer_invoice_demo.xml',

        # '../l10n_ar_account/demo/account_customer_invoice_demo.yml',
        # '../l10n_ar_account/demo/account_customer_expo_invoice_demo.yml',
        'demo/account_customer_invoice_validate_demo.xml',
        'demo/account_customer_refund_demo.xml',
        # '../l10n_ar_account/demo/account_supplier_invoice_demo.yml',
        # '../l10n_ar_account/demo/account_supplier_refund_demo.yml',
        # # todo ver si usamos esto o un demo con el de groups
        # # '../l10n_ar_account/demo/account_payment_demo.yml',
        # '../l10n_ar_account/demo/account_other_docs_demo.yml',
        # # we add this file only fot tests run by odoo, we could use
        # # an yml testing if config.options['test_enable'] and only load it
        # # in that case
        # '../l10n_ar_account/demo/account_journal_demo.xml',
        # # '../account/demo/account_bank_statement.yml',
        # # '../account/demo/account_invoice_demo.yml',

        # # de l10n_ar_account_withholding
        # 'demo/customer_payment_demo.xml',
        # 'demo/supplier_payment_demo.xml',

        # # de l10n_ar_afipws_fe
        # '../l10n_ar_afipws_fe/demo/account_journal_expo_demo.yml',
        # # no podemos cargar este archivo porque usa el mismo prefijo de modulo
        # # y entonces sobree escribe las facturas de arriba, habria que
        # # duplicarlo
        # # '../l10n_ar_account/demo/account_customer_expo_invoice_demo.yml',
        # '../l10n_ar_afipws_fe/demo/account_journal_demo.yml',
        # # idem para las de expo
        # # '../l10n_ar_account/demo/account_customer_invoice_demo.yml',
        # '../l10n_ar_afipws_fe/demo/account_journal_demo_without_doc.yml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
