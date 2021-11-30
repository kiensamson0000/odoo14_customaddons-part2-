# -*- coding: utf-8 -*-
import base64
import json
import logging
import os
import random
import string
import traceback

import shopify
import werkzeug

from odoo import http
from odoo.http import request
from ...s_base.controllers.sp_controllers import SpController

_logger = logging.getLogger(__name__)


class SpDataController(SpController):

    def shopify_auth_s_shopify_bought_together(self, **kw):
        # check neccessary param
        # todo validate hmac
        # todo validate shop_url
        if 'shop' in kw:
            # generate permission url
            current_app = request.env.ref('s_shopify_bought_together.s_shopify_bought_together_app').sudo()
            if current_app:
                shopify.ShopifyResource.clear_session()
                shopify.Session.setup(
                    api_key=current_app.sp_api_key,
                    secret=current_app.sp_api_secret_key)
                shopify_session = shopify.Session(kw['shop'], current_app.sp_api_version)
                scope = [
                    "read_products",
                    "read_product_listings",
                    "write_themes",
                    "write_script_tags",
                ]
                redirect_uri = current_app.base_url + "/shopify/finalize/s_shopify_bought_together"
                permission_url = shopify_session.create_permission_url(
                    scope, redirect_uri)
                return werkzeug.utils.redirect(permission_url)

        return "Hello, world"

    def shopify_finalize_s_shopify_bought_together(self, **kw):
        try:
            # check neccessary param
            # todo validate hmac
            # todo validate shop_url
            if 'shop' in kw:
                current_app = request.env.ref('s_shopify_bought_together.s_shopify_bought_together_app').sudo()
                if current_app:
                    shopify.Session.setup(
                        api_key=current_app.sp_api_key,
                        secret=current_app.sp_api_secret_key)
                    shopify_session = shopify.Session(kw['shop'], current_app.sp_api_version)
                    token = shopify_session.request_token(kw)
                    shopify.ShopifyResource.activate_session(shopify_session)
                    # script_src = current_app.webhook_base_url + "/s_shopify_bought_together/static/src/js/s_shopify_bought_together_recommend_product_detail.js"
                    # existedScriptTags = shopify.ScriptTag.find(src=script_src)
                    # if not existedScriptTags:
                    #     scriptTag = shopify.ScriptTag.create({
                    #         "event": "onload",
                    #         "src": script_src
                    #     })
                    # script = shopify.ScriptTag(
                    #     dict(event='onload',
                    #          src=current_app.webhook_base_url + "/s_shopify_bought_together/static/src/js/s_shopify_bought_together_recommend_product_detail.js")).save()

                    if token:
                        # todo check active, unactive shop
                        current_s_sp_shop = request.env['s.sp.shop'].sudo().search([('base_url', '=', kw['shop'])],
                                                                                   limit=1)
                        current_user = http.request.env['res.users'].sudo().search([('login', '=', kw['shop'])],
                                                                                   limit=1)
                        if not current_s_sp_shop:
                            client = shopify.GraphQL()
                            query = '''
                                                      {
                                                        shop {
                                                          id
                                                          name
                                                          email
                                                          myshopifyDomain
                                                          contactEmail
                                                          currencyCode
                                                          billingAddress {
                                                              country
                                                              firstName
                                                              lastName
                                                              name
                                                          }
                                                          currencyFormats{
                                                              moneyFormat
                                                              moneyInEmailsFormat
                                                              moneyWithCurrencyFormat
                                                              moneyWithCurrencyInEmailsFormat
                                                            }
                                                        }
                                                      }
                                                  '''
                            result = client.execute(query)
                            current_shop_dict = json.loads(result)
                            # check and create s_sp_shop, res_user, res_company

                            # create company
                            current_company = http.request.env['res.company'].sudo().search([('name', '=', kw['shop'])],
                                                                                            limit=1)
                            if not current_company:
                                with open(os.path.abspath(
                                        os.path.dirname(os.path.dirname(__file__))) + '/static/src/img/favicon.png',
                                          "rb") as image_file:
                                    encoded_allfetch_image = base64.b64encode(image_file.read())
                                current_company = http.request.env['res.company'].sudo().create({
                                    'logo': False, 'currency_id': 2, 'sequence': 10,
                                    'favicon': encoded_allfetch_image,
                                    'name': kw['shop'], 'street': False, 'street2': False, 'city': False,
                                    'state_id': False,
                                    'zip': False, 'country_id': False, 'phone': False, 'email': False, 'website': False,
                                    'vat': False, 'company_registry': False, 'parent_id': False
                                })
                            # create user

                            # generate password
                            letters = string.ascii_lowercase
                            password_generate = ''.join(random.choice(letters) for i in range(30))
                            current_s_sp_shop = request.env['s.sp.shop'].sudo().create({
                                'name': current_shop_dict['data']['shop']['name'],
                                'base_url': kw['shop'],
                                'email': current_shop_dict['data']['shop']['email'],
                                'currency_code': current_shop_dict['data']['shop']['currencyCode'],
                                'currency_id': 2,
                                'password': password_generate,
                                'first_name': current_shop_dict['data']['shop']['billingAddress']['firstName'] or '',
                                'country': current_shop_dict['data']['shop']['billingAddress']['country'] or '',
                                'full_name': current_shop_dict['data']['shop']['billingAddress']['name'] or '',
                                'last_name': current_shop_dict['data']['shop']['billingAddress']['lastName'] or '',
                                'money_format': current_shop_dict['data']['shop']['currencyFormats'][
                                                    'moneyFormat'] or '',
                                'money_email_format': current_shop_dict['data']['shop']['currencyFormats'][
                                                          'moneyInEmailsFormat'] or '',
                                'money_with_currency_format': current_shop_dict['data']['shop']['currencyFormats'][
                                                                  'moneyWithCurrencyFormat'] or '',
                                'money_currency_email_format': current_shop_dict['data']['shop']['currencyFormats'][
                                                                   'moneyWithCurrencyInEmailsFormat'] or '',
                            })

                            if not current_user:
                                current_user = http.request.env['res.users'].sudo().create({
                                    'company_ids': [[6, False, [current_company.sudo().id]]],
                                    'company_id': current_company.sudo().id,
                                    'active': True,
                                    'lang': 'en_US', 'tz': 'Europe/Brussels',
                                    'image_1920': False, '__last_update': False,
                                    'name': kw['shop'], 'email': current_shop_dict['data']['shop']['email'],
                                    'login': kw['shop'],
                                    'password': password_generate,
                                    'is_client': True,
                                    'action_id': False,
                                    'sp_shop_id': current_s_sp_shop.sudo().id
                                })
                            # todo add user to app group
                            # group = request.env.ref('s_shopify_bought_together.shopify_bought_together_data_group')
                            # if group:
                            #     if current_user.id not in group.sudo().users.ids:
                            #         group.sudo().users = [(4, current_user.id)]

                        else:
                            # todo active shop
                            current_s_sp_shop.status = True
                            # current_user = http.request.env['res.users'].sudo().search([('login', '=', kw['shop'])],
                            #                                                            limit=1)
                            # todo add user to app group
                            # group = request.env.ref('s_shopify_bought_together.shopify_bought_together_data_group')
                            # if group:
                            #     if current_user.id not in group.sudo().users.ids:
                            #         group.sudo().users = [(4, current_user.id)]

                            ## update shop infomation
                            client = shopify.GraphQL()
                            query = '''
                                                                 {
                                                                   shop {
                                                                     id
                                                                     name
                                                                     email
                                                                     myshopifyDomain
                                                                     contactEmail
                                                                     currencyCode
                                                                     enabledPresentmentCurrencies
                                                                     billingAddress {
                                                                         country
                                                                         firstName
                                                                         lastName
                                                                         name
                                                                     }
                                                                     currencyFormats{
                                                                        moneyFormat
                                                                        moneyInEmailsFormat
                                                                        moneyWithCurrencyFormat
                                                                        moneyWithCurrencyInEmailsFormat
                                                                    }
                                                                   }
                                                                 }
                                                             '''
                            result = client.execute(query)
                            current_shop_dict = json.loads(result)
                            current_s_sp_shop.sudo().write({
                                'name': current_shop_dict['data']['shop']['name'],
                                'base_url': kw['shop'],
                                'email': current_shop_dict['data']['shop']['email'],
                                'currency_code': current_shop_dict['data']['shop']['currencyCode'],
                                'first_name': current_shop_dict['data']['shop']['billingAddress']['firstName'] or '',
                                'country': current_shop_dict['data']['shop']['billingAddress']['country'] or '',
                                'full_name': current_shop_dict['data']['shop']['billingAddress']['name'] or '',
                                'last_name': current_shop_dict['data']['shop']['billingAddress']['lastName'] or '',
                                'money_format': current_shop_dict['data']['shop']['currencyFormats'][
                                                    'moneyFormat'] or '',
                                'money_email_format': current_shop_dict['data']['shop']['currencyFormats'][
                                                          'moneyInEmailsFormat'] or '',
                                'money_with_currency_format': current_shop_dict['data']['shop']['currencyFormats'][
                                                                  'moneyWithCurrencyFormat'] or '',
                                'money_currency_email_format': current_shop_dict['data']['shop']['currencyFormats'][
                                                                   'moneyWithCurrencyInEmailsFormat'] or '',
                            })

                            # main_current_shop_currency = request.env['shopify.google.feed.currencies'].sudo().search(
                            #     [('sp_shop_id', '=', request.env.user.sp_shop_id.id),
                            #      ('currencies_id', '=', current_shop_dict['data']['shop']['currencyCode'])], limit=1)
                            # main_currency_values = {
                            #     'currencies_id': current_shop_dict['data']['shop']['currencyCode'],
                            #     'sp_shop_id': current_s_sp_shop.id,
                            #     'is_main_currency': True,
                            # }
                            # # neu tim thay thi write neu khong tim thay thi create
                            # if len(main_current_shop_currency) > 0:
                            #     main_current_shop_currency.write(main_currency_values)
                            # else:
                            #     request.env['shopify.google.feed.currencies'].sudo().create(main_currency_values)
                        # Get Shop Owner
                        if current_s_sp_shop:
                            if not current_s_sp_shop.shop_owner:
                                s_current_shop = shopify.Shop.current()
                                current_s_sp_shop.shop_owner = s_current_shop.attributes['shop_owner']
                        # check and create s_sp_app
                        current_s_sp_app = http.request.env['s.sp.app'].sudo().search(
                            [('sp_shop_id', '=', current_s_sp_shop.sudo().id), ('s_app_id', '=', current_app.id)],
                            limit=1)
                        if not current_s_sp_app:
                            # todo update shop plan
                            current_s_sp_app = http.request.env['s.sp.app'].sudo().create({
                                'sp_shop_id': current_s_sp_shop.sudo().id,
                                's_app_id': current_app.id,
                                'status': True,
                                'token': token,
                                's_plan_id': None
                            })
                            # insert script theme
                            if current_s_sp_shop:
                                if len(current_s_sp_shop.sudo().s_sp_app_ids) > 0:
                                    for app_id in current_s_sp_shop.sudo().s_sp_app_ids:
                                        if app_id.s_app_id:
                                            if app_id.s_app_id.id == current_app.id:
                                                # s_sp_app = current_s_sp_shop.sudo().s_sp_app_ids[0]
                                                session = shopify.Session(app_id.sudo().sp_shop_id.base_url,
                                                                          app_id.sudo().s_app_id.sp_api_version,
                                                                          app_id.sudo().token)
                                                shopify.ShopifyResource.activate_session(session)
                                                product_collection = '<script>\n' \
                                                                     '//Frequently bought together\n' \
                                                                     '  window.productCollections = {\n' \
                                                                     '    collections: {{ product.collections | json }}\n' \
                                                                     '  }\n' \
                                                                     '//Frequently bought together\n' \
                                                                     '</script>'
                                                if product_collection and current_s_sp_shop.sudo().is_insert_collection_theme == False:
                                                    try:
                                                        theme = shopify.Theme.find(role='main')[0].id
                                                        if theme:
                                                            value = shopify.Asset.find('templates/product.liquid',
                                                                                       theme_id=theme).value
                                                            if value:
                                                                if '//Frequently bought together' not in value:
                                                                    current_s_sp_shop.sudo().is_insert_collection_theme = True
                                                                    product_liquid = shopify.Asset.find(
                                                                        'templates/product.liquid',
                                                                        theme_id=theme)
                                                                    product_liquid.value = value + '\n' + product_collection
                                                                    product_liquid.save()
                                                    except Exception as e:
                                                        logging.exception('Error loading data shop ' + str(e))
                            # create product
                            if current_s_sp_app:
                                current_s_sp_app.sudo().shopify_fetch_all_products()
                                queue_product = request.env['s.shopify.product.data.queue'].sudo().search(
                                    [('sp_shop_id', '=',
                                      current_s_sp_shop.sudo().id), ('sp_app_id', '=', current_s_sp_app.sudo().id)])
                                if len(queue_product) > 0:
                                    for queue in queue_product:
                                        if queue:
                                            queue.sudo().cron_update_product_data(webhook=True)
                        else:
                            current_s_sp_app.sudo().write({
                                'status': True,
                                'install_status': True,
                                'token': token,
                                'is_force_update_webhook': False
                            })
                            # insert script theme
                            if current_s_sp_shop and current_s_sp_shop.sudo().is_insert_collection_theme == False:
                                if len(current_s_sp_shop.sudo().s_sp_app_ids) > 0:
                                    for app_id in current_s_sp_shop.sudo().s_sp_app_ids:
                                        if app_id.s_app_id:
                                            if app_id.s_app_id.id == current_app.id:
                                                # s_sp_app = current_s_sp_shop.sudo().s_sp_app_ids[0]
                                                session = shopify.Session(app_id.sudo().sp_shop_id.base_url,
                                                                          app_id.sudo().s_app_id.sp_api_version,
                                                                          app_id.sudo().token)
                                                shopify.ShopifyResource.activate_session(session)
                                                product_collection = '<script>\n' \
                                                                     '//Frequently bought together\n' \
                                                                     '  window.productCollections = {\n' \
                                                                     '    collections: {{ product.collections | json }}\n' \
                                                                     '  }\n' \
                                                                     '//Frequently bought together\n' \
                                                                     '</script>'

                                                if product_collection:
                                                    try:
                                                        theme = shopify.Theme.find(role='main')[0].id
                                                        if theme:
                                                            value = shopify.Asset.find('templates/product.liquid',
                                                                                       theme_id=theme).value
                                                            if value:
                                                                if '//Frequently bought together' not in value:
                                                                    current_s_sp_shop.sudo().is_insert_collection_theme = True
                                                                    product_liquid = shopify.Asset.find(
                                                                        'templates/product.liquid',
                                                                        theme_id=theme)
                                                                    product_liquid.value = value + '\n' + product_collection
                                                                    product_liquid.save()
                                                    except Exception as e:
                                                        logging.exception('Error loading data shop ' + str(e))
                        # add script
                        current_s_sp_app.add_script_to_shop(has_session=True)
                        # add user group bought together
                        group = request.env.ref('s_shopify_bought_together.shopify_bought_together_data_group')
                        if current_user and group and current_s_sp_app:
                            if current_user.sudo().id not in group.sudo().users.ids:
                                group.sudo().users = [(4, current_user.sudo().id)]
                        # add user group plan
                        group_plan_bought_together = request.env.ref(
                            's_shopify_bought_together.shopify_bought_together_data_group_plan')
                        if current_user and group_plan_bought_together:
                            if current_user.sudo().id not in group_plan_bought_together.sudo().users.ids:
                                group_plan_bought_together.sudo().users = [(4, current_user.sudo().id)]
                        # create shop bought together plan submission
                        current_shop_submission = http.request.env[
                            'sp.bought.together.plan'].sudo().search(
                            [('s_sp_shop_id', '=', current_s_sp_shop.sudo().id)],
                            limit=1)
                        if not current_shop_submission:
                            current_shop_submission = http.request.env[
                                'sp.bought.together.plan'].sudo().create({
                                's_sp_shop_id': current_s_sp_shop.sudo().id,
                                's_sp_app_id': current_s_sp_app.sudo().id,
                            })

                        # check if is_first_product_data_action is False then action add queue
                        current_shop_global_setting = http.request.env['s.shopify.data.global.setting'].sudo().search(
                            [('sp_shop_id', '=', current_s_sp_shop.sudo().id),
                             ('sp_app_id', '=', current_s_sp_app.sudo().id)],
                            limit=1)
                        if not current_shop_global_setting:
                            current_shop_global_setting = http.request.env[
                                's.shopify.data.global.setting'].sudo().create({
                                'sp_shop_id': current_s_sp_shop.sudo().id,
                                'sp_app_id': current_s_sp_app.sudo().id,
                            })

                        # if not current_shop_global_setting.is_first_product_data_action:
                        #     print('shopify_fetch_all_products')
                        #     current_s_sp_app.sudo().sudo().shopify_fetch_all_products()
                        #     current_shop_global_setting.is_first_product_data_action = True
                        # action auto login
                        db = http.request.env.cr.dbname
                        request.env.cr.commit()
                        uid = request.session.authenticate(db, kw['shop'], current_s_sp_shop.password)
                        integration_bought_together_id = http.request.env[
                            'sp.bought.together.integration'].sudo().search(
                            [('s_sp_app_id', '=', current_s_sp_app.sudo().id),
                             ('s_sp_shop_id', '=', current_user.sudo().sp_shop_id.id)],
                            limit=1)
                        bought_together_menu = request.env.ref(
                            's_shopify_bought_together.sp_frequently_bought_together_menu').id
                        bought_together_action = request.env.ref(
                            's_shopify_bought_together.open_form_integration_action').id
                        if bought_together_menu:
                            redirectUrl = current_app.base_url + '/web?#menu_id=' + str(
                                bought_together_menu)
                            return werkzeug.utils.redirect(redirectUrl)
                        # if integration_bought_together_id:
                        #     if current_shop_submission.current_plan:
                        #         return werkzeug.utils.redirect(
                        #             '/web#id=%s&view_type=form&model=sp.bought.together.integration' % integration_bought_together_id.id)
                        #     else:
                        #         return werkzeug.utils.redirect(
                        #             '/web#id=%s&view_type=form&model=sp.bought.together.plan' % current_shop_submission.id)
                        # else:
                        #     return werkzeug.utils.redirect(
                        #         '/web#id=%s&view_type=form&model=sp.bought.together.plan' % current_shop_submission.id)
        except Exception as ex:
            _logger.error(traceback.format_exc())
            return werkzeug.utils.redirect('https://google.com/')

        return werkzeug.utils.redirect('https://shopify.com/')

    @http.route(
        '/shopify_data/s_shopify_bought_together/get_product_not_display/<string:shop>',
        auth='public', type='json', cors='*',
        csrf=False)
    def odoo_get_product_not_display(self, shop, **kw):
        recommend_tuning_id = http.request.env['sp.bought.together.recommend.tuning'].sudo().search(
            [('s_sp_shop_id.base_url', '=', shop)], limit=1)
        if recommend_tuning_id:
            # product excluded
            no_of_product_excluded = recommend_tuning_id.count_product_excluded
            # widget hidden
            no_of_widget_hidden = recommend_tuning_id.count_widget_hidden
            product_data = {'product_excluded': no_of_product_excluded, 'widget_hidden': no_of_widget_hidden}
        else:
            product_data = {'product_excluded': '', 'widget_hidden': ''}
        return product_data

    @http.route(
        '/shopify_data/s_shopify_bought_together/fetch_product/<string:product_id>/<string:vendor>/<string:shop>',
        auth='public', type='json', cors='*',
        csrf=False)
    def odoo_fetch_product(self, product_id, vendor, shop, **kw):
        # product
        sp_product_tmpl = http.request.env['s.shopify.product.template'].sudo().search(
            [('shopify_tmpl_id', '=', product_id), ('sp_shop_id.base_url', '=', shop)], limit=1)
        # turn on app
        sp_integration_id = http.request.env['sp.bought.together.home'].sudo().search(
            [('enable_recommendation', '=', True), ('s_sp_shop_id.base_url', '=', shop)], limit=1)
        # visual preference
        sp_visual_preference_id = http.request.env['sp.bought.together.visual.preference'].sudo().search(
            [('s_sp_shop_id.base_url', '=', shop)], limit=1)
        # filter collection
        random_recommendations_filter_collection = http.request.env[
            'sp.bought.together.recommend.tuning'].sudo().search(
            [('is_random_recommendations', '=', True),
             ('filter_random_recommendations', '=', 'filter_by_collection'),
             ('s_sp_shop_id.base_url', '=', shop)], limit=1)
        # recommend tuning
        recommend_tuning_id = http.request.env['sp.bought.together.recommend.tuning'].sudo().search(
            [('s_sp_shop_id.base_url', '=', shop)], limit=1)
        # general setting
        general_setting_id = http.request.env['sp.bought.together.general.settings'].sudo().search(
            [('s_sp_shop_id.base_url', '=', shop)], limit=1)
        arr_product = []
        if len(sp_integration_id) > 0:
            if sp_product_tmpl:
                if len(sp_product_tmpl.sudo().product_bought_together_ids) > 0 or len(
                        random_recommendations_filter_collection) > 0:
                    # visual preference
                    vals = {
                        'title_bought_together': sp_visual_preference_id.sudo().title_bought_together if len(
                            sp_visual_preference_id) > 0 and sp_visual_preference_id.sudo().title_bought_together else 'Frequently Bought Together',
                        'color_title': sp_visual_preference_id.sudo().color_title_code if len(
                            sp_visual_preference_id) > 0 else None,
                        'color_message': sp_visual_preference_id.sudo().color_message_code if len(
                            sp_visual_preference_id) > 0 else None,
                        'message_bought_together': sp_visual_preference_id.sudo().message_bought_together if len(
                            sp_visual_preference_id) > 0 else ' ',
                        'product_name': sp_visual_preference_id.sudo().product_name_code if len(
                            sp_visual_preference_id) > 0 else None,
                        'color_select': sp_visual_preference_id.sudo().color_select_code if len(
                            sp_visual_preference_id) > 0 else None,
                        'option_product': sp_visual_preference_id.sudo().option_product_code if len(
                            sp_visual_preference_id) > 0 else None,
                        'price_product': sp_visual_preference_id.sudo().price_product_code if len(
                            sp_visual_preference_id) > 0 else None,
                        'product_compare_price': sp_visual_preference_id.sudo().product_compare_price_code if len(
                            sp_visual_preference_id) > 0 else None,
                        'text_total_price_product': sp_visual_preference_id.sudo().text_total_price_product if len(
                            sp_visual_preference_id) > 0 else 'Total',
                        'total_price_product_color': sp_visual_preference_id.sudo().total_price_product_color_code if len(
                            sp_visual_preference_id) > 0 else None,
                        'add_to_cart': sp_visual_preference_id.sudo().add_to_cart_code if len(
                            sp_visual_preference_id) > 0 else None,
                        'add_to_cart_text_color': sp_visual_preference_id.sudo().add_to_cart_text_color_code if len(
                            sp_visual_preference_id) > 0 else None,
                        'background_product_image': sp_visual_preference_id.sudo().background_product_image if len(
                            sp_visual_preference_id) > 0 else None,
                        'add_to_cart_text': sp_visual_preference_id.sudo().add_to_cart_text if len(
                            sp_visual_preference_id) > 0 and sp_visual_preference_id.sudo().add_to_cart_text else 'Add to cart',
                        'money_format': sp_integration_id.sudo().s_sp_app_id.sp_shop_id.money_format if sp_integration_id.sudo().s_sp_app_id.sp_shop_id.money_format else '${{amount}}',
                        'judge_me_enable': sp_visual_preference_id.sudo().judge_me_enable if len(
                            sp_visual_preference_id) > 0 else False,
                        'judge_me_token': sp_visual_preference_id.sudo().judge_me_token if len(
                            sp_visual_preference_id) > 0 and sp_visual_preference_id.sudo().judge_me_token != '' else False,
                    }
                    if vals:
                        arr_product.append({'visual_preference': vals})
                    # lay url shop
                    if sp_product_tmpl.sudo().sp_shop_id:
                        if sp_product_tmpl.sudo().sp_shop_id.base_url:
                            arr_product.append({'base_url': sp_product_tmpl.sudo().sp_shop_id.base_url})
                    # lay id cac sp goi y mua cung nhau
                    product_data = []
                    for product_bought_together in sp_product_tmpl.sudo().product_bought_together_ids:
                        if product_bought_together:
                            product_data.append(product_bought_together.sudo().shopify_product_handle)
                    if len(product_data) > 0:
                        arr_product.append({'product': product_data})
                    else:
                        arr_product.append({'product': 0})
                    if len(random_recommendations_filter_collection) > 0:
                        number_product = random_recommendations_filter_collection.sudo().number_recommendations - len(
                            random_recommendations_filter_collection.sudo().global_recommendations_ids)
                        if number_product > 0:
                            arr_product.append({'number_product_collection': number_product})
                        else:
                            arr_product.append({'number_product_collection': '0'})
                    else:
                        arr_product.append({'number_product_collection': '0'})

                    if recommend_tuning_id:
                        # get product widget disable
                        list_widget_disable = []
                        if len(recommend_tuning_id.sudo().product_template_widget_disable_ids) > 0:
                            for widget in recommend_tuning_id.sudo().product_template_widget_disable_ids:
                                if widget.shopify_tmpl_id:
                                    list_widget_disable.append(widget.shopify_tmpl_id)
                        if len(list_widget_disable) > 0:
                            arr_product.append({'widget_disable': list_widget_disable})
                        else:
                            arr_product.append({'widget_disable': '0'})
                        # get product product excluded
                        list_product_excluded = []
                        if len(recommend_tuning_id.sudo().product_template_product_excluded_ids) > 0:
                            for product_exclude in recommend_tuning_id.sudo().product_template_product_excluded_ids:
                                if product_exclude.shopify_tmpl_id:
                                    list_product_excluded.append(product_exclude.shopify_tmpl_id)
                        if len(list_product_excluded) > 0:
                            arr_product.append({'product_exclude': list_product_excluded})
                        else:
                            arr_product.append({'product_exclude': '0'})

                    # general settings
                    vals = {
                        'widget_position': general_setting_id.widget_position if general_setting_id else None,
                        'redirect_page': general_setting_id.redirect_page if general_setting_id else None
                    }
                    if vals:
                        arr_product.append({'general_settings': vals})
                    arr_product.append({'main_product_handle': sp_product_tmpl.shopify_product_handle})
        return arr_product

    def shopify_web_hook_app_uninstalled(self, shop, app, object_name, action, **kw):
        if shop:
            # todo removed user inside group
            group = request.env.ref('s_shopify_bought_together.shopify_bought_together_data_group')
            current_user = http.request.env['res.users'].sudo().search([('login', '=', str(shop))], limit=1)
            if group and current_user:
                if current_user.sudo().id in group.sudo().users.ids:
                    group.sudo().users = [(3, current_user.sudo().id)]
                    print("Uninstall app " + str(shop) + ": removed user inside group")

    # @http.route('/bought_together/plan/accept/<int:model_id>/<int:plan_id>', type='http', auth='public')
    # def plan_accept_bought_together(self, model_id=None, plan_id=None):
    #     shop = request.params['shop'] if 'shop' in request.params else ''
    #     shopify_admin = 'https://' + shop + '/admin' if shop != '' else 'https://shopify.com/'
    #     try:
    #         if not 'charge_id' in request.params:
    #             raise Exception('Missing Charge ID. Please try again')
    #         if not plan_id:
    #             raise Exception('Missing Plan Parameter. Please try again')
    #         if not model_id:
    #             raise Exception('Missing Current Shop. Please try again')
    #         # shop = request.session['shop_url']
    #         model = request.env['s.sp.app'].sudo().browse(model_id)
    #         if model:
    #             charge = model.activate_plan(request.params['charge_id'], plan_id=plan_id)
    #             # todo add user to app group
    #             current_app = request.env.ref('s_shopify_bought_together.s_shopify_bought_together_app')
    #             if not current_app:
    #                 raise Exception('Could not find s_app.')
    #             current_user = request.env['res.users'].sudo().search([('login', '=', shop)], limit=1)
    #             if not current_user:
    #                 raise Exception('Could not find Current user.')
    #             current_s_sp_app = http.request.env['s.sp.app'].sudo().search(
    #                 [('sp_shop_id', '=', current_user.sudo().sp_shop_id.id), ('s_app_id', '=', current_app.id)],
    #                 limit=1)
    #             if not current_s_sp_app:
    #                 raise Exception('Could not find Shop App')
    #             group = request.env.ref('s_shopify_bought_together.shopify_bought_together_data_group')
    #             if not group:
    #                 raise Exception('Could not find bundle data group.')
    #             if current_user and group and current_s_sp_app and current_s_sp_app.sudo().s_charge_id:
    #                 if current_user.sudo().id not in group.sudo().users.ids:
    #                     group.sudo().users = [(4, current_user.sudo().id)]
    #             bought_together_menu = request.env.ref(
    #                 's_shopify_bought_together.sp_frequently_bought_together_menu').id
    #             if bought_together_menu:
    #                 redirectUrl = current_app.sudo().base_url + '/web?#menu_id=' + str(
    #                     bought_together_menu)
    #                 return werkzeug.utils.redirect(redirectUrl)
    #
    #     except Exception as e:
    #         _logger.error(traceback.format_exc())
    #     return werkzeug.utils.redirect(shopify_admin)

    @http.route('/bought_together/af_customers_redact', type='json', auth="public", csrf=False)
    def bought_together_customers_redact(self):
        return 'Done'

    @http.route('/bought_together/af_customers_data_request', type='json', auth="public", csrf=False)
    def bought_together_customers_data_redact(self):
        return 'Done'

    @http.route('/bought_together/af_shop_redact', type='json', auth="public", csrf=False)
    def bought_together_shop_redact(self):
        return 'Done'
