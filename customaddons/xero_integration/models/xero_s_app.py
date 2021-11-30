# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import hashlib
import json
import requests
import calendar
import time


class SApp(models.Model):
    _name = 'xero.s.app'
    _description = 'xero_s_app'
    _rec_name = 'app_name'

    app_name = fields.Char("App Name")
    client_id = fields.Char("Client ID")
    client_secret = fields.Char("Client secret")
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('connect', 'Connect'),
    #     ('disconnect', 'Disconnect'),
    # ], string="Status", readonly=True, default="draft", compute="_check_status", tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('connect', 'Connect'),
        ('disconnect', 'Disconnect'),
    ], string="Status", readonly=True, default="draft", tracking=True)

    def xero_connect(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://odoo.website/xero/auth/' + str(self.app_name),
            'target': 'new'
        }

    # def _check_status(self):
    #     shop_xero = self.env['xero.s.shop'].sudo().search([('app_name', '=', self.app_name)], limit=1)
    #     print(shop_xero)
    #     # if shop_xero.access_token:
    #     #     self.state = 'connect'


    def xero_disconnect(self):
        self.state = 'disconnect'
        shop_xero = self.env['xero.s.shop'].sudo().search([('app_name', '=', self.app_name)], limit=1)
        if shop_xero:
            shop_xero.access_token = False
            shop_xero.refresh_token = False
        else:
            raise UserError("Doesn't exist shop_xero!")

        # Removing connections
        #If you would like to remove an individual tenant connection from your app
        #(e.g. a user wants to disconnect one of their orgs) you can make a DELETE request on the Connections endpoint:
        # DELETE
        # https: // api.xero.com / connections / {connectionId}
        # Authorization: "Bearer " + access_token


