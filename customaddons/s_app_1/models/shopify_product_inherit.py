from odoo import api, fields, models, _, tools


class ShopifyProductInherit(models.Model):
    _inherit = 'product.product'

    pro_id = fields.Char(string='Product ID')
    shop_id = fields.Many2one('res.partner', string='Shop ID')
    variant_id = fields.Char(string='Variant ID')
    # discount_amount = fields.Monetary(string='Discount Amount')

    discount_id = fields.One2many('shopify.discount.program.product', 'product_id', string='Discount Program',  ondelete='cascade')