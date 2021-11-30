import requests
import json

from odoo import fields, models, api, _

class HaravanCollections(models.Model):
    _name = "haravan.collections"
    _description = "API Collections Haravan"

    collec_id = fields.Char('ID Collection')
    collec_title = fields.Char('Name Collection')
    collec_descriptions = fields.Char('Description')
    collec_url_image = fields.Char('Image')
    collec_created_at = fields.Char('Created at')

    #############################
    ## USE API COLLECTIONS "HARAVAN INTEGRATION" ON Module "Haravan Integration"
    def get_collections_haravan(self):
        try:
            # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
            token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
            url = "https://apis.haravan.com/com/custom_collections.json"
            payload = {}
            headers = {
                # 'Authorization': 'Bearer ' + current_seller.token_connect
                'Authorization': 'Bearer ' + token_connect
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            result_collections = response.json()
            collections = result_collections["custom_collections"]
            val = {}
            if collections:
                for collection in collections:
                    try:
                        val['collec_id'] = collection['id']
                        val['collec_title'] = collection['title']
                        val['collec_descriptions'] = collection['body_html']
                        if collection['image']:
                            val['collec_url_image'] = collection['image']['src']
                            val['collec_created_at'] = collection['image']['created_at']
                    except Exception as e:
                        print(e)
                    existed_collec = self.env['haravan.collections'].search([('collec_id', '=', collection['id'])],
                                                                            limit=1)
                    if not existed_collec:
                        self.env['haravan.collections'].create(val)
                    else:
                        existed_collec.write(val)
        except Exception as e:
            print(e)

    ### VÌ TRONG PRODUCT KHONG CO COLLECTION => CHUYỂN SANG "product_type ~ categories"
    #############################
    ## USE API CATEGORY "HARAVAN INTEGRATION" on app "Sales"
    #############################
    # def get_collections_haravan_sale(self):
    #     # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
    #     token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
    #     url = "https://apis.haravan.com/com/products/types.json"
    #     payload = {}
    #     headers = {
    #         # 'Authorization': 'Bearer ' + current_seller.token_connect
    #         'Authorization': 'Bearer ' + token_connect
    #     }
    #     response = requests.request("GET", url, headers=headers, data=payload)
    #     result_collections = response.json()
    #     collections = result_collections["custom_collections"]
    #     val = {}
    #     if collections:
    #         for collection in collections:
    #             try:
    #                 val['collec_id'] = collection['id']
    #                 val['collec_title'] = collection['title']
    #                 val['collec_descriptions'] = collection['body_html']
    #                 if collection['image']:
    #                     val['collec_url_image'] = collection['image']['src']
    #                     val['collec_created_at'] = collection['image']['created_at']
    #             except Exception as e:
    #                 print(e)
    #             existed_collec = self.env['product.category'].search([('haravan_collec_id', '=', collection['id'])],
    #                                                                  limit=1)
    #             if not existed_collec:
    #                 self.env['product.category'].sudo().create(val)
    #             else:
    #                 existed_collec.write(val)