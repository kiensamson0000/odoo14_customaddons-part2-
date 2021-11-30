# -*- coding: utf-8 -*-

from odoo import models, fields


class CompanyLocation(models.Model):
    _name = 'company.location'
    name = fields.Char(string='Location', require=True)
