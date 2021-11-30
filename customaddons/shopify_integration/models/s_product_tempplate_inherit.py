# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ShopifyProductInherit(models.Model):
    _inherit = 'product.template'

    shopify_product_id = fields.Char(string='Product ID')
    shopify_product_type = fields.Char()
    check_product_shopify = fields.Boolean()
    shop_id = fields.Many2one('res.partner', string='Shop ID')
    variant_id = fields.Char(string='Variant ID')

    discount_id = fields.One2many('s.discount.program.product', 'product_id', string='Discount Program',  ondelete='cascade')


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    _description = "Sync Order Shopify"

    shopify_order_id = fields.Char()
    shopify_payment_method = fields.Char(string='Gateway')
    shopify_transactions_id = fields.Char()
    shopify_location_id = fields.Char()
    shopify_currency = fields.Char()

    shopify_sale_order_id = fields.Many2one('account.move')

    # Inherit Auto Fill Information From Sale Order To Invoices and Credit Notes
    @api.model
    def _create_invoices(self, grouped=False, final=False):
        res = super(SaleOrderInherit, self)._create_invoices(grouped,final)
        if res.shopify_transactions_id and self.shopify_location_id and self.shopify_order_id:
            if self.invoice_ids:
                for invoices_refund in self.invoices_ids:
                    invoices_refund.shopify_transactions_id = self.shopify_transactions_id
                    invoices_refund.shopify_location_id = self.shopify_location_id
                    invoices_refund.shopify_order_id = self.shopify_order_id
        return res


class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"
    _description = "Sync Order Shopify"

    shopify_line_id = fields.Char()



