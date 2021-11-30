from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class MagenestGitCommit(models.Model):
    _name = 'magenest.employee.commit'

    hashCode = fields.Char(string='HashCode')

    employeeEmail = fields.Char(string="Email")

    title = fields.Char(string="Title")

    committedDate = fields.Date(string="Committed date")

    taskCode = fields.Char(string="Task Code")

    user_id = fields.Many2one('res.users', string='Employee')

    task_id = fields.Many2one('project.task', string='Task')

