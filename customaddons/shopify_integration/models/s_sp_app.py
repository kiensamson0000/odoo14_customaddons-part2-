# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SSpApp(models.Model):
    _name = 's.sp.app'
    _description = 'save shop that have installed the app'

    sp_app = fields.Many2one('s.app', string='App ID')
    sp_shop = fields.Many2one('s.shop', string='Shop ID')
    token_shop_app = fields.Char('Token Shop')
    web_user = fields.Char('Web User')

