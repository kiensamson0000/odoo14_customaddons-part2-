import requests
import json

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class ProductCategoriesInherit(models.Model):
    _inherit = "product.category"
    _description = "Inherit product category"

    # haravan_product_cate = fields.Char()
    check_cate_haravan = fields.Boolean('check cate haravan')

    def get_categories_haravan_sale(self):
        try:
            # current_seller = self.env['haravan.seller'].sudo().search([])[0] (chua connect duoc)
            token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
            url = "https://apis.haravan.com/com/products/types.json"
            payload = {}
            headers = {
                # 'Authorization': 'Bearer ' + current_seller.token_connect
                'Authorization': 'Bearer ' + token_connect
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            result_categories = response.json()
            categories = result_categories["types"]
            val = {}
            if categories:
                for cate in categories:
                    try:
                        val['name'] = cate
                        val['check_cate_haravan'] = True
                    except Exception as e:
                        print(e)
                    existed_cate = self.env['product.category'].search([('name', '=', cate)], limit=1)
                    if not existed_cate:
                        self.env['product.category'].create(val)
                    else:
                        existed_cate.write(val)
            else:
                raise ValidationError(_('Sync Category of Haravan is Fail.'))
        except Exception as e:
            print(e)