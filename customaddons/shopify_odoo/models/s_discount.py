# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
from time import *
from odoo.exceptions import UserError, ValidationError
import requests
import json


class SDiscount(models.Model):
    _name = 's.discount'
    _description = 's_discount'
    _rec_name = 'discount_name'

    discount_name = fields.Char()
    decrease_price = fields.Monetary(default=0.0)
    valid_date_from = fields.Date(default=date.today())
    valid_date_to = fields.Date()

    res_partner_discount_shopify = fields.Many2many('res.partner', string='Customers')
    product_discount_shopify = fields.Many2one('product.template', string='Products')
    currency_id = fields.Many2one('res.currency', string='Currency')

    @api.onchange('valid_date_to')
    def check_valid_date_to(self):
        for rec in self:
            if rec.valid_date_to < rec.valid_date_from:
                raise ValidationError('Valid Date From Must Start Earlier Valid Date To. ')

    def get_customer_shopify(self):
        # current_id = self.env.uid
        current_id = 9
        search_user = self.env['res.users'].search([('id', '=', current_id)], limit=1)
        search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)])[0]

        url = search_user.login + "/admin/api/2021-07/customers.json"

        payload = {}
        headers = {
            'X-Shopify-Access-Token': search_token.token_shop_app
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response)
        print(search_user.id)
        print('current id:', current_id)

    def get_product_shopify(self):
        current_id = 9
        search_user = self.env['res.users'].search([('id', '=', current_id)], limit=1)
        search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)])[0]

        url = search_user.login + "/admin/api/2021-07/products.json"

        payload = {}
        headers = {
            'X-Shopify-Access-Token': search_token.token_shop_app
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response)
