from odoo import api, fields, models, _, tools


class ShopifyDiscountProgram(models.Model):
    _name = "shopify.discount.program"
    _description = "Discount Program"

    name = fields.Char(string='Name')
    shop_id = fields.Many2one('shopify.shop', string='Shop ID')

    cus_ids = fields.One2many('shopify.discount.program.customer', 'discount_id', string='Discount Customer ID')
    pro_ids = fields.One2many('shopify.discount.program.product', 'discount_id', string='Discount Product ID')

    @api.depends('shop_id')
    def get_customer(self):
        for rec in self:
            if rec.shop_id:
                rec.cus_ids = rec.env['res.partner'].search(
                    [('shop_id', '=', rec.shop_id.id), ('company_type', '=', 'person')], limit=50)
            else:
                rec.cus_ids = rec.env['res.partner'].search([(0, '=', 1)])

    @api.onchange(shop_id)
    def get_product(self):
        for rec in self:
            if rec.shop_id:
                rec.pro_ids = rec.env['product.product'].search([('shop_id', '=', rec.shop_id.id)], limit=50)
            else:
                rec.pro_ids = rec.env['product.product'].search([(0, '=', 1)])

    def open_product(self):
        pro_list = self.env['product.product'].search([('shop_id', '=', self.shop_id.id)], limit=50)
        product_list = self.env['shopify.discount.program.product'].search([])
        pro_id_list = []
        for pro in product_list:
            if pro.discount_id.id == self.id:
                pro_id_list.append(pro.product_id.id)

        for pro in pro_list:
            if pro.id not in pro_id_list:
                pro_vals = {
                    'discount_id': self.id,
                    'product_id': pro.id
                }
                self.env['shopify.discount.program.product'].create(pro_vals)

    def open_customer(self):
        cus_list = self.env['res.partner'].search(
            [('shop_id', '=', self.shop_id.id), ('company_type', '=', 'person')], limit=50)

        customer_list = self.env['shopify.discount.program.customer'].search([])
        cus_id_list = []
        for cus in customer_list:
            if cus.discount_id.id == self.id:
                cus_id_list.append(cus.customer_id.id)
        for cus in cus_list:
            if cus.id not in cus_id_list:
                cus_vals = {
                    'discount_id': self.id,
                    'customer_id': cus.id,
                }
                self.env['shopify.discount.program.customer'].create(cus_vals)


class ShopifyDiscountProgramProduct(models.Model):
    _name = "shopify.discount.program.product"

    discount_id = fields.Many2one('shopify.discount.program', string='Discount ID')
    product_id = fields.Many2one('product.product', string='Product ID')
    name = fields.Char(related='product_id.name')
    price = fields.Float(related='product_id.lst_price')
    discount_amount = fields.Float(string='Discount Amount')


class ShopifyDiscountProgramCustomer(models.Model):
    _name = "shopify.discount.program.customer"

    discount_id = fields.Many2one('shopify.discount.program', string='Discount ID')
    customer_id = fields.Many2one('res.partner', string='Customer ID')
    email = fields.Char(related='customer_id.email')
    check_person = fields.Boolean(string='Choose Person')
