# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SApp(models.Model):
    _name = 's.app'
    _description = 's_app'
    _rec_name = 'app_name'

    api_key = fields.Char()
    secret_key = fields.Char()
    api_version = fields.Char()
    app_name = fields.Char()
