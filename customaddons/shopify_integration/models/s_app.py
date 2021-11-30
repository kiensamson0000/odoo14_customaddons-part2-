# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SApp(models.Model):
    _name = 's.app'
    _description = 'save list apps'
    _rec_name = 's_app_name'

    s_api_key = fields.Char('API Key')
    s_secret_key = fields.Char('Secret Key')
    s_api_version = fields.Char('API Version')
    s_app_name = fields.Char('App name')
