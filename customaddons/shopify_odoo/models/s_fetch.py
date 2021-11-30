# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from time import *
from odoo.exceptions import UserError, ValidationError
import requests
import json
import base64
import re
from urllib.request import urlopen
from datetime import *


class SFetch(models.Model):
    _name = 's.fetch'
    _description = 's_fetch'
    _rec_name = "current_shop"

    current_shop = fields.Many2one('s.shop', string='Shop')
    valid_date_from = fields.Date(default=date.today())
    valid_date_to = fields.Date()
    shop_user_id = fields.Integer()

    order_fetch_shopify_log = fields.Many2many('order.fetch.shopify.log', string='Order')
    product_fetch_shopify_log = fields.Many2many('product.fetch.shopify.log', string='Products')

    @api.onchange('current_shop', 'shop_user_id')
    def _add_shop_user_id(self):
        # self.shop_user_id = self.env.uid
        self.shop_user_id = 8
        search_user = self.env['res.users'].search([('id', '=', self.shop_user_id)], limit=1)
        search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)])
        self.current_shop = search_shop.id

    @api.onchange('valid_date_to')
    def check_valid_date_to(self):
        for rec in self:
            if rec.valid_date_to:
                if rec.valid_date_to < rec.valid_date_from:
                    raise ValidationError('Valid Date From Must Start Earlier Valid Date To. ')

    def get_orders_shopify(self):
        try:
            # current_id = self.env.uid
            current_id = 8    #(b/c logining = account admin)
            order_quantity = 0
            search_user = self.env['res.users'].search([('id', '=', current_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)])[0]
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)])
            api_version = search_shop.shop_app_ids[0].api_version
            url = "https://" + str(search_user.login) + "/admin/api/" + str(api_version) +  "/orders.json?created_at_max=" + str(self.valid_date_to) + "&" + "created_at_min=" + str(self.valid_date_from)
            payload = {}
            headers = {
                'X-Shopify-Access-Token': search_token.token_shop_app,
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            result = response.json()
            ######

            if 'orders' in result:
                for order in result['orders']:
                    order_quantity += 1
                    # todo: Search and Link or Create Customer in Odoo
                    if 'customer' not in order:
                        if 'shipping_address' in order:
                            search_customer = self.env['res.partner'].sudo().search([('phone', '=', order['shipping_address']['phone'])])
                            if not search_customer:
                                self.env['res.partner'].create({
                                    'company_type': 'person',
                                    'name': order['shipping_address']['first_name'] + order['shipping_address']['last_name'],
                                    'phone': order['shipping_address']['phone'],
                                    'address1': order['shipping_address']['address1'],
                                    'city': order['shipping_address']['city'],
                                    'shopify_user_id': current_id,
                                    'country': self.env['res.country'].sudo().search(
                                        [('name', '=', order['shipping_address']['country'])]).id})
                    # if 'shipping_address' doesn't exist => no create order in 'sale order'
                    if 'shipping_address' in order:
                        create_time_order = (order['created_at'].split('+')[0])
                        time_order = create_time_order.replace('T', ' ')
                        link_partner = self.env['res.partner'].sudo().search([('phone', '=', order['shipping_address']['phone'])], limit=1)
                        # transaction_id = shopify.Transaction.find(order_id=order.id)
                        # check fulfillments
                        if len(order['fulfillments']) > 0:
                            shopify_location = str(order.fulfillments[0].attributes['location_id'])
                        else:
                            shopify_location = None
                        order_vals = {
                            'shopify_order_id': order['id'],
                            'name': order['id'],
                            'shopify_payment_method': order['gateway'],
                            'shopify_currency': order['currency'],
                            # 'shopify_transactions_id': str(transaction_id[0].id) if 'id' in transaction_id[
                            #     0].attributes else None,
                            'shopify_transactions_id': None,
                            'shopify_location_id': str(order['location_id']) if order['location_id'] else shopify_location,
                            'state': 'draft',
                            'shopify_user_id': current_id,
                            'date_order': datetime.strptime(time_order, '%Y-%m-%d %H:%M:%S'),
                            'partner_id': link_partner.id if 'customer' not in order else self.env[
                                'res.partner'].sudo().search([('shopify_customer_id', '=', order['customer']['id'])], limit=1).id
                        }
                        #
                        existing_orders = self.env['sale.order'].sudo().search([('shopify_order_id', '=', order['id'])], limit=1)
                        if existing_orders:
                            existing_orders.sudo().write(order_vals)
                        else:
                            new_record = self.env['sale.order'].sudo().create(order_vals)
                            #   Add Product to Order
                            if new_record:
                                if order['line_items']:
                                    vals_product = order['line_items']
                                    for order_product in vals_product:
                                        list_order_product = []
                                        #   Check And Add Product Tax
                                        if order_product['taxable']:
                                            for product_tax in order_product['tax_lines']:
                                                list_tax = []
                                                if product_tax['rate']:
                                                    search_tax = self.env['account.tax'].sudo().search(
                                                        [('amount', '=', float(product_tax['rate'] * 100)),
                                                         ('amount_type', '=', 'percent'), ('type_tax_use', '=', 'sale')],
                                                        limit=1)
                                                    if search_tax:
                                                        list_tax.append(search_tax.id)
                                                    else:
                                                        self.env['account.tax'].create({
                                                            'amount': float(product_tax['rate'] * 100),
                                                            'amount_type': 'percent',
                                                            'type_tax_use': 'sale',
                                                            'name': 'Tax ' + str(product_tax['rate'] * 100) + ' %',
                                                            'active': True
                                                        })
                                                        search_tax_1 = self.env['account.tax'].sudo().search(
                                                            [('amount', '=', float(product_tax['rate'] * 100)),
                                                             ('amount_type', '=', 'percent'), ('type_tax_use', '=', 'sale')],
                                                            limit=1)
                                                        list_tax.append(search_tax_1.id)
                                            existing_products = self.env['product.template'].sudo().search(
                                                [('shopify_product_id', '=', order_product['variant_id'])], limit=1)
                                            if existing_products:
                                                list_order_product.append({
                                                    'shopify_line_id': order_product['id'],
                                                    'product_id': existing_products['product_variant_id']['id'],
                                                    'product_uom_qty': order_product['quantity'],
                                                    'price_unit': order_product['price'],
                                                    'tax_id': list_tax
                                                })
                                                if list_order_product:
                                                    new_record.order_line = [(0, 0, e) for e in list_order_product]
                                        # No tax
                                        else:
                                            existing_products = self.env['product.template'].sudo().search(
                                                [('shopify_product_id', '=', order_product['variant_id'])], limit=1)
                                            if existing_products:
                                                list_order_product.append({
                                                    'shopify_line_id': order_product['id'],
                                                    'product_id': existing_products['product_variant_id']['id'],
                                                    'product_uom_qty': order_product['quantity'],
                                                    'price_unit': order_product['price'],
                                                })
                                                if list_order_product:
                                                    new_record.order_line = [(0, 0, e) for e in list_order_product]
                #
                self.order_fetch_shopify_log = [(0, 0, {
                    'valid_date_from': self.valid_date_from,
                    'valid_date_to': self.valid_date_to,
                    'order_log': datetime.now(),
                    'order_quantity': order_quantity,
                })]
        except Exception as e:
            raise ValidationError(str(e))

    def get_products_shopify(self):
        try:
            # current_id = self.env.uid
            # declare current_id =8 (b/c logining = account admin)
            current_id = 8
            product_quantity = 0

            search_user = self.env['res.users'].search([('id', '=', current_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)])[0]
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)])
            api_version = search_shop.shop_app_ids[0].api_version
            url = "https://" + str(search_user.login) + "/admin/api/" + str(api_version) + "/products.json?created_at_max=" + str(self.valid_date_to) + "&created_at_min=" + str(self.valid_date_from)
            payload = {}
            headers = {
                'X-Shopify-Access-Token': search_token.token_shop_app,
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            result = response.json()
            ######
            if 'products' in result:
                for product in result['products']:
                    for pro_val in product['variants']:
                        product_quantity += 1
                        product_vals = {
                            'shopify_product_id': pro_val['id'],
                            'name': str(product['title']) + " " + str(pro_val['title']) if len(product['variants']) > 1 else str(
                        product['title']),
                            'lst_price': pro_val['price'],
                            'description': re.sub(r'<.*?>', '', product['body_html']) if product['body_html'] else None,
                            'shopify_product_type': product['product_type'],
                            'default_code': pro_val['sku'] if pro_val['sku'] else None,
                            'barcode': pro_val['barcode'] if pro_val['barcode'] else None,
                            'check_product_shopify': True,
                            'sale_ok': True if product['status'] == 'active' else False,
                            'purchase_ok': False,
                            'type': 'product',
                            'taxes_id': None,
                            'is_published': True,
                            'categ_id': 1,
                            'shopify_user_id': current_id,
                            'image_1920': base64.b64encode(
                                urlopen(product['images'][0]['src']).read()) if product['images'] else None,
                            'shopify_shop_id': search_shop.id
                        }
                        existed_product = self.env["product.template"].sudo().search(
                            [('shopify_product_id', '=', pro_val['id'])], limit=1)
                        if not existed_product:
                            self.env['product.template'].sudo().create(product_vals)
                        else:
                            existed_product.sudo().write(product_vals)
                #
                self.product_fetch_shopify_log = [(0, 0, {
                    'valid_date_from': self.valid_date_from,
                    'valid_date_to': self.valid_date_to,
                    'product_log': datetime.now(),
                    'product_quantity': product_quantity,
                })]
        except Exception as e:
            raise ValidationError(str(e))


class OrderFetchShopifyLog(models.Model):
    _name = 'order.fetch.shopify.log'
    _description = "order_fetch_shopify_log"

    valid_date_from = fields.Date(default=date.today())
    valid_date_to = fields.Date()
    order_log = fields.Datetime("Log")
    order_quantity = fields.Integer("Quantity")


class ProductFetchShopifyLog(models.Model):
    _name = 'product.fetch.shopify.log'
    _description = "product_fetch_shopify_log"

    valid_date_from = fields.Date(default=date.today())
    valid_date_to = fields.Date()
    product_log = fields.Datetime("Log")
    product_quantity = fields.Integer("Quantity")


