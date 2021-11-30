from odoo import api, fields, models
from datetime import date, datetime


class ReportTimeSheet(models.Model):
    _name = "report.timesheet"
    _rec_name = "user_id"
    _order = "percent_complete asc"

    user_id = fields.Many2one(string="Employee", comodel_name="hr.employee", index=True)
    department_id = fields.Many2one(string="Department", comodel_name="hr.department")
    date = fields.Date(string="Date Report", index=True)
    timesheet_total = fields.Float(string="Timesheet total")
    time_registered = fields.Float(string="Time registered")
    percent_complete = fields.Float(string="Percent completed (%)", group_operator="avg")

    # compute_percent_complete = fields.Char(string="Percent completed", compute="_compute_percent_complete", store=True)
    #
    # @api.depends('percent_complete')
    # def _compute_percent_complete(self):
    #     for rec in self:
    #         rec.compute_percent_complete = "0 %"
    #         if rec.percent_complete:
    #             rec.compute_percent_complete = str(rec.percent_complete) + " %"

    def gen_report_timesheet(self):
        if not self.check_day_off():
            employees = self.env['hr.employee'].sudo().search([])
            for employee in employees:
                if employee.user_id:
                    if not employee.user_id.has_group('base.group_system'):
                        today = date.today()
                        self._cr.execute('SELECT SUM(unit_amount) FROM account_analytic_line WHERE employee_id = %s AND date = %s',
                                         (employee.id, today))
                        get_today_timesheets = self.env.cr.fetchall()
                        today_timesheet = 0
                        for b in get_today_timesheets:
                            if b[0]:
                                today_timesheet = b[0]
                        if employee.resource_calendar_id:
                            default_working_hour = self.get_working_hour_day(today, employee.resource_calendar_id)

                            timesheet_existed = self.env['report.timesheet'].sudo().search([('user_id', '=', employee.id), ('date', '=', date.today())], limit=1)
                            if not timesheet_existed:
                                self.env['report.timesheet'].sudo().create({
                                    'user_id': employee.id,
                                    'department_id': employee.department_id.id if employee.department_id else False,
                                    'date': date.today(),
                                    'timesheet_total': today_timesheet,
                                    'time_registered': default_working_hour,
                                    'percent_complete': round((today_timesheet / default_working_hour) * 100, 2),
                                })
                            else:
                                timesheet_existed.sudo().write({
                                    'timesheet_total': today_timesheet,
                                    'time_registered': default_working_hour,
                                    'percent_complete': round((today_timesheet / default_working_hour) * 100, 2),
                                })

    def get_working_hour_day(self, day=None, resource_calendar_id=False):
        total_time = 0
        if day and resource_calendar_id:
            week_day = day.weekday()
            for rec in resource_calendar_id.attendance_ids:
                if str(rec.dayofweek) == str(week_day):
                    total_time += rec.hour_to - rec.hour_from
        if total_time > 0:
            return total_time
        else:
            return 8

    def check_day_off(self):
        dayoff = self.env['attendance.day.off'].sudo().search([('set_day', '=', date.today())])
        if dayoff:
            return True
        elif date.today().weekday() == 6:
            return True
        else:
            return False
