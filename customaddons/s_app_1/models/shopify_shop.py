from odoo import api, fields, models, _, tools


class ShopifyApp(models.Model):
    _name = "shopify.shop"
    _description = "Shopify Shop"
    _rec_name = 'base_url'

    base_url = fields.Char(string='Base URL')
    shop_owner = fields.Char(string='Shop Owner')
    shop_currency = fields.Char(string='Shop Currency')
    password = fields.Char(string='Password')