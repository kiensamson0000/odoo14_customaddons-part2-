import requests
import json

from odoo import fields, models, api

class HaravanCompanies(models.Model):
    _name = "haravan.companies"
    _description = "API Company Haravan"

    vendors_name = fields.Char()
    id = fields.Char()

    ### Shop là company(1 Shop)
    def get_companies_haravan_sale(self):
        # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
        token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
        url = "https://apis.haravan.com/com/shop.json"
        payload = {}
        headers = {
            # 'Authorization': 'Bearer ' + current_seller.token_connect
            # 'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token_connect
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        result_companies = response.json()
        companies = result_companies["shop"]
        val = {}
        if companies:
            val['name'] = companies['name']
            val['street'] = companies['address1']
            val['city'] = companies['province']
            # val['country_id'] = companies['country_code']
            val['email'] = companies['email']
            val['phone'] = companies['phone']
            # val['currency_id'] = int(companies['currency'])
            val['favicon'] = None
            val['website'] = companies['domain']
            val['zip'] = companies['zip']
            val['phone'] = companies['phone']
            val['check_company_haravan'] = True
            existed_company = self.env['res.company'].search([('name', '=', companies['name'])], limit=1)
            if not existed_company:
                self.env['res.company'].sudo().create(val)
            else:
                existed_company.write(val)