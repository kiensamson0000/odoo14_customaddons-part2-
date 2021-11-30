import requests
import json

from odoo import fields, models, api


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"
    _description = "Inherit res.partner"

    haravan_customer_id = fields.Char('ID Customer')
    check_partner_haravan = fields.Boolean(default=False)


class HaravanVendors(models.Model):
    _name = "haravan.vendors"
    _description = "API Vendors Haravan"

    ### 1 Vendors(Haravan) ~ 1 Partner
    def get_vendors_haravan_sale(self):
        # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
        token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
        url = "https://apis.haravan.com/com/products/vendors.json"
        payload = {}
        headers = {
            # 'Authorization': 'Bearer ' + current_seller.token_connect
            # 'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token_connect
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        result_partner = response.json()
        partners = result_partner["vendors"]
        val = {}
        if partners:
            for ven in partners:
                val['name'] = ven
                val['check_partner_haravan'] = True
                existed_partner = self.env['res.partner'].search([('name', '=', ven)], limit=1)
                if not existed_partner:
                    self.env['res.partner'].create(val)
                else:
                    existed_partner.write(val)
