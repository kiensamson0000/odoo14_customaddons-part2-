# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools

class ShopifyContactInherit(models.Model):
    _inherit = 'res.partner'
    _rec_name = 'shop_id'

    customer_id = fields.Char(string='Customer ID')
    shop_id = fields.Many2one('s.shop', string='Shop ID')

    discount_id = fields.One2many('s.discount.program.customer', 'customer_id', string='Discount Customer ID')
