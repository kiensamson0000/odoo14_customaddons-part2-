# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request


class EmployeeLocation(models.Model):
    _inherit = 'hr.employee'
    employee_location = fields.Many2one(comodel_name='company.location', strings='Location')


class EmployeeBaseLocation(models.Model):
    _inherit = 'hr.employee.public'
    employee_location = fields.Many2one(comodel_name='company.location', strings='Location')

class EmployeeForceUpdateLocation(models.TransientModel):
    _name = 'employee.change.location'

    def _default_events(self):
        if self._context.get('active_ids'):
            return self.env['hr.employee'].browse(self._context.get('active_ids'))

    employee_no = fields.Many2many('hr.employee', string="Employee", required=True,
                                   default=_default_events)

    location_change = fields.Many2one('company.location')

    def add_location(self):
        for rec in self.employee_no:
            request.env['hr.employee'].browse(rec.id).write({
                'employee_location': self.location_change.id,
            })
        return {'type': 'ir.actions.act_window_close'}
