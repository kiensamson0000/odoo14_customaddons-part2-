from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class MagenestTask(models.Model):
    _inherit = 'project.task'
    _order = "write_date desc,priority asc," \
             " sequence, id desc"
    STATE_COLOR_SELECTION = [
        ('0', 'Blocker'),
        ('1', 'Critical'),
        ('2', 'Important'),
        ('3', 'Normal'),
        ('4', 'Trivial'),

    ]

    priority = fields.Selection(STATE_COLOR_SELECTION, 'Priority', default='3', track_visibility='onchange')
    code = fields.Char(string='Task Code', copy=False, default=None)
    # _sql_constraints = [
    #     ('code_uniq', 'unique(code)', "A code can only be assigned to one task !"),
    # ]

    # Field to mark a task as done
    # COMPLETED_SELECTION = [
    #     ('0', 'Uncompleted'),
    #     ('1', 'Completed')
    # ]

    # completed = fields.Selection(COMPLETED_SELECTION, 'Completed' , default='0',track_visibility='onchange')

    # def _check_missed_deadline(self):
    #     should_process_completed_field = False
    #     for task in self:
    #         today = fields.Date.from_string(fields.Date.context_today(self))
    #
    #         if task.completed == '0':
    #             if task.date_deadline:
    #                 the_date_deadline = fields.Date.from_string(task.date_deadline)
    #                 if the_date_deadline < today:
    #                     task.missed_deadline_search = True
    #                 else:
    #                     task.missed_deadline_search = False
    #
    #         else:
    #             task.missed_deadline_search = False
    #     #set the field for project

    # missed_deadlines = self.env['project.task'].search([("completed", '=', '0'),
    #
    #                                                     ('date_deadline', '>', today)])
    #
    # for overdue in missed_deadlines:
    #     overdue.missed_deadline_search = True

    # end of compute function
    # missed_deadline_search = fields.Boolean(string="Missed Deadline", compute='_check_missed_deadline')

    @api.model
    def create(self, values):
        task = super(MagenestTask, self).create(values)
        sequenModel = self.env['ir.sequence'].sudo()
        # Before write logic

        project_model = task.sudo().project_id
        if project_model:
            project_name = project_model.name
            if not project_model.code:
                project_model.code = str(int(datetime.now().timestamp()))
                # raise ValidationError(_("Project must have a code. Contact with the project manager to set it up"))

            code = ''.join([project_model.code, '-'])
            sequenceCode = ''.join(['project_', 'code_', str(project_model.id)])
            projectSequenceId = project_model.sequenceId

            if not projectSequenceId:

                # sequenModel = self.env['ir.sequence'].search([('code','=',sequenceCode)]);

                sObject = sequenModel.create({'name': project_name,
                                              'code': sequenceCode,
                                              'prefix': code,
                                              'padding': 3
                                              })

                # project_model.update({'sequenceId',sequenModel.id});
                for si in sObject:
                    theId = si.id
                    project_model.sudo().sequenceId = si.id

            sequenModel = self.env['ir.sequence'].sudo().browse(project_model.sequenceId)
            # sequenModel = self.env['ir.sequence'].browse(64)

            for sequenceObj in sequenModel:
                sc = sequenceObj.code

                # update order no
                # testcase.update({orderno:orderno})
                task.sudo().code = str(self.env['ir.sequence'].next_by_code(sc))
        return task

    # @api.multi
    # def write(self, values):
    #     tasks = super(MagenestTask, self).write(values)
    #     sequenModel = self.env['ir.sequence'].sudo();
    #
    #     for task in self:
    #         if not task.code:
    #             project_model = task.project_id
    #             if project_model:
    #                 project_name = project_model.name
    #                 if not project_model.code:
    #                     raise ValidationError(
    #                         _("Project must have a code. Contact with the project manager to set it up"))
    #
    #                 code = ''.join([project_model.code, '-'])
    #                 sequenceCode = ''.join(['project_', 'code_', str(project_model.id)])
    #                 projectSequenceId = project_model.sequenceId
    #
    #                 if not projectSequenceId:
    #
    #                     # sequenModel = self.env['ir.sequence'].search([('code','=',sequenceCode)]);
    #
    #                     sObject = sequenModel.create({'name': project_name,
    #                                                   'code': sequenceCode,
    #                                                   'prefix': code,
    #                                                   'padding': 3
    #                                                   })
    #
    #                     # project_model.update({'sequenceId',sequenModel.id});
    #                     for si in sObject:
    #                         theId = si.id;
    #                         project_model.sudo().sequenceId = si.id;
    #
    #                 sequenModel = self.env['ir.sequence'].browse(project_model.sequenceId)
    #                 # sequenModel = self.env['ir.sequence'].browse(64)
    #
    #                 for sequenceObj in sequenModel:
    #                     sc = sequenceObj.code;
    #
    #                     # update order no
    #                     # testcase.update({orderno:orderno})
    #                     task.code = str(self.env['ir.sequence'].next_by_code(sc))
    #
    #         #end of for
    #         #######################################
    #         #Hooking when the stage_id is changed
    #         if 'stage_id' in values:
    #             if values.get('stage_id'):
    #                 stageId =  values.get('stage_id')
    #                 project_task_type = self.env['project.task.type'].browse(stageId)
    #                 stage_name =  project_task_type.name;
    #
    #                 stage_id = stage_name.lower()
    #
    #                 if stage_id == 'done':
    #                     task.completed= '1'
    #                 if stage_id == 'todo' or stage_id == 'to do' or stage_id == 'to_do' or stage_id == 'in_progress' or stage_id == 'in progress' or stage_id == 'inprogress' or stage_id == 'backlog' or stage_id == 'back_log':
    #                     task.completed = '0'
    #
    #
    #
    #
    #
    #     return  tasks
