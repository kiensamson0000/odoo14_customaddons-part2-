# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
from odoo.exceptions import UserError, ValidationError


class UpdateProductQuantity(models.Model):
    _name = 'update.product.quantity'
    _description = 'Update Product Quantity'

    name = fields.Char()

    product_name = fields.Many2one('product.template', string="Product Name")
    update_date = fields.Datetime(string="Update Date")
    quantity = fields.Integer("Quantity")
    note = fields.Text("Note")
    update_check = fields.Boolean("")
    fields.Boolean(string="Cho phép load lên testcase sheet?", default=False)
