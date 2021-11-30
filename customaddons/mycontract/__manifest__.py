# -*- coding: utf-8 -*-
{
    'name': "mycontract",

    'summary': """
        testcase + task code
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "My Magenest",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/templates.xml',
        'views/task_view.xml',
        'views/project_view.xml',
        # 'views/testcase_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
