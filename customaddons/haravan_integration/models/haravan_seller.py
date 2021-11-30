import requests
import json

from odoo import fields, models, api, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

class HaravanSeller(models.Model):
    _name = "haravan.seller"
    _description = "Information Seller Haravan"

    code = fields.Char('Code')
    client_id = fields.Char('Client ID')
    client_secret = fields.Char('Client Secret')
    grant_type = fields.Char('Grant type')
    redirect_uri = fields.Char('Redirect uri')
    token_connect = fields.Char('Token Seller')

    def action_view_config(self):
        res_id = self.env['haravan.seller'].sudo().search([('client_id', '!=', False)])
        return {
            'name': _('Config connection Haravan API'),
            'view_mode': 'form',
            'view_id': self.env.ref('haravan_integration.haravan_seller_view_form').id,
            'res_model': 'haravan.seller',
            'context': "{'create': False}",
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': res_id.id if res_id else False,
        }

    def get_token_haravan(self):
        url = "https://accounts.haravan.com/connect/token"
        #### Error chưa get được token haravan
        # payload = 'code=' + self.code + '&client_id=' + self.client_id + '&client_secret=' + self.client_secret + '&grant_type=' + self.grant_type + '&redirect_uri=' + self.redirect_uri
        payload = json.dumps({
            "code": self.code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": self.grant_type,
            "redirect_uri": self.redirect_uri
        })
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)
        if response.json()["error"]:
            raise ValidationError(_('Values Code / Client ID / Client Secret / Grant type / Redirect uri is wrong.'))
        else:
            token_connect = response.json()["access_token"]
            val = {
                'code': self.code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': self.grant_type,
                'redirect_uri': self.redirect_uri,
                'token_connection': token_connect
            }
            existed_secret = self.env['haravan.seller'].search([('client_secret', '=', self.client_secret)], limit=1)
            if not len(existed_secret):
                self.env['haravan.seller'].create(val)
            else:
                existed_secret.write(val)