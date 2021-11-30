from datetime import *

from odoo import models, fields, _, api


# class ResConfigSetting(models.TransientModel):
#     _inherit = "res.config.settings"
#
#     target_timesheet = fields.Float(string="Target timesheet (%)")
#
#     @api.model
#     def get_values(self):
#         res = super(ResConfigSetting, self).get_values()
#
#         res['target_timesheet'] = float(self.env['ir.config_parameter'].sudo().get_param('project_task_timer.target_timesheet', default=0))
#
#         return res
#
#     @api.model
#     def set_values(self):
#         self.env['ir.config_parameter'].sudo().set_param('project_task_timer.target_timesheet', self.target_timesheet)
#
#         super(ResConfigSetting, self).set_values()


class ProjectTaskTimeSheet(models.Model):
    _inherit = 'account.analytic.line'

    date_start = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string='End Date', readonly=1)
    timer_duration = fields.Float(invisible=1, string='Time Duration (Minutes)')
    employee_location = fields.Many2one(comodel_name='company.location', strings='Location',
                                        related='employee_id.employee_location', store=True)
    employee_category_ids = fields.Many2many(related='employee_id.category_ids', string="Employee Tags", readonly=False,
                                             related_sudo=False)
    # department leader user
    team_leader_user_id = fields.Many2one('res.users', related='employee_id.department_id.manager_id.user_id',
                                          store=True)
    task_code = fields.Char(string="Task Code", compute="compute_task_code", store=True)
    account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=False, ondelete='restrict',
                                 index=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    testcase_task_type = fields.Selection(selection=[('manual', 'Manual'),
                                                     ('selenium', 'Create Selenium scripts'),
                                                     ('retest_selenium', 'Retest Selenium'),
                                                     ('convert_webdriver', 'Convert to Webdriver'),
                                                     ('webdriver', 'Webdriver'), ], string='Task type',
                                          compute="_compute_testcase_task_type", store=True)
    #
    check_time_sheet = fields.Boolean(compute="_check_time_sheet", store=True)

    @api.depends('task_id')
    def _compute_testcase_task_type(self):
        for rec in self:
            rec.testcase_task_type = None
            if rec.task_id:
                if rec.task_id.testcase_task_type:
                    rec.testcase_task_type = rec.task_id.testcase_task_type

    @api.model
    def create(self, vals):
        res = super(ProjectTaskTimeSheet, self).create(vals)
        self.env['traceback.timesheet'].sudo().create({
            'employee_id': res.employee_id.id,
            'time': datetime.now(),
            'task_id': res.task_id.id,
            'timesheet_id': res.id,
            'log': "Create timesheet: Value" + str(vals),
            'start': res.date_start,
            'end': res.date_end,
            'description': res.name,
            'unit_amount': res.unit_amount
        })
        return res

    @api.depends('task_id')
    def compute_task_code(self):
        for rec in self:
            rec.task_code = False
            if rec.task_id:
                if rec.task_id.code:
                    rec.task_code = rec.task_id.code

    # function để chị thủy call từ app bật tắt timesheet bên ngoài vào
    def update_timesheet_from_other_app(self, description=""):
        now = datetime.now()
        for rec in self:
            # start_lunch = datetime(now.year, now.month, now.day, 4, 45, 0)
            # end_lunch = now.replace(now.year, now.month, now.day, 5, 0, 0)
            # print(start_lunch)
            # print(end_lunch)
            # if start_lunch < now < end_lunch:
            if rec.task_id:
                last_update = rec.write_date
                duration = now - last_update
                rec.sudo().write({
                    'unit_amount': rec.unit_amount + round(duration.total_seconds() / (60.0 * 60.0), 2),
                    'date_end': datetime.now(),
                    'date_start': rec.create_date,
                    'name': str(description['description']) if type(description) is dict else str(description)
                })
                self.env['traceback.timesheet'].sudo().create({
                    'employee_id': rec.employee_id.id,
                    'time': datetime.now(),
                    'task_id': rec.task_id.id,
                    'timesheet_id': rec.id,
                    'log': "Update timesheet" + str(description),
                    'start': rec.date_start,
                    'end': rec.date_end,
                    'description': rec.name,
                    'unit_amount': rec.unit_amount
                })
                # if rec.task_id:
                #     rec.task_id.write({
                #         'is_user_working': False
                #     })
        return now

    # funticon check time sheet after 17h15
    @api.depends('date_start')
    def _check_time_sheet(self):
        a = self.env.user.tz_offset
        prefix = a.split('00')[0]
        time_offset = False
        if prefix[0] == '+':
            time_offset = int(prefix.split('+')[1])
        elif prefix[0] == '-':
            time_offset = - int(prefix.split('-')[1])
        for rec in self:
            rec.check_time_sheet = False
            if rec.date_start and time_offset:
                time_date_start = rec.date_start + timedelta(hours=time_offset)
                check_time = time_date_start.replace(hour=17, minute=00, second=0)
                if time_date_start >= check_time:
                    rec.check_time_sheet = True


class ProjectTaskTimer(models.Model):
    _inherit = 'project.task'

    task_timer_string = fields.Char(compute='_compute_task_timer_string')
    is_my_task = fields.Boolean(compute='_compute_is_my_task')
    is_user_working = fields.Boolean(
        'Is Current User Working',
        help="Technical field indicating whether the current user is working. ")
    # duration = fields.Float(
    #     'Real Duration', compute='_compute_duration',
    #     store=True)
    duration = fields.Float(
        'Real Duration', store=True)

    # def _compute_is_user_working(self):
    #     for order in self:
    #         if order.timesheet_ids.filtered(lambda x: (not x.date_end) and (x.date_start)):
    #             order.is_user_working = True
    #         else:
    #             order.is_user_working = False

    def write(self, vals):
        res = super(ProjectTaskTimer, self).write(vals)
        if "is_user_working" in vals:
            if vals['is_user_working']:
                for rec in self:
                    self._cr.execute(
                        "UPDATE project_task SET is_user_working = False WHERE user_id = %s and is_user_working=True",
                        (rec.user_id.id,))
        return res

    def cron_job_stop_all_task_timer(self):
        last_working_tasks = self.env['account.analytic.line'].sudo().search(
            [('date_start', '!=', False), ('date_end', '=', False)])
        for e in last_working_tasks:
            try:
                unit_amount = 0.0
                timer_duration = 0.0
                if e.date_start:
                    diff = fields.Datetime.now() - e.date_start
                    timer_duration = round(diff.total_seconds() / 60.0, 2)
                    unit_amount = round(diff.total_seconds() / (60.0 * 60.0), 2)
                e.write({
                    'date_end': fields.Datetime.now(),
                    'unit_amount': unit_amount,
                    'timer_duration': timer_duration,
                })
                if e.task_id:
                    e.task_id.write({
                        'is_user_working': False
                    })
            except Exception as ex:
                print('error_cron_job_stop_all_task_timer')
                a = 0

    def _compute_task_timer_string(self):
        for rec in self:
            rec.task_timer_string = ''
            if not rec.is_user_working:
                rec.task_timer_string = '---> Start'
            else:
                rec.task_timer_string = 'Stop <---'

    def _compute_is_my_task(self):
        for rec in self:
            if self._uid == rec.user_id.id or self.user_has_groups('base.group_system'):
                rec.is_my_task = True
            else:
                rec.is_my_task = False

    def toggle_start(self):
        if not self.is_user_working:
            ### end last task
            last_working_tasks = self.env['account.analytic.line'].search(
                [('date_start', '!=', False), ('date_end', '=', False), ('create_uid', '=', self._uid)])
            for e in last_working_tasks:
                unit_amount = 0.0
                timer_duration = 0.0
                if e.date_start:
                    diff = fields.Datetime.now() - e.date_start
                    timer_duration = round((diff.total_seconds()) / 60.0, 2)
                    unit_amount = round((diff.total_seconds()) / (60.0 * 60.0), 2)
                e.write({
                    'date_end': fields.Datetime.now(),
                    'unit_amount': unit_amount,
                    'timer_duration': timer_duration
                })
                e.task_id.write({
                    'is_user_working': False
                })
            ### end last task
            self.write({'is_user_working': True})
            time_line = self.env['account.analytic.line']
            for time_sheet in self:
                time_line.create({
                    'name': self.env.user.name + ': ' + time_sheet.name,
                    'task_id': time_sheet.id,
                    'user_id': self.env.user.id,
                    'project_id': time_sheet.project_id.id,
                    'date_start': datetime.now(),
                })
        else:
            self.write({'is_user_working': False})
            time_line_obj = self.env['account.analytic.line']
            domain = [('task_id', 'in', self.ids), ('date_end', '=', False), ('create_uid', '=', self._uid)]
            for time_line in time_line_obj.search(domain):
                if time_line.date_start:
                    time_line.write({'date_end': fields.Datetime.now()})
                    if time_line.date_end:
                        diff = time_line.date_end - time_line.date_start
                        time_line.timer_duration = round(diff.total_seconds() / 60.0, 2)
                        time_line.unit_amount = round(diff.total_seconds() / (60.0 * 60.0), 2)
                    else:
                        time_line.unit_amount = 0.0
                        time_line.timer_duration = 0.0
        if self.is_user_working:
            message = 'Start timesheet success!!'
            view_form = self.env.ref('project_task_timer.time_sheet_notes').id

            return {
                'name': _('Message'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'notes.views',
                'views': [(view_form, 'form')],
                'view_id': view_form,
                'target': 'new',
                'context': {'default_message_task': message},
            }
        else:
            message = 'Stop timesheet success!!'
            view_form = self.env.ref('project_task_timer.time_sheet_notes').id
            return {
                'name': _('Message'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'notes.views',
                'views': [(view_form, 'form')],
                'view_id': view_form,
                'target': 'new',
                'context': {'default_message_task': message},
            }


class ProjectTaskTimerView(models.TransientModel):
    _name = 'notes.views'

    # def toggle_start(self):
    #     res = super(ProjectTaskTimerView, self)._toggle_start()
    #
    #     for rec in self:
    #         if rec.task_timer:
    #             message = 'Timesheet Success'
    #             view_form = self.env.ref('project_task_timer.time_sheet_notes').id
    #             return {
    #                 'name': _('Message'),
    #                 'type': 'ir.actions.act_window',
    #                 'view_mode': 'form',
    #                 'res_model': 'notes.views',
    #                 'views': [(view_form, 'form')],
    #                 'view_id':view_form,
    #                 'res_id':self.id,
    #                 'target': 'new',
    #                 'context': {'default_name': message},
    #             }

    message_task = fields.Char('Message')
