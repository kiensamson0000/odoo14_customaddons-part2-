from odoo import api, fields, models, _, tools


class ShopifyContactInherit(models.Model):
    _inherit = 'res.partner'

    cus_id = fields.Char(string='Customer ID')
    shop_id = fields.Many2one('shopify.shop', string='Shop ID')
    # check_person = fields.Boolean(string='Choose Person')

    discount_id = fields.One2many('shopify.discount.program.customer', 'customer_id', string='Discount Customer ID')
