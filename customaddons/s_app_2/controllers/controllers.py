# -*- coding: utf-8 -*-
import logging

import requests
import shopify
import werkzeug
import json

from odoo import http
from .config import DefaultConfig

_logger = logging.getLogger(__name__)


class ShopifyApp(http.Controller):
    @http.route('/shopify_app/shopify_app/', auth='public')
    def index(self, **kw):
        shopify.ShopifyResource.clear_session()

        _env = http.request.env
        shop_url = kw['shop']
        current_app = DefaultConfig()
        shopify.Session.setup(
            api_key=current_app.SHOPIFY_API_KEY,
            secret=current_app.SHOPIFY_SHARED_SECRET)

        session = shopify.Session(shop_url, current_app.API_VERSION)

        scope = ["read_orders", "read_content", "write_content"]
        redirect_uri = current_app.BASE_URL + "/shopify_app/auth"
        permission_url = session.create_permission_url(scope, redirect_uri)
        return werkzeug.utils.redirect(permission_url)

    @http.route('/shopify_app/auth', auth='public')
    def finalize(self, **kw):
        shop_url = kw['shop']
        current_app = DefaultConfig()
        shopify.Session.setup(
            api_key=current_app.SHOPIFY_API_KEY,
            secret=current_app.SHOPIFY_SHARED_SECRET)
        shopify_session = shopify.Session(shop_url, current_app.API_VERSION)

        # todo : write it to another storage
        http.request.httprequest.session.shopify_obj = shopify_session
        http.request.httprequest.session.shopify_url = shop_url

        token = shopify_session.request_token(kw)

        organizationEnv = http.request.env['shopify_app.shop']

        organization = organizationEnv.sudo().search([("url", "=", shop_url)], limit=1)
        if organization:
            if organization['install_status'] == 'uninstalled':
                organization.write({'install_status': 'active'})

        http.request.httprequest.session.shopify_token = token

        shopify.ShopifyResource.activate_session(shopify_session)

        existing_weekhooks = shopify.Webhook.find()
        if organization and not existing_weekhooks:
            # need to update the token
            existingApp = http.request.env['shopify.module.name'].sudo().search(
                [('shopify_shop_id', '=', organization.id)])
            if existingApp:
                existingApp.write({'code': token})
            else:
                existingApp = http.request.env['shopify.module.name'].sudo().create({
                    'app_name': 'blog post',
                    'code': token,
                    'install_status': True,
                    'shopify_shop_id': organization.id
                })
                x = 1

        if not organization:

            vals = {
                'url': shop_url,
                'code': token
            }

            createdOrg = organization.sudo().create(vals)

            # create shopify app
            existingApp = http.request.env['shopify.module.name'].sudo().create({
                'app_name': 'blog post',
                'code': token,
                'install_status': True,
                'shopify_shop_id': createdOrg.id
            })

            # Create company
            shopUrl = shop_url
            shopUrlemail = shop_url.split('.')[0] + '@gmail.com'
            companyModel = http.request.env['res.company']

            company = companyModel.sudo().search([("name", "=", shopUrl)])
            if not company:
                # create company
                vals = {'logo': False, 'currency_id': 2, 'sequence': 10,
                        'favicon': 'AAABAAEAEBAAAAAAIAAGAgAAFgAAAIlQTkcNChoKAAAADUlIRFIAAAAQAAAAEAgGAAAAH/P/YQAAAc1JREFUeJyV0s+LzVEYBvDP+53vNUYzSZqFlbBgJUL5tWByJzaysZPJP2AhP+7SYhZXKZEtNRZKlqPUjEQTFmbhH5AosRPjTrr3zvdY3DO6ZiKe09k8z/u85+15T8i4c2xSraiRrBX24ih2YA3e4ileoJVSMjHbAAFT403tTtdgrbYbF3AcG5f1jK+YxbXFpYX5oYFhEzMNMVVvGh4c0mr/OIkb2OrveIfzA0U86i5VyojQav84gFvYnIu+4xXeoMQe7MMQtuDmUpU+R8R8iWFc7jO/x5XEdLAYRaGqqpHgNCaxKU95KaV0rsThHBi00AjxIKmcnekFNVVvLtRqa+52up0CtzGIekQcLHAE63ODl4npSjKRzTAx29DudiQe4nWmN2CsWBHam0K0UqpWR5eSIuIr5vvYbYXfV5VWO5eFtKy2++iiwIc+YmclrYsoVjWICJVqHXb20e8KzOmtDQ4F44F79eavqql6U/TOOA5l+huelYnn0dt5HSNoYjGFp/fGr3Xz+CXGsjaSGzzDXBl8wXXswii2436Ix3LiIfbhhN73ho/Zs1BCSulJRDTyC6O58Ey+K/EJFztL3bmyGBCn9l/9Y/L/gtVx/yd+Akefkiz2xrqJAAAAAElFTkSuQmCC',
                        'name': shopUrl, 'street': False, 'street2': False, 'city': False, 'state_id': False,
                        'zip': False, 'country_id': False, 'phone': False, 'email': False, 'website': False,
                        'vat': False, 'company_registry': False, 'parent_id': False}
                companyShop = companyModel.sudo().create(vals);
                companyId = companyShop.id
                # create user for the company
                user = http.request.env['res.users']

                userId = user.sudo().search([("login", "=", shopUrlemail)])
                if not userId:
                    vals = {'company_ids': [[6, False, [companyId]]], 'company_id': companyId,
                            'active': True,
                            'org_id': createdOrg.id,
                            'lang': 'en_US', 'tz': 'Europe/Brussels',
                            'image_1920': False, '__last_update': False,
                            'name': shopUrl, 'email': shopUrlemail, 'login': shopUrlemail,
                            'password': token, 'action_id': False
                            };
                    createdUser = user.sudo().create(vals);
                    createdUserId = createdUser.id
                    if createdUserId:
                        group_shopify_manager_id = http.request.env.ref('social.group_social_manager')
                        group_shopify_manager_id.sudo().update({
                            'users': [(4, createdUserId)]
                        })

                    http.request.httprequest.session.shopify_token = token
                    http.request.httprequest.session.shopify_email = shopUrlemail

                    shopify.ShopifyResource.activate_session(shopify_session)
                    x = 1
            else:
                # never run into this block of code,log for further usage
                x = 1
        user = http.request.env['res.users']

        shopUrlemail = shop_url.split('.')[0] + '@gmail.com'
        user = user.sudo().search([("login", "=", shopUrlemail)])
        shopUrlemail = shop_url.split('.')[0] + '@gmail.com'
        http.request.httprequest.session.shopify_email = shopUrlemail

        shopify.ShopifyResource.activate_session(shopify_session)

        if user:
            db = http.request.env.cr.dbname
            http.request.httprequest.session.shopify_token = token
            http.request.httprequest.session.shopUrlemail = shopUrlemail
            http.request.httprequest.session.shopify_url = shop_url

            redirect = werkzeug.utils.redirect(current_app.BASE_URL + '/shopify_app/home/')
            return redirect

    @http.route('/shopify_app/home/', auth='public')
    def home(self, **kw):
        current_app = DefaultConfig()

        db = http.request.env.cr.dbname
        if http.request.httprequest.session.shopify_token:
            token = http.request.httprequest.session.shopify_token
            shopUrlemail = http.request.httprequest.session.shopUrlemail
            shopify_url = http.request.httprequest.session.shopify_url

            shopRecord = http.request.env['shopify_app.shop'].sudo().search([('url', '=', shopify_url)])
            user_token = shopRecord.code

            uid = http.request.httprequest.session.authenticate(db, shopUrlemail, user_token)

            user_id = http.request.env['res.users'].sudo().search([('id', '=', uid)])

            if shopRecord:
                if not shopRecord.name:
                    session = shopify.Session(shopify_url, current_app.API_VERSION, token)
                    shopify.ShopifyResource.activate_session(session)

                    client = shopify.GraphQL()
                    query = '''
                            {
                              shop {
                                id
                                name
                                email
                                myshopifyDomain
                                contactEmail
                              }
                            }
                        '''

                    result = client.execute(query)
                    d = json.loads(result)
                    shop_name = d['data']['shop']['name']
                    s_email = d['data']['shop']['email']
                    s_contactEmail = d['data']['shop']['contactEmail']
                    shopId = shopRecord.write({
                        'name': shop_name,
                        'email': s_email
                    })

            config = http.request.env['shopify.config.user'].sudo().search([('shop_id', '=', shopRecord.id)],
                                                                           limit=1)
            configMenu = http.request.env['ir.ui.menu'].sudo().search([('name', '=', 'Config User')])
            if config:
                config_id = config.id
                redirectUrl = current_app.BASE_URL + '/web#id=' + str(config_id) + '&active_id=' + str(
                    config_id) + '&model=shopify.config.user&view_type=form&cids=' + str(
                    current_app.CID) + '&menu_id=' + str(configMenu.id)
            else:
                vals = {
                    'user_id': user_id.id,
                    'shop_id': user_id.org_id.id
                }
                config_basic_app = http.request.env['shopify.config.user'].sudo().create(vals)
                config_id = config_basic_app.id
                redirectUrl = current_app.BASE_URL + '/web#id=' + str(config_id) + '&active_id=' + str(
                    config_id) + '&model=shopify.config.user&view_type=form&cids=' + str(
                    current_app.CID) + '&menu_id=' + str(configMenu.id)

            return werkzeug.utils.redirect(redirectUrl)

