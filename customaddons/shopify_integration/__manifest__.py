# -*- coding: utf-8 -*-
{
    'name': "Shopify Integration",

    'summary': """
        Shopify Integration With Odoo
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/s_shop_security.xml',
        'views/s_cart_assets.xml',
        'views/s_app_view.xml',
        'views/s_shop_view.xml',
        'views/s_sp_app_view.xml',
        'views/s_discount_program_view.xml',
        'views/account_move_inherit_view.xml',
        'views/product_template_inherit_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
