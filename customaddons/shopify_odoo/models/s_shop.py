# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import json
import base64
import werkzeug
from werkzeug.utils import redirect


class SShop(models.Model):
    _name = 's.shop'
    _description = 's_shop'
    _rec_name = 'shop_owner'

    shop_base_url = fields.Char()
    shop_owner = fields.Char()
    shop_user = fields.Char()
    shop_password = fields.Char()
    shop_currency = fields.Char()
    shop_user_id = fields.Integer()

    shop_app_ids = fields.Many2many('s.app', string='App Shopify')
    shopify_shop_product_temp = fields.One2many('product.template', 'shopify_shop_id')

    @api.onchange('shop_user_id')
    def _add_shop_user_id(self):
        for rec in self:
            rec.shop_user_id = self.env.uid


class XeroSShop(models.Model):
    _name = 'xero.s.shop'
    _description = 'xero_s_shop'
    _rec_name = 'app_name'

    app_name = fields.Char("App Name")
    id_token = fields.Char("ID Token")
    access_token = fields.Char("Access Token")
    expires_in = fields.Integer("Expires In")
    refresh_token = fields.Char("Refresh Token")
    shop_user_id = fields.Integer()

    shop_app_ids = fields.Many2many('xero.s.app', string='App Xero')
    # xero_shop_product_temp = fields.One2many('product.template', 'xero_shop_id')

    @api.onchange('shop_user_id')
    def _add_shop_user_id(self):
        for rec in self:
            rec.shop_user_id = self.env.uid


    # create button refresh tokens, after 30 minutes
    #(crete cron job call after 30 minutes)
    def xero_refresh_token(self):
        base_url = "https://odoo.website"
        access_token_url = 'https://identity.xero.com/connect/token'
        xero_id = self.env['xero.s.app'].sudo().search([('app_name', '=', self.app_name)], limit=1)
        if xero_id:
            client_id = xero_id.client_id
            client_secret = xero_id.client_secret
            data = client_id + ":" + client_secret
            encodedBytes = base64.b64encode(data.encode("utf-8"))
            encodedStr = str(encodedBytes, "utf-8")
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': "Basic " + encodedStr
            }
            data_token = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            access_token = requests.request("POST", access_token_url, data=data_token, headers=headers, verify=False)
            if access_token:
                parsed_token_response = json.loads(access_token.text)
                if parsed_token_response:
                    shop_xero = self.env['xero.s.shop'].sudo().search([('app_name', '=', self.app_name)], limit=1)
                    shop_xero.sudo().write({
                        'access_token': parsed_token_response.get('access_token'),
                        'refresh_token': parsed_token_response.get('refresh_token'),
                    })

    # create button sync xero main view
    def sync_xero(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://odoo.website/xero/render/' + str(self.app_name),
            'target': 'new'
        }