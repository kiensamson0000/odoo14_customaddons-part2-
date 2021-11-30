import requests
import json

from datetime import datetime

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    _description = "Inherit sale.order"

    haravan_order_id = fields.Char('ID')
    haravan_gateway = fields.Char('Payment methods')
    haravan_fulfillment_status = fields.Selection([
        ('notfulfilled', 'Chưa hoàn thành'),
        ('partial', 'Hoàn thành một phần'),
        ('fulfilled', 'Đã hoàn thành'),
        ('approved', 'Đã xác nhận'),
        ('voided','Đã hủy')
    ], string='Fulfillment status')  # trạng thái tạo vận đơn
    haravan_financial_status = fields.Selection([
        ('pending', 'Chưa thanh toán'),
        ('partially_paid', 'Đã thanh toán một phần'),
        ('paid', 'Đã thanh toán'),
        ('partiallyrefunded', 'Đã thanh toán một phần'),
        ('refunded', 'Đã hoàn tiền'),
        ('voided', 'Đã huỷ')
    ], string='Financial status', store=True)  # trạng thái thanh toán
    haravan_source_name = fields.Char('Sales Channel')

    ### khi ko bấm nút giao hàng thì orders['fulfillments'] = [] rỗng
    ### không lấy status giao hàng chi tiết
    # haravan_carrier_status_code = fields.Selection([
    #     ('readytopick', 'chờ lấy hàng'),
    #     ('picking', 'đang đi lấy'),
    #     ('delivering', 'đang giao hàng'),
    #     ('delivered', 'đã giao hàng'),
    #     ('cancel', 'hủy giao hàng'),
    #     ('return', 'chuyển hoàn'),
    #     ('pending', 'chờ xử lý'),
    #     ('notmeetcustomer', 'không gặp khách'),
    #     ('waitingforreturn', 'chờ chuyển hoàn')
    # ], string='Carrier Status')  # trạng thái giao hàng
    # haravan_carrier_cod_status_code = fields.Selection([
    #     ('none', 'Không'),
    #     ('codpending', 'Chưa nhận'),
    #     ('codpaid', ' Chưa nhận'),
    #     ('codreceipt', ' Đã nhận')
    # ], string='Carrier Cod Status')  # trạng thái thu tiền COD
    # tracking_company = fields.Char('Shipping unit')        #ten nha van chuyen
    # total_discounts (number) Tổng giá trị khuyến mãi của đơn hàng
    # partner_invoice_id = fields.Char('Invoice Address')

    def action_return_information_sendo_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Company',
            'view_mode': 'form',
            'res_model': 'update.order.state',
            'target': 'new',
            'context': {
                'default_haravan_order_id': self.id,
            }
        }

    def get_orders_haravan_sale(self):
        # try:
        # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
        token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
        url = "https://apis.haravan.com/com/orders.json"
        payload = {}
        headers = {
            # 'Authorization': 'Bearer ' + current_seller.token_connect
            'Authorization': 'Bearer ' + token_connect
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        result_order = response.json()
        # list_orders = [result_order['orders'][5]]
        list_orders = result_order["orders"]
        val = {}
        val_customer = {}
        for order in list_orders:
            try:
                if 'id' in order:
                    ## get infor customer
                    # val_customer['parent_id'] = order['billing_address']['id']
                    val_customer['name'] = order['billing_address']['name']
                    val_customer['haravan_customer_id'] = order['billing_address']['id']
                    val_customer['street'] = order['billing_address']['address1']
                    val_customer['email'] = order['email']
                    val_customer['phone'] = order['billing_address']['phone']
                    val_customer['mobile'] = order['billing_address']['phone']
                    val_customer['type'] = 'contact'
                    val_customer['check_partner_haravan'] = True
                    # val_customer['comment'] = 'Sync By Call Sendo API'
                    # val_customer['company_type'] = 'person'
                    # val_customer['tags'] = order['tags']
                    existsed_customer = self.env['res.partner'].sudo().search(
                        ['&', ('phone', '=', order['billing_address']['phone']),
                         ('street', '=', order['billing_address']['address1'])], limit=1)
                    if not existsed_customer:
                        self.env['res.partner'].sudo().create(val_customer)
                        ## get infor order
                        val['haravan_order_id'] = order['id']
                        val['name'] = order['id']
                        val['haravan_source_name'] = order['source_name']
                        # if order['fulfillment_status'] == None:
                        #     val['haravan_fulfillment_status'] = 'Không giao hàng'
                        # else:
                        #     val['haravan_fulfillment_status'] = order['fulfillment_status']
                        val['haravan_fulfillment_status'] = order['fulfillment_status']
                        val['haravan_gateway'] = order['gateway']
                        val['haravan_financial_status'] = order['financial_status']
                        val['amount_total'] = order['subtotal_price']
                        val['date_order'] = datetime.fromtimestamp(order['created_at'])
                        val['amount_total'] = order['subtotal_price']
                        val['partner_id'] = existsed_customer.id
                        # val['amount_untaxed'] = order['sub_total']
                        existed_order = self.env['sale.order'].sudo().search([('haravan_order_id', '=', order['id'])],
                                                                             limit=1)
                        if not existed_order:
                            new_record = self.env['sale.order'].create(val)
                            if new_record:
                                if 'line_items' in order:
                                    val_product = order['line_items']
                                    list_product = []
                                    for product in val_product:
                                        try:
                                            if 'id' in product:
                                                existed_product_haravan = self.env['product.template'].sudo().search(
                                                    [('default_code', '=', product['product_id'])], limit=1)
                                                if existed_product_haravan:
                                                    list_product.append({
                                                        'product_id': existed_product_haravan.product_variant_id.id,
                                                        'product_uom_qty': product['quantity'],
                                                        'price_unit': product['price']
                                                    })
                                        except Exception as e:
                                            print(e)
                                    if len(list_product) > 0:
                                        new_record.order_line = [(0, 0, e) for e in list_product]
                        else:
                            existed_order.sudo().write(val)
                    else:
                        # existsed_customer.sudo().write(val_customer)
                        ## get infor order
                        val['haravan_order_id'] = order['id']
                        val['name'] = order['id']
                        val['haravan_source_name'] = order['source_name']
                        val['haravan_fulfillment_status'] = order['fulfillment_status']
                        val['haravan_gateway'] = order['gateway']
                        val['haravan_financial_status'] = order['financial_status']
                        val['amount_total'] = order['subtotal_price']
                        # val['date_order'] = datetime.datetime.strptime(order['created_at'], '%m/%d/%Y %H:%M:%S.%f')
                        date = str(order['created_at']).replace("T", " ").replace("Z", '')
                        val['date_order'] = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                        val['amount_total'] = order['subtotal_price']
                        val['partner_id'] = existsed_customer.id
                        # val['amount_untaxed'] = order['sub_total']
                        # In sale.order khong co field order_id => create new field haravan_order_id
                        existed_order = self.env['sale.order'].sudo().search([('haravan_order_id', '=', order['id'])],
                                                                             limit=1)
                        if not existed_order:
                            new_record = self.env['sale.order'].create(val)
                            if new_record:
                                if 'line_items' in order:
                                    val_product = order['line_items']
                                    list_product = []
                                    for product in val_product:
                                        try:
                                            if 'id' in product:
                                                existed_product_haravan = self.env['product.template'].sudo().search(
                                                    [('default_code', '=', product['product_id'])], limit=1)
                                                if existed_product_haravan:
                                                    list_product.append({
                                                        'product_id': existed_product_haravan.product_variant_id.id,
                                                        'product_uom_qty': product['quantity'],
                                                        'price_unit': product['price']
                                                    })
                                        except Exception as e:
                                            print(e)
                                    if len(list_product) > 0:
                                        new_record.order_line = [(0, 0, e) for e in list_product]
                        else:
                            existed_order.sudo().write(val)
            except Exception as e:
                print(e)

    # def create_order_haravan_sale(self):
    #     # try:
    #     # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
    #     existsed_customer = self.env['res.partner'].sudo().search(
    #         ['&', ('phone', '=', order['billing_address']['phone']),
    #          ('street', '=', order['billing_address']['address1'])], limit=1)
    #     token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
    #     url = "https://apis.haravan.com/com/orders.json"
    #     payload = json.dumps({
    #         "order": {
    #             "billing_address": {
    #                 "address1": "Số 111, KIm Mã, Ba Đình, Hà Nội",
    #                 "address2": None,
    #                 "city": None,
    #                 "company": None,
    #                 "country": "Vietnam",
    #                 "first_name": "Hiếu",
    #                 "id": self.,
    #                 "last_name": "Dương Trung",
    #                 "phone": "0967543622",
    #                 "province": "Hà Nội",
    #                 "zip": None,
    #                 "name": "Dương Trung Hiếu",
    #                 "province_code": "HI",
    #                 "country_code": "VN",
    #                 "default": true,
    #                 "district": "Quận Ba Đình",
    #                 "district_code": "HI2",
    #                 "ward": "Phường Kim Mã",
    #                 "ward_code": "00028"
    #             },
    #             "shipping_address": {
    #                 "address1": "Số 111, KIm Mã, Ba Đình, Hà Nội",
    #                 "address2": None,
    #                 "city": None,
    #                 "company": None,
    #                 "country": "Vietnam",
    #                 "first_name": "Hiếu",
    #                 "last_name": "Dương Trung",
    #                 "latitude": 0.00000000,
    #                 "longitude": 0.00000000,
    #                 "phone": "0967543622",
    #                 "province": "Hà Nội",
    #                 "zip": None,
    #                 "name": "Dương Trung Hiếu",
    #                 "province_code": "HI",
    #                 "country_code": "VN",
    #                 "district_code": "HI2",
    #                 "district": "Quận Ba Đình",
    #                 "ward_code": "00028",
    #                 "ward": "Phường Kim Mã"
    #             },
    #             "email": "duonghieu9@gmail.com",
    #             "fulfillment_status": "fulfilled",
    #             "line_items": [
    #                 {
    #                     "quantity": 1,
    #                     "requires_shipping": true,
    #                     "title": "Áo len cổ tròn kiểu Cổ điển",
    #                     "variant_id": 1075094458,
    #                     "variant_title": "Trắng / L",
    #                     "vendor": "Khác",
    #                     "properties": null,
    #                     "product_exists": false
    #                 },
    #                 {
    #                     "quantity": 1,
    #                     "requires_shipping": true,
    #                     "title": "Áo len cổ tròn kiểu Cổ điển",
    #                     "variant_id": 1075094459,
    #                     "variant_title": "Trắng / XL",
    #                     "vendor": "Khác",
    #                     "properties": null,
    #                     "product_exists": false
    #                 }
    #             ]}
    #     })
    #     headers = {
    #         # 'Authorization': 'Bearer ' + current_seller.token_connect
    #         'Content-Type': 'application/json',
    #         'Authorization': 'Bearer ' + token_connect
    #     }
    #     response = requests.request("POST", url, headers=headers, data=payload)
    #     print(response.text)  # check