from odoo import api, fields, models


class ProjectTaskInherit(models.Model):
    _inherit = "project.task"

    testcase_task_type = fields.Selection(
        string='TestCase type',
        selection=[('manual', 'Manual'),
                   ('selenium', 'Create Selenium scripts'), ('retest_selenium', 'Retest Selenium'),
                   ('convert_webdriver', 'Convert to Webdriver'),
                   ('webdriver', 'Webdriver'), ])

    @api.model
    def timesheet_app_search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain:
            for element in domain:
                if element[0] == 'stage_type':
                    domain.remove(element)
            domain.append(['stage_type', 'in', ['todo', 'inprogress', 'qa']])
        else:
            domain = [['stage_type', 'in', ['todo', 'inprogress', 'qa']]]
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
