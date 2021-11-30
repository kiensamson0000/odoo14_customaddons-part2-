import requests
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from urllib.request import urlopen
import base64
import re


#   Class Inherit Product Template
class ProductTemplateInheritXero(models.Model):
    _inherit = "product.template"

    xero_product_id = fields.Char(string='Xero Product ID')
    xero_product_type = fields.Char()
    check_product_xero = fields.Boolean()
    xero_user_id = fields.Integer()

    # xero_discount_id = fields.One2many('s.discount', 'product_discount_xero', string='Xero Discount')
    xero_shop_id = fields.Many2one('xero.s.shop', string='Xero Shop')


#   Class Inherit Res Partner
class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    xero_customer_id = fields.Char(string='Customer ID')
    xero_shop_id = fields.Many2one('xero.s.shop', string='Shop ID')
    xero_user_id = fields.Integer()

    # xero_discount_ids = fields.Many2many('s.discount', string='Discount Customer ID')


# #       Class Inherit Sale Order
# class SaleOrderInherit(models.Model):
#     _inherit = "sale.order"
#     _description = "Sync Order Xero"
#
#     xero_order_id = fields.Char()
#     xero_payment_method = fields.Char(string='Gateway')
#     xero_transactions_id = fields.Char()
#     xero_location_id = fields.Char()
#     xero_currency = fields.Char()
#     xero_user_id = fields.Integer()
#
#     shopify_sale_order_id = fields.Many2one('account.move')
#
#     # Inherit Auto Fill Information From Sale Order To Invoices and Credit Notes
#     @api.model
#     def _create_invoices(self, grouped=False, final=False):
#         res = super(SaleOrderInherit, self)._create_invoices(grouped, final)
#         if self.shopify_transactions_id and self.shopify_location_id and self.shopify_order_id:
#             if self.invoice_ids:
#                 for invoice_refund in self.invoice_ids:
#                     invoice_refund.shopify_order = self.shopify_order_id
#                     invoice_refund.shopify_transactions = self.shopify_transactions_id
#                     invoice_refund.shopify_location = self.shopify_location_id
#         return res
#
#
# #       Class Inherit Sale Order Line
# class SaleOrderLineInherit(models.Model):
#     _inherit = "sale.order.line"
#     _description = "Sync Order Xero"
#
#     xero_line_id = fields.Char()
