# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SSpApp(models.Model):
    _name = 's.sp.app'
    _description = 's_sp_app'
    _rec_name = 'web_user'

    shop_app_s_apps = fields.Many2one("s.app", string='App')
    shop_app_s_shops = fields.Many2one("s.shop", string='Shop')
    token_shop_app = fields.Char()
    web_user = fields.Char()
    password_user = fields.Char()
