from odoo import api, fields, models, _, tools


class ShopifyApp(models.Model):
    _name = "shopify.app"
    _description = "Shopify App"
    _rec_name = 'api_key'

    api_key = fields.Char(string='API Key')
    secret_key = fields.Char(string='Secret Key')
    api_version = fields.Char(string='API Version')
    app_name = fields.Char(string='App Name')

