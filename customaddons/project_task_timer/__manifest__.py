{
    'name': 'Project Task Timer',
    'version': '12.0.1.0',
    'summary': """Task Timer With Start & Stop""",
    'description': """"This module helps you to track time sheet in project automatically.""",
    'category': 'Project',
    'author': 'Magenest',
    'company': 'Magenest',
    'website': "https://store.magenest.com",
    'depends': ['base', 'project', 'hr_timesheet', 'mycontract', 'company_location'],
    'data': [
        'data/group.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/project_task_timer_view.xml',
        'views/project_timer_static.xml',
        'views/project_task_view.xml',
        # 'views/res_config_settings.xml',
        'views/report_timesheet.xml',
        'data/ir_cron.xml',
        'views/hr_employee_view.xml',
        'views/traceback_timesheet.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
