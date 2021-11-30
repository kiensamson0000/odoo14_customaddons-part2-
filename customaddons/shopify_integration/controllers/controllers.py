# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import UserError, ValidationError

import shopify
import binascii
import os
import werkzeug
from werkzeug.utils import redirect
from werkzeug.http import dump_cookie
import random
import string
from urllib.request import urlopen
import base64
from datetime import *


class ShopifyApp(http.Controller):
    @http.route('/shopify/auth/<string:name>', auth='public', website=False)
    def shopify_auth(self, name=None, **kw):
        exiting_app = http.request.env['s.app'].sudo().search([('s_app_name', '=', name)])
        if 'shop' in kw:
            shop_url = kw['shop']
            print(kw)
            shopify.Session.setup(api_key=exiting_app.s_api_key, secret=exiting_app.s_secret_key)
            base_url = "https://odoo.website"
            session = shopify.Session(shop_url, exiting_app.s_api_version, kw)
            scope = ['read_orders', 'write_orders', 'read_products', 'write_products', 'read_customers', 'write_script_tags', 'read_script_tags']
            redirect_uri = base_url + "/shopify/finalize/" + name
            permission_url = session.create_permission_url(scope, redirect_uri)
            print(permission_url)
        return werkzeug.utils.redirect(permission_url)

    @http.route('/shopify/finalize/<string:name>', auth='public', website=True)
    def shopify_finalize(self, name=None, **kw):
        exiting_app = http.request.env['s.app'].sudo().search([('s_app_name', '=', name)])
        if 'shop' in kw:
            shop_url = kw['shop']
            shopify.Session.setup(
                api_key=exiting_app.s_api_key,
                secret=exiting_app.s_secret_key)
            session = shopify.Session(shop_url, exiting_app.s_api_version)
            access_token = session.request_token(kw)
            #
            session = shopify.Session(shop_url, exiting_app.s_api_version, access_token)
            shopify.ShopifyResource.activate_session(session)
            #
            shop_current = shopify.Shop.current()

            # todo: create s_shop
            search_shop = request.env['s.shop'].sudo().search([('shop_base_url', '=', shop_current.domain)])
            password = random.randint(1000000000, 9999999999)
            print(password)
            shop_infor = {
                'shop_base_url': shop_current.domain,
                'shop_owner': shop_current.shop_owner,
                'shop_currency': shop_current.currency,
                'shop_password': password,
                'shop_app_ids': [(4, exiting_app.id)]
            }
            if search_shop:
                search_shop.sudo().write(shop_infor)
            else:
                request.env['s.shop'].sudo().create(shop_infor)

            # todo: create s_sp_app
            search_s_sp_app = request.env['s.sp.app'].sudo().search([('web_user', '=', shop_current.domain)])
            s_sp_app_infor = {
                'sp_app': request.env['s.app'].sudo().search([('s_api_key', '=', exiting_app.s_api_key)]).id,
                'sp_shop': request.env['s.shop'].sudo().search([('shop_base_url', '=', shop_current.domain)]).id,
                'token_shop_app': access_token,
                'web_user': shop_current.domain,
            }
            if search_s_sp_app:
                search_s_sp_app.sudo().write(s_sp_app_infor)
            else:
                request.env['s.sp.app'].sudo().create(s_sp_app_infor)

            # todo: create SHOP in 'res.partner'
            existed_res_partner = request.env['res.partner'].sudo().search([('email', '=', shop_current.customer_email)])
            partner_vals = {
                'company_type': 'company',
                'name': shop_current.name,
                'street': shop_current.address1,
                'street2': shop_current.address2,
                'city': shop_current.city,
                'zip': shop_current.zip,
                'email': shop_current.customer_email,
                'website': shop_current.domain,
                'shop_id': request.env['s.shop'].sudo().search([("shop_base_url", "=", shop_current.domain)]).id,
            }
            if not existed_res_partner:
                request.env['res.partner'].sudo().create(partner_vals)
            else:
                existed_res_partner.sudo().write(partner_vals)

            # Active Shop Currency in module core
            active_currency = request.env['res.currency'].sudo().search([("name", "=", shop_current.currency), ('active', '=', False)])
            if active_currency:
               active_currency.active = True

            # todo: create USER in 'res.partner'
            existed_user = request.env['res.users'].sudo().search([('login', '=', shop_current.domain)])
            user_vals = {
                'login': shop_current.domain,
                'password': password,
                'active': 'true',
                'partner_id': request.env['res.partner'].sudo().search([('email', '=', shop_current.customer_email)]).id
            }
            if not existed_user:
                request.env['res.users'].sudo().create(user_vals)
            else:
                existed_user.sudo().write(user_vals)

        # todo: create customer in 'res.partner'
        website = 'https://' + shop_current.domain
        customer_current = shopify.Customer.search()
        customer_list = request.env['res.partner'].sudo().search([])
        customer_id_list = []
        for customer in customer_list:
            customer_id_list.append(customer.customer_id)
        for customer in customer_current:
            if customer.id.__str__() not in customer_id_list:
                customer_name = customer.first_name + '' + customer.last_name
                cus_vals = {
                    'customer_id': customer.id,
                    'company_type': 'person',
                    'name': customer_name,
                    'parent_id': request.env['res.partner'].sudo().search([("website", "=", website)]).id,
                    'phone': customer.phone,
                    'email': customer.email,
                    'shop_id': request.env['s.shop'].sudo().search([("shop_base_url", "=", shop_current.domain)]).id
                }
                request.env['res.partner'].create(cus_vals)

        # todo: create product in 'product.template'
        product_current = shopify.Product.find()
        for product in product_current:
            product_vals = {
                'shopify_product_id': product.id,
                'name': product.title,
                'lst_price': product.variants[0].price,
                'variant_id': product.variants[0].id,
                'image_1920': base64.b64encode(urlopen(product.images[0].src).read()),
                'shop_id': request.env['s.shop'].sudo().search([("shop_base_url", "=", shop_current.domain)]).id
            }
            existed_product = request.env["product.template"].sudo().search([('shopify_product_id', '=', product.id)],
                                                                  limit=1)
            if not existed_product:
                request.env['product.template'].sudo().create(product_vals)
            else:
                existed_product.write(product_vals)
        #
        # todo: create order in 'sale.order'
        list_order = shopify.Order.find()
        if list_order:
            try:
                for order in list_order:
                    search_customer = request.env['res.partner'].sudo().search([('name', '=', order.shipping_address.name), ('phone','=', order.shipping_address.phone)])
                    create_time_order = (order.created_at.split('+')[0])
                    time_order = create_time_order.replace('T', ' ')
                    partner_ref = request.env['res.partner'].sudo().search([('name', '=', order.shipping_address.name), ('phone', '=', order.shipping_address.phone)], limit=1)
                    transaction_id = shopify.Transaction.find(order_id=order.id)
                    order_vals = {
                        'shopify_order_id': order.id,
                        'name': order.id,
                        'shopify_payment_method': order.gateway,
                        'shopify_currency': order.currency,
                        'shopify_transactions_id': str(transaction_id[0].id) if 'id' in transaction_id[
                            0].attributes else None,
                        'shopify_location_id': str(order.location_id) if order.location_id else str(
                            order.fulfillments[0].location_id),
                        'state': 'draft',
                        'date_order': datetime.strptime(time_order, '%Y-%m-%d %H:%M:%S'),
                        'partner_id': partner_ref.id if 'customer' not in order.attributes else request.env[
                            'res.partner'].sudo().search([('customer_id', '=', order.customer.id)]).id
                    }
                    existed_orders = request.env['sale.order'].sudo().search([('shopify_order_id', '=', order.id)], limit=1)
                    if not existed_orders:
                        new_record = request.env['sale.order'].sudo().create(order_vals)
                        # Add product to Order
                        if new_record:
                            if "line_items" in order.attributes:
                                product_list = order.line_items
                                list_order_product = []
                                for order_product in product_list:
                                    # check product taxable
                                    if order_product.taxable:
                                        tax_list = []
                                        for product_tax in order_product.tax_lines:
                                            if 'rate' in product_tax.attributes:
                                                search_tax = request.env['account.tax'].sudo().search(
                                                    [('amount', '=', float(product_tax.rate * 100)),
                                                     ('amount_type', '=', 'percent'), ('type_tax_use', '=', 'sale')],
                                                    limit=1)
                                                if search_tax:
                                                    tax_list.append(search_tax.id)
                                                else:
                                                    request.env['account_tax'].create({
                                                        'amount': float(product_tax.rate * 100),
                                                        'amount_type': 'percent',
                                                        'type_tax_use': 'sale',
                                                        'name': 'Tax ' + str(product_tax.rate * 100) + ' %',
                                                        'active': True
                                                    })
                                                    search_tax_1 = request.env['account.tax'].sudo().search(
                                                        [('amount', '=', float(product_tax.rate * 100)),
                                                         ('amount_type', '=', 'percent'),
                                                         ('type_tax_use', '=', 'sale')],
                                                        limit=1)
                                                    tax_list.append(search_tax_1.id)
                                        existed_products = request.env['product.template'].sudo().search([('shopify_product_id', '=', order_product.variant_id)], limit=1)
                                        if existed_products:
                                            list_order_product.append({
                                                'shopify_line_id': order_product.id,
                                                'product_id': existed_products.product_variant_id.id,
                                                'product_uom_qty': order_product.quantity,
                                                'price_unit': order_product.price,
                                                'tax_id': tax_list
                                            })
                                            if list_order_product:
                                                new_record.order_line = [(0, 0, e) for e in list_order_product]
                                    else:
                                        existed_products = request.env['product.template'].sudo().search(
                                            [('shopify_product_id', '=', order_product.variant_id)], limit=1)
                                        if existed_products:
                                            list_order_product.append({
                                                'shopify_line_id': order_product.id,
                                                'product_id': existed_products.product_variant_id.id,
                                                'product_uom_qty': order_product.quantity,
                                                'price_unit': order_product.price
                                            })
                                            if list_order_product:
                                                new_record.order_line = [(0, 0, e) for e in list_order_product]
                    else:
                        existed_orders.sudo().write(order_vals)
            except Exception as e:
                raise ValidationError(str(e))
        # password_login = request.env['s.shop'].search([('shop_base_url', '=', shop_current.domain)])

        # todo: insert script theme
        script_src = "https://odoo.website/shopify_integration/static/src/js/shop_script.js"
        existedScriptTags = shopify.ScriptTag.find(src=script_src)
        if not existedScriptTags:
            shopify.ScriptTag.create({
                "event": "onload",
                "src": script_src
            })
        ####
        curent_user = request.env['s.shop'].sudo().search([('shop_base_url', '=', shop_current.domain)])
        db = http.request.env.cr.dbname
        request.env.cr.commit()
        request.session.authenticate(db, curent_user.shop_base_url, curent_user.shop_currency)
        redirect_link = 'https://odoo.website/web#cids=1&home='
        return werkzeug.utils.redirect(redirect_link)

    @http.route('/shopify_data/fetch_product/<string:product_id>/<string:vendor>/<string:shop>', auth='public',
                type='json', cors='*', csrf=False)
    def odoo_fetch_product(self, product_id, vendor, shop, **kw):
        shopify_product = request.env['product.template'].sudo().search([('shopify_product_id', '=', product_id)])
        shop_id = request.env['s.shop'].sudo().search([('shop_base_url', '=', shop)])
        discount_product = request.env['s.discount.program'].sudo().search([('shop_id', '=', shop_id.id)])
        discount_pro = 0
        for discount in discount_product.product_ids:
            if discount.product_id.id == shopify_product.id:
                discount_pro = discount.discount_amount
                break
        return {
            'product_info': shopify_product,
            'product_name': shopify_product.name,
            'product_price': shopify_product.lst_price,
            'product_variant': shopify_product.variant_id,
            'discount': discount_pro,
            'shop': shop,
        }

    @http.route('/shopify_data/fetch_variant/<string:variant_id>/<string:shop>', auth='public',
                type='json', cors='*', csrf=False)
    def odoo_fetch_variant(self, variant_id, shop, *kwargs):
        variant = variant_id.split(',')
        pro_list = []
        pro_list_name = []
        for var in variant[:-1]:
            sp_product = request.env['product.template'].sudo().search([('variant_id', '=', var)])
            pro_list.append(sp_product.id)
            pro_list_name.append(sp_product.name)

        shop_id = request.env['s.shop'].sudo().search([('shop_base_url', '=', shop)])
        discount_product = request.env['s.discount.program'].sudo().search([('shop_id', '=', shop_id.id)])
        discount = 0

        dict_discount_product = {}
        discount_product_list = []
        for discount_pro in discount_product:
            discount_name = discount_pro.name
            discount_product_list.append(discount_pro.name)
            dict_discount_product[discount_name] = {}
            for pro in discount_pro.product_ids:
                if pro.product_id.id in pro_list:
                    dict_discount_product[discount_name][pro.name] = pro.discount_amount

        dict_discount = {}
        for pro in pro_list_name:
            price_list = []
            for dis in discount_product_list:
                price_list.append(dict_discount_product[dis][pro])
            price_max = max(price_list)
            for dis in discount_product_list:
                if (price_max > 0) & (dict_discount_product[dis][pro] == price_max):
                    dict_discount[pro] = {'Discount Name': dis, 'Discount Amount': price_max}
                    discount += price_max
                    break
        return {
            'discount': dict_discount,
            'total': discount
        }
