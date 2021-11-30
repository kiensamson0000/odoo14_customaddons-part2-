from odoo import fields, models


class MagenestProject(models.Model):
    _inherit = 'project.project'
    code = fields.Char(string='Project Code')
    sequenceId = fields.Integer('Sequence Number')
    # run_completed_process = fields.Boolean(string="Run completed cron job yet",default=False)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', "A code can only be assigned to one product !"),
    ]

    # @api.multi
    # def write(self, vals):
    #     project = super(MagenestProject, self).write(vals)
    #
    #     for proj in self:
    #         if not  proj.run_completed_process:
    #             for task in proj.task_ids:
    #                 stageModel = task.stage_id
    #                 # project_task_type = self.env['project.task.type'].browse(stageId)
    #                 stage_name = stageModel.name;
    #
    #                 stage_id = stage_name.lower()
    #
    #                 if stage_id == 'done':
    #                     task.completed = '1'
    #                 if stage_id == 'todo' or stage_id == 'to do' or stage_id == 'to_do' or stage_id == 'in_progress' or stage_id == 'in progress' or stage_id == 'inprogress' or stage_id == 'backlog' or stage_id == 'back log' or stage_id == 'back_log':
    #                     task.completed = '0'
    #
    #             #end of for
    #             proj.run_completed_process = True
    #             self.env.cr.commit()
    #     return project
