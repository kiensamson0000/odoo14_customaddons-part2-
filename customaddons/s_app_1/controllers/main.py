from werkzeug.utils import redirect

from odoo import http
import shopify
import os
import binascii
import werkzeug
from odoo.http import request

from random import randint

api_version = '2021-04'
app_name = 'Master Shop'
API_KEY = 'f322f4ab2502a9ca49dec4642d24b2b7'
API_SECRET = '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'


class MasterShopShopify(http.Controller):
    @http.route('/shopify/auth/mts', auth='public', website=False)
    def shopify_shop(self, **kwargs):
        if 'shop' in kwargs:
            # print(kwargs['shop'])
            shop_url = kwargs['shop']

            shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)

            state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
            base_url = 'https://odoo.website'
            redirect_uri = base_url + "/shopify/finalize/mts"
            #         grant_options = 'per-user'
            scopes = ['read_orders', 'write_products', 'read_customers', 'write_script_tags', 'read_script_tags']
            # 'read_products',
            newSession = shopify.Session(shop_url, api_version)
            auth_url = newSession.create_permission_url(scopes, redirect_uri)
            # print(auth_url)

            return werkzeug.utils.redirect(auth_url)

    @http.route('/shopify/finalize/mts', auth='public', website=False)
    def shopify_shop_final(self, **kwargs):
        params = request.params
        shop_url = params['shop']
        session = shopify.Session(shop_url, api_version)
        access_token = session.request_token(params)  # request_token will validate hmac and timing attacks

        session = shopify.Session(shop_url, api_version, access_token)
        shopify.ShopifyResource.activate_session(session)

        app_list = request.env['shopify.app'].search([])
        app_flag = True
        for app in app_list:
            if API_KEY == app.api_key:
                app_flag = False
                break
        if app_flag:
            app_vals = {
                'api_key': API_KEY,
                'secret_key': API_SECRET,
                'api_version': api_version,
                'app_name': app_name,
            }
            request.env['shopify.app'].create(app_vals)

        shop_list = request.env['shopify.shop'].search([])
        shop_flag = True
        mk = randint(1000000000, 9999999999)
        shop = shopify.Shop.current()
        for sh in shop_list:
            if shop.myshopify_domain == sh.base_url:
                shop_flag = False
                break
        if shop_flag:
            shop_vals = {
                'base_url': shop.domain,
                'shop_owner': shop.shop_owner,
                'shop_currency': shop.currency,
                'password': mk
            }
            request.env['shopify.shop'].create(shop_vals)

            request.env['shopify.shop.app'].create({
                'app': request.env['shopify.app'].search([("api_key", "=", API_KEY)]).id,
                'shop': request.env['shopify.shop'].search([("base_url", "=", shop.domain)]).id
            })

            partner = request.env['res.partner'].sudo().create({
                'company_type': 'company',
                'name': shop.name,
                'street': shop.address1,
                'street2': shop.address2,
                'city': shop.city,
                # shop.country_name
                'country_id': request.env['res.country'].search([('name', '=', 'Cuba')]).id,
                'zip': shop.zip,
                'email': shop.customer_email,
                'website': shop.domain,
                'shop_id': request.env['shopify.shop'].search([("base_url", "=", shop.domain)]).id
            })
            request.env['res.users'].sudo().create({
                'login': shop.domain,
                'password': mk,
                'active': 'true',
                'partner_id': partner.id,
            })

        mat_khau = request.env['shopify.shop'].search([('base_url', '=', shop.domain)])
        print(mat_khau.password)
        # db = http.request.env.cr.dbname
        # request.env.cr.commit()
        # uid = request.session.authenticate(db, shop_url, mat_khau.password)
        website = ('http://' + shop.domain) or ('https://' + shop.domain)
        customer = shopify.Customer.search()
        cus_list = request.env['res.partner'].search([])
        cus_id_list = []
        for cus in cus_list:
            cus_id_list.append(cus.cus_id)
        for cus in customer:
            if cus.id.__str__() not in cus_id_list:
                name = cus.first_name + ' ' + cus.last_name
                cus_vals = {
                    'cus_id': cus.id,
                    'company_type': 'person',
                    'name': name,
                    'parent_id': request.env['res.partner'].search([("website", "=", website)]).id,
                    'phone': cus.phone,
                    'email': cus.email,
                    'shop_id': request.env['shopify.shop'].search([("base_url", "=", shop.domain)]).id
                }
                request.env['res.partner'].create(cus_vals)

        pr = shopify.Product.find()
        pro_list = request.env['product.product'].search([])
        pro_id_list = []
        for pro in pro_list:
            pro_id_list.append(pro.pro_id)
        for pro in pr:
            if pro.id.__str__() not in pro_id_list:
                pro_vals = {
                    'pro_id': pro.id,
                    'name': pro.title,
                    'lst_price': pro.variants[0].price,
                    'variant_id': pro.variants[0].id,
                    # 'image_1920': pro.images[0].src,
                    'shop_id': request.env['shopify.shop'].search([("base_url", "=", shop.domain)]).id
                }
                request.env['product.product'].create(pro_vals)

        script_src = "https://odoo.website/shopify_app/static/src/js/mastershop321_script.js"
        existedScriptTags = shopify.ScriptTag.find(src=script_src)
        if not existedScriptTags:
            scriptTag = shopify.ScriptTag.create({
                "event": "onload",
                "src": script_src
            })
        redirect_link = 'https://odoo.website/web#id=' + mat_khau.id.__str__() + '&action=301&model=shopify.shop&view_type=form&cids=1&menu_id=213'
        return werkzeug.utils.redirect(redirect_link, 301)

    @http.route('/shopify_data/fetch_product/<string:product_id>/<string:vendor>/<string:shop>', auth='public',
                type='json', cors='*', csrf=False)
    def odoo_fetch_product(self, product_id, vendor, shop, *kwargs):
        sp_product = request.env['product.product'].sudo().search([('pro_id', '=', product_id)])

        shop_id = request.env['shopify.shop'].sudo().search([('base_url', '=', shop)])
        discount_product = request.env['shopify.discount.program'].sudo().search(
            [('shop_id', '=', shop_id.id)])

        discount = 0
        for discoun in discount_product.pro_ids:
            if discoun.product_id.id == sp_product.id:
                discount = discoun.discount_amount
                break

        return {
            'product_info': sp_product,
            'product_name': sp_product.name,
            'product_price': sp_product.lst_price,
            'product_variant': sp_product.variant_id,
            'discount': discount,
            'shop': shop,
        }

    @http.route('/shopify_data/fetch_variant/<string:variant_id>/<string:shop>', auth='public',
                type='json', cors='*', csrf=False)
    def odoo_fetch_variant(self, variant_id, shop, *kwargs):
        variant = variant_id.split(',')
        pro_list = []
        pro_list_name = []
        for var in variant[:-1]:
            sp_product = request.env['product.product'].sudo().search([('variant_id', '=', var)])
            pro_list.append(sp_product.id)
            pro_list_name.append(sp_product.name)

        shop_id = request.env['shopify.shop'].sudo().search([('base_url', '=', shop)])
        discount_product = request.env['shopify.discount.program'].sudo().search(
            [('shop_id', '=', shop_id.id)])

        discount = 0

        dict_discount_product = {}
        discount_product_list = []
        for discount_pro in discount_product:
            discount_name = discount_pro.name
            discount_product_list.append(discount_pro.name)
            dict_discount_product[discount_name] = {}
            for pro in discount_pro.pro_ids:
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

    # new_product = shopify.Product()
    # new_product.title = "Burton Custom Freestyle 151"
    # new_product.product_type = "Snowboard"
    # new_product.vendor = "Burton"
    # new_product.save()
    # shop = shopify.Shop.current
    # print(shop)

    # pr = shopify.Product.find()
    # for pro in pr:
    #     print(pro.title)

    # shop = shopify.Shop.current()
    # print(shop.id)
    # print(shop.name)
    # print(shop.email)

    # order = shopify.Order.find()
    # for ord in order:
    #     print(ord.currency)
    #     print(ord.customer.first_name)
    #     print(ord.current_subtotal_price_set.shop_money.amount)
