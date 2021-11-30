import requests
import json
from odoo import fields, models, api


class ResCompanyInherit(models.Model):
    _inherit = "res.company"
    _description = "Inherit rescompany"

    check_company_haravan = fields.Boolean()