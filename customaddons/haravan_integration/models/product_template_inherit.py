import requests
import json
import re

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'
    _description = 'Inherit product template'

    haravan_product_id = fields.Char(string='Product ID', store=True)
    haravan_product_type = fields.Char("Product Type")
    haravan_vendors = fields.Char('Vendor')
    haravan_tags = fields.Char("Tag")
    haravan_image_url = fields.Char(store=True)  # save url image --> hien thi trong view = (widget="image") #1
    haravan_created_at = fields.Char('Created at')
    haravan_updated_at = fields.Char('Updated at')
    # haravan_inventory_quantity = fields.Integer(string='Inventory Quantity', required=True)
    check_product_haravan = fields.Boolean()

    # @api.constrains('haravan_inventory_quantity')
    # def check_haravan_inventory_quantity(self):
    #     for rec in self:
    #         if rec.haravan_inventory_quantity < 0:
    #             raise ValidationError(_("Inventory Quantity Product need more than 0."))

    def get_product_haravan_sale(self):
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
                    ### link ref to categories, company
                    ### Install app Inventory
                    ### Note: get "category,company" trước nếu không bị error
                    existed_cate_product = self.env['product.category'].search(
                        [('name', '=', product['product_type'])], limit=1)
                    if existed_cate_product:
                        val['categ_id'] = existed_cate_product.id
                    ### API get product ko tra ve ten company nen ko the search lay ten company de hien thi nhu categories
                    # existed_company = self.env['res.company'].search([('name', '=', companies['name'])], limit=1)
                    # val['company_id'] = existed_company_product.id
                    val['name'] = product['title']
                    val['sale_ok'] = True
                    val['purchase_ok'] = False
                    val['haravan_product_id'] = product['id']
                    val['haravan_product_type'] = product['product_type']
                    val['default_code'] = product['id']
                    val['haravan_tags'] = product['tags']
                    ##### val['type'] = 'product'
                    val['taxes_id'] = None
                    val['is_published'] = True  # field in model Webiste(Shop) pulish product
                    # standard_price, # barcode
                    val['haravan_vendors'] = product['vendor']
                    val['haravan_created_at'] = product['created_at']
                    val['haravan_updated_at'] = product['updated_at']
                    ### list_price: min_price tren web
                    if product["variants"]:
                        min_price = product["variants"][0]['price']
                        for list_price in product["variants"]:
                            if list_price['price'] <= min_price:
                                min_price = list_price['price']
                        val['list_price'] = min_price
                    val['description'] = re.sub(r'<.*?>', '', product['body_html'])
                    val['check_product_haravan'] = True
                    if product['images']:
                        for image in product['images']:
                            if 'id' in image:
                                val['haravan_image_url'] = product["images"][0]["src"]
                                # error don't read url image
                                # reason: url private
                                # val['image_1920'] = base64.b64encode(urlopen(product["images"][0]["src"]).read())
                    val['attribute_line_ids'] = self.prepare_attribute_vals(product)
                    existed_product = self.env["product.template"].search([('haravan_product_id', '=', product['id'])],
                                                                          limit=1)
                    if not existed_product:
                        self.env["product.template"].sudo().create(val)
                    else:
                        existed_product.write(val)
        except Exception as e:
            print(e)

    ### VARIENTS_PRODUCT
    def prepare_attribute_vals(self, result):
        product_attribute_obj = self.env['product.attribute']
        product_attribute_value_obj = self.env['product.attribute.value']
        attrib_line_vals = []
        if 'options' in result:
            for attrib in result.get('options'):
                attrib_name = attrib.get('name')
                attr_val_ids = []
                attribute = product_attribute_obj.search([('name', '=ilike', attrib_name)], limit=1)
                if not attribute:
                    attribute = product_attribute_obj.create({'name': attrib_name})
                attrib_index = attrib.get('position')
                attrib_values = []
                if 'variants' in result and result['variants']:
                    index = 'option' + str(attrib_index)
                    for var in result['variants']:
                        if index in var:
                            attrib_values.append(var[index])
                if attrib_values:
                    for attrib_vals in attrib_values:
                        attrib_value = attribute.value_ids.filtered(lambda x: x.name == attrib_vals)
                        if attrib_value:
                            attr_val_ids.append(attrib_value[0].id)
                        else:
                            attrib_value = product_attribute_value_obj.with_context(active_id=False).create(
                                {'attribute_id': attribute.id, 'name': attrib_vals})
                            attr_val_ids.append(attrib_value.id)
                    if attr_val_ids:
                        attribute_line_ids_data = [0, 0,
                                                   {'attribute_id': attribute.id, 'value_ids': [[6, 0, attr_val_ids]]}]
                    attrib_line_vals.append(attribute_line_ids_data)
        return attrib_line_vals

    ### chua xu ly variant_product
    def create_products_sales(self):
        try:
            # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
            cate_haravan = self.env['product.category'].sudo().search([('id', '=', self.categ_id.id)], limit=1)
            token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
            url = "https://apis.haravan.com/com/products.json"
            payload = json.dumps({
                "product": {
                    "title": self.name,
                    "body_html": self.description or 'string',
                    "vendor": self.haravan_vendors,
                    "product_type": cate_haravan.name,
                    "tags": self.haravan_tags,
                    "images": [
                        {
                            "src": self.haravan_image_url
                        }
                    ],
                    "variants": [
                        # {
                        #     "option1": "Blue",
                        #     "option2": "155",
                        #     "price": "100",
                        #     "sku": 123,
                        #     "inventory_policy": "deny",
                        #     "inventory_management": null,
                        #     "requires_shipping": false, "barcode": "ss",
                        #     "compare_at_price": 1500,
                        #     "grams": 550
                        # },
                        # {
                        #     "option1": "Black",
                        #     "option2": "159",
                        #     "price": "200",
                        #     "sku": "123",
                        #     "inventory_policy": "continue",
                        #     "inventory_management": "haravan",
                        #     "requires_shipping": true,
                        #     "barcode": "qqq",
                        #     "compare_at_price": 1500,
                        #     "grams": 200
                        # }
                    ],
                    "options": [
                        # {
                        #     "name": "Color"
                        # },
                        # {
                        #     "name": "Size"
                        # }
                    ]
                }
            })
            headers = {
                # 'Authorization': 'Bearer ' + current_seller.token_connect
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token_connect
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)  # check
            if response.json()['product']:
                print(response.json()['product'])  # check
                existed_product_haravan = self.env['product.template'].search(
                    [('default_code', '=', self.default_code)], limit=1)
                existed_product_haravan.check_product_haravan = True
                existed_product_haravan.haravan_product_id = response.json()['product'][
                    'id']  # chu y ep kieu neu kieu dlu
            else:
                raise ValidationError(_('Create Product Fail in Sync with API Haravan'))
        except Exception as e:
            print(e)

    ### UPDATE
    # field thay đổi cần cập nhật thì truyền vào, field nào không thay đổi thì không cần truyển
    # không cập nhật variant thì cần truyền duy nhất
    # Variants bắt buộc phải truyền đủ số biến thể của sản phẩm đó.
    # Thay đổi giá 1 biến thể trong sản phẩm bằng cách thêm thuộc tính “price”.
    # Thay đổi số lượng tồn kho 1 biến thể trong sản phẩm bằng cách thêm thuộc tính “inventory_quantity”.
    # “inventory_management” = "haravan" mới có thể cập nhật số lượng tồn kho được.
    # Ví dụ: 1 sản phẩm có 2 biến thể, nếu thay đổi giá 1 biến thể thì biến thể còn lại phải bắt buộc truyền “id” để giữ lại (nếu không truyền sẽ bị mất biến thể đó hoặc bị lỗi).
    # Thuộc tính tags là chuỗi chứa nhiều phần tử cách nhau bởi dấu phẩy, khi update thêm tags cần post lại những tags cũ, nếu không post tags cũ sẽ bị mất. Request
    def update_products_haravan_sales(self):
        pass
        # try:
        # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
        # cate_haravan = self.env['product.category'].sudo().search([('id', '=', self.categ_id.id)], limit=1)
        # token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
        # url = "https://apis.haravan.com/com/products/" + self.seller_product_id + ".json"
        # payload = json.dumps({
        #     "product": {
        #         "body_html": self.description or 'string',
        #         "body_plain": None,
        #         # "created_at": None,
        #         # "handle": None,
        #         "id": self.haravan_product_id,
        #         "images": [
        #             {
        #                 "src": self.haravan_image_url
        #             }
        #         ],
        #         "product_type": cate_haravan.name,
        #         # "published_at": None,
        #         # "published_scope": None,
        #         "tags": self.haravan_tags,
        #         # "template_suffix": "product",
        #         "title": self.name,
        #         # "updated_at": None,
        #         "variants": [
        #             {
        #                 "barcode": self.,
        #                 "compare_at_price": 1500,
        #                 "created_at": None,
        #                 "fulfillment_service": None,
        #                 "grams": 550,
        #                 "id": 1040046883,
        #                 "inventory_management": "haravan",
        #                 "inventory_policy": "deny",
        #                 "inventory_quantity": 0,
        #                 "old_inventory_quantity": 0,
        #                 "inventory_quantity_adjustment": None,
        #                 "position": 1,
        #                 "price": 100,
        #                 "product_id": self.haravan_product_id,
        #                 "requires_shipping": False,
        #                 "sku": "sku123",
        #                 "taxable": False,
        #                 "title": "Blue / 155",
        #                 "updated_at": None,
        #                 "image_id": None,
        #                 "option1": "Hồng",
        #                 "option2": "M",
        #                 "option3": "Default Title",
        #                 "inventory_advance": None
        #             },
        #             # {
        #             #     "barcode": "qqq",
        #             #     "compare_at_price": 1500,
        #             #     "created_at": "2019-05-31T09:12:00.55Z",
        #             #     "fulfillment_service": null,
        #             #     "grams": 200,
        #             #     "id": 1040046884,
        #             #     "inventory_management": "haravan",
        #             #     "inventory_policy": "continue",
        #             #     "inventory_quantity": 0,
        #             #     "old_inventory_quantity": 0,
        #             #     "inventory_quantity_adjustment": null,
        #             #     "position": 2,
        #             #     "price": 200,
        #             #     "product_id": 1020104002,
        #             #     "requires_shipping": true,
        #             #     "sku": "123",
        #             #     "taxable": false,
        #             #     "title": "Black / 159",
        #             #     "updated_at": "2019-05-31T09:12:00.55Z",
        #             #     "image_id": null,
        #             #     "option1": "Black",
        #             #     "option2": "159",
        #             #     "option3": null,
        #             #     "inventory_advance": null
        #             # }
        #         ],
        #         "vendor": self.vendor,
        #         "options": [
        #             {
        #                 "name": "Color",
        #                 "id": 2448194925,
        #                 "position": 1,
        #                 "product_id": self.haravan_product_id
        #             },
        #             {
        #                 "name": "Size",
        #                 "id": 2448194926,
        #                 "position": 2,
        #                 "product_id": self.haravan_product_id
        #             },
        #             {
        #                 "name": "Title",
        #                 "id": 2448194927,
        #                 "position": 3,
        #                 "product_id": self.haravan_product_id
        #             }
        #         ],
        #         "only_hide_from_list": False,
        #         "not_allow_promotion": False
        #     }
        # })
        # headers = {
        #     # 'Authorization': 'Bearer ' + current_seller.token_connect
        #     'Content-Type': 'application/json',
        #     'Authorization': 'Bearer ' + token_connect
        # }
        # response = requests.request("PUT", url, headers=headers, data=payload)
        # print(response.text)  # check
        # if response.json()['product']:
        #     print(response.json()['product'])
        # else:
        #     raise UserError(_(response.json()["errors"]))
        # except Exception as e:
        #     raise UserError(str(e))

    ### API DELETE 1 PRODUCT FOLLOW ID
    def delete_products_haravan_sales(self):
        # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
        token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
        url = "https://apis.haravan.com/com/products/" + self.haravan_product_id + ".json"
        payload = json.dumps({
            "product": {
                "id": self.haravan_product_id
            }
        })
        headers = {
            # 'Authorization': 'Bearer ' + current_seller.token_connect
            'Authorization': 'Bearer ' + token_connect
        }
        response = requests.request("DELETE", url, headers=headers, data=payload)
        print(response.text)  # CHECK
        if response.json()['errors']:
            raise UserError(_(response.json()["errors"]))
