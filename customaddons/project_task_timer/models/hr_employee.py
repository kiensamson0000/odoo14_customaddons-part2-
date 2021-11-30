from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_quarter_assets = fields.Boolean(string="Is Quarter Assets", default=False)


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    is_quarter_assets = fields.Boolean(string="Is Quarter Assets", default=False)
