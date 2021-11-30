from odoo import api, fields, models, _, tools


class ShopifyApp(models.Model):
    _name = "shopify.shop.app"
    _description = "Shopify App"

    shop = fields.Many2one('shopify.shop', string='Shop ID')
    app = fields.Many2one('shopify.app', string='App ID')