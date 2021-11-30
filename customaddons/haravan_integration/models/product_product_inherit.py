import requests
import json
import re

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class ProductProductInheritharavan(models.Model):
    _inherit = "product.product"
    _description = 'Inherit product product'

    haravan_product_id = fields.Char(string='Product ID', store=True)
    haravan_variant_product_id = fields.Char(string='Product ID', store=True)  #
    haravan_variant_vendors = fields.Char('Vendor')
    haravan_variant_image_url = fields.Char(store=True)  # save url image --> hien thi trong view = (widget="image") #1
    haravan_variant_created_at = fields.Char('Created at')
    haravan_variant_updated_at = fields.Char('Updated at')
    haravan_variant_inventory_quantity = fields.Integer(string='Inventory Quantity')
    check_product_variant_haravan = fields.Boolean()
    check_inventory_management = fields.Boolean()

    @api.constrains('haravan_variant_inventory_quantity')
    def check_haravan_variant_inventory_quantity(self):
        for rec in self:
            if rec.haravan_variant_inventory_quantity < 0:
                raise ValidationError(_("Inventory Quantity Product need more than 0."))

    def get_product_variant_haravan_sale(self):
        try:
            # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
            token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
            url = "https://apis.haravan.com/com/products.json"
            payload = {}
            headers = {
                # 'Authorization': 'Bearer ' + current_seller.token_connect
                'Authorization': 'Bearer ' + token_connect
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            result_products = response.json()
            list_product = result_products['products']
            val = {}
            for product in list_product:
                if 'id' in product:
                    list_product_variants = product['variants']
                    for product_variant in list_product_variants:
                        existed_cate_product = self.env['product.category'].search(
                            [('name', '=', product['product_type'])], limit=1)
                        if existed_cate_product:
                            val['categ_id'] = existed_cate_product.id
                        val['name'] = product['title'] + ' ' + product_variant['title']
                        val['haravan_variant_product_id'] = product_variant['id']
                        val['default_code'] = product_variant['id']
                        # if product_variant['barcode'] != None:
                        #     val['barcode'] = product_variant['barcode']
                        val['lst_price'] = product_variant['price']
                        val['haravan_variant_created_at'] = product_variant['created_at']
                        val['haravan_variant_updated_at'] = product_variant['updated_at']
                        val['haravan_variant_inventory_quantity'] = int(product_variant['inventory_quantity'])
                        val['check_product_variant_haravan'] = True
                        if product_variant['inventory_management'] == 'haravan':
                            val['check_inventory_management'] = True
                        val['sale_ok'] = True
                        val['purchase_ok'] = False
                        val['taxes_id'] = None
                        val['is_published'] = True
                        val['haravan_product_id'] = product['id']
                        val['haravan_variant_vendors'] = product['vendor']
                        ##### val['type'] = 'product'
                        val['description'] = re.sub(r'<.*?>', '', product['body_html'])
                        if product['images']:
                            for image in product['images']:
                                if 'id' in image:
                                    val['haravan_variant_image_url'] = product["images"][0]["src"]
                        existed_product_variant = self.env["product.product"].search(
                            [('haravan_variant_product_id', '=', product_variant['id'])],
                            limit=1)
                        if not existed_product_variant:
                            self.env["product.product"].sudo().create(val)
                        else:
                            existed_product_variant.write(val)
        except Exception as e:
            print(e)

    def update_variant_inventory_quantity_sales(self):
        try:
            # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
            token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
            url = "https://apis.haravan.com/com/variants/" + self.haravan_variant_product_id + ".json"
            payload = json.dumps({
                "variant": {
                    "id": self.haravan_variant_product_id,
                    "inventory_quantity": int(self.qty_available)
                }
            })
            headers = {
                # 'Authorization': 'Bearer ' + current_seller.token_connect
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token_connect
            }
            response = requests.request("PUT", url, headers=headers, data=payload)
            print(response.text)  # CHECK
            if 'errors' in response.json():
                raise UserError(_(response.json()["errors"]))
        except Exception as e:
            raise ValidationError(str(e))
