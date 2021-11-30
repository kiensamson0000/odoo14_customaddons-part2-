# -*- coding: utf-8 -*-
{
    'name': "Haravan Integration",
    'summary': """
        GET DATA use API FROM haravan.com CONNECT Odoo
    """,
    'description': """
        GET DATA use API FROM haravan.com CONNECT Odoo
    """,
    'author': "khuathuykien",
    'website': "https://magenest.com/vi/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # note any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'sale_management', 'product', 'website_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/api_haravan_cron.xml',
        'wizard/update_order_state_view.xml',
        'views/haravan_seller_view.xml',
        'views/sale_order_inherit_view.xml',
        'views/product_template_inherit_view.xml',
        'views/res_partner_inherit_view.xml',
        'views/product_product_inherit_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
