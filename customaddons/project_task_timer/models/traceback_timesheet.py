from odoo import api, fields, models


class TracebackTimeSheet(models.Model):
    _name = "traceback.timesheet"

    employee_id = fields.Many2one(string="User", comodel_name="hr.employee")
    time = fields.Datetime(string="Time")
    log = fields.Text(string="Message")
    task_id = fields.Many2one(string="Task", comodel_name="project.task")
    timesheet_id = fields.Many2one(string="Timesheet", comodel_name="account.analytic.line")
    description = fields.Char(string="Description")
    start = fields.Datetime(string="START")
    end = fields.Datetime(string="END")
    unit_amount = fields.Float(string="Unit Amount")
