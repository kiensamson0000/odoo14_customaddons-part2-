# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Shopify App',
    'version' : '1.1',
    'summary': 'Invoices & Payments',
    'sequence': 10,
    'description': """
Manage shop for Shopify connect
   """,
    'category': 'Accounting/Accounting',
    'website': 'https://www.odoo.com/',
    'images' : [],
    'depends' : ['base', 'contacts', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/shop_security.xml',
        'views/assets.xml',
        'views/shopify_app.xml',
        'views/shopify_shop.xml',
        'views/shopify_discount_program_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
