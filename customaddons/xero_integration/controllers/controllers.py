import base64

import requests
import json
import logging
from odoo import http, _
from datetime import datetime, timedelta

from odoo.http import request, Response
import werkzeug
from werkzeug.utils import redirect
import re
from urllib.request import urlopen

_logger = logging.getLogger(__name__)


class XeroApp(http.Controller):
    @http.route('/xero/auth/<string:name>', auth='public', type='http', website=True)
    def xero_auth(self, name=None, **kwarg):
        search_app = request.env['xero.s.app'].sudo().search([('app_name', '=', name)], limit=1)
        base_url = "https://odoo.website"
        redirect_uri = base_url + "/xero/finalize/" + name
        client_id = search_app.client_id
        scope = "offline_access accounting.transactions openid profile email accounting.contacts accounting.settings"
        auth_url = "https://login.xero.com/identity/connect/authorize?response_type=code&client_id=" + client_id + "&redirect_uri=" + redirect_uri + "&scope=" + scope + "&state=123"
        return werkzeug.utils.redirect(auth_url)


    @http.route('/xero/finalize/<string:name>', auth='public', type='http', website=True)
    def shopify_finalize(self, name=None, **kwargs):
        if kwargs.get('code'):
            # print("\n\nIn controllers code"+ kwarg+ "\n\n\n",kwarg.get('code'))
            base_url = "https://odoo.website"
            access_token_url = 'https://identity.xero.com/connect/token'
            xero_id = request.env['xero.s.app'].sudo().search([('app_name', '=', name)])
            if xero_id:
                client_id = xero_id.client_id
                client_secret = xero_id.client_secret
                redirect_uri = base_url + "/xero/finalize/" + name
                # print("base64.b64encode(client_id+""::::::::::::",base64.b64encode(client_id+":"+client_secret))
                data = client_id + ":" + client_secret
                encodedBytes = base64.b64encode(data.encode("utf-8"))
                encodedStr = str(encodedBytes, "utf-8")
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': "Basic " + encodedStr
                }
                data_token = {
                    'code': kwargs.get('code'),
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code'
                }
                access_token = requests.post(access_token_url, data=data_token, headers=headers, verify=False)
                # access_token = requests.post(access_token_url, data=data_token, headers=headers)
                if access_token:
                    parsed_token_response = json.loads(access_token.text)
                    shop_xero = request.env['xero.s.shop'].sudo().search([('shop_app_ids', '=', xero_id.id)], limit=1)

                    if parsed_token_response:
                        token_vals = {
                            'app_name': name,
                            'id_token': parsed_token_response.get('id_token'),
                            'access_token': parsed_token_response.get('access_token'),
                            'expires_in': parsed_token_response.get('expires_in'),
                            'shop_app_ids': [(4, xero_id.id)],
                            'refresh_token': parsed_token_response.get('refresh_token'),
                        }
                        if shop_xero:
                            shop_xero.sudo().write(token_vals)
                        else:
                            request.env['xero.s.shop'].sudo().create(token_vals)
                    if shop_xero.access_token:
                        xero_id.sudo().write({
                            'state': 'connect'
                        })
                    else:
                        xero_id.sudo().write({
                            'state': 'disconnect'
                        })

                    # 5. Check the tenants you’re authorized to access
                    # header1 = {
                    #     'Authorization': "Bearer " + xero_id.access_token,
                    #     'Content-Type': 'application/json'
                    # }
                    # # print("header1:::::::::::::::",header1)
                    # xero_tenant_response = requests.request('GET', 'https://api.xero.com/connections', headers=header1)
                    #
                    # parsed_tenent = json.loads(xero_tenant_response.text)
                    # if parsed_tenent:
                    #     for tenant in parsed_tenent:
                    #         if 'tenantId' in tenant:
                    #             xero_id.xero_tenant_id = tenant.get('tenantId')
                    #             xero_id.xero_tenant_name = tenant.get('tenantName')
                    #     _logger.info(_("Authorization successfully!"))

                        # country_name = xero_id.import_organization()  # function return country name import_organization()
                        # xero_id.write({
                        #     'xero_country_name': country_name
                        # })

        return "Authenticated Successfully..!! \n You can close this window now"

    @http.route('/xero/render/<string:name>', auth='public', type='http', website=True)
    def xero_render(self, name=None, **kwargs):
        return "hello 123321431212"

        # a = request.search()
        # return request.render("xero_integration.xero_main", {
        #     'sale_account': 's'
        # })