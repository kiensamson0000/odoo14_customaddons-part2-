import requests
import json

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class UpdateOrderState(models.Model):
    _name = "update.order.state"
    _description = "Update Order State"

    haravan_order_id = fields.Many2one('sale.order', string='ID Order Haravan', default=False)
    haravan_fulfillment_status = fields.Selection(related= 'haravan_order_id.haravan_fulfillment_status')
    haravan_cancel_reason = fields.Selection([
        ('customer', 'Khách hàng đổi ý'),
        ('fraud', 'Đơn hàng giả mạo'),
        ('inventory', 'Hết hàng'),
        ('other', 'Khác')
    ], string='Lý do hủy đơn hàng')
    harvan_note_reason = fields.Char('Ghi chú')

    ### Question: trạng thái giao đơn hàng(carrier_status_code) hay trạng thái đơn hàng fulfillment_status(tao van don)
    ###
    ### API cập nhật trạng thái xác nhận đơn hàng
    def update_confirmed_status_haravan_sales(self):
        # print(self)
        try:
            # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
            token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
            url = "https://apis.haravan.com/com/orders/" + self.haravan_order_id.haravan_order_id + "/confirm.json"
            payload = json.dumps({
                "order": {
                    "id": self.haravan_order_id.haravan_order_id
                }
            })
            headers = {
                # 'Authorization': 'Bearer ' + current_seller.token_connect
                'Authorization': 'Bearer ' + token_connect
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)  # CHECK
            # change state
            self.haravan_order_id.haravan_fulfillment_status = 'approved'
            if "errors" in response.json():
                raise UserError(_(response.json()["errors"]))
        except Exception as e:
            raise UserError(str(e))

    ### API cập nhật trạng thái hủy đơn hàng
    def update_cancelled_status_haravan_sales(self):
        # current_seller = self.env['haravan.seller'].sudo().search([])[0]    (chua connect duoc)
        token_connect = '914CE4F424C6DCD6EC3E50792E040C11348E8E27E5C73B5E8A2BB9F3C9690FFB'
        url = "https://apis.haravan.com/com/orders/" + self.haravan_order_id.haravan_order_id + "/cancel.json"
        payload = json.dumps({
            "order": {
                "id": self.haravan_order_id.haravan_order_id,
                "cancel_reason": self.haravan_cancel_reason,
                "refunds": [
                    {
                        "note": self.harvan_note_reason
                    }
                ]
            }
        })
        headers = {
            # 'Authorization': 'Bearer ' + current_seller.token_connect
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token_connect
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)  # CHECK
        # change state
        self.haravan_order_id.haravan_fulfillment_status = 'voided'
        if "errors" in response.json():
            raise UserError(_(response.json()["errors"]))