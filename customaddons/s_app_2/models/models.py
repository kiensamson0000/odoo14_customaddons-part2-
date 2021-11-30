# -*- coding: utf-8 -*-
import shopify

from odoo import models, fields


class ShopifyApp(models.Model):
    _name = 'shopify.config.user'
    _description = 'Shopify Config User'

    name = fields.Char(string="Name")
    link = fields.Char(string='Facebook Link')
    phone = fields.Char(string='Phone Number')
    user_id = fields.Char(string="User ID")
    shop_id = fields.Char(string="Shop's ID")

    # def test_blog_creation(self):
    #     shops = self.env['shopify_app.shop'].sudo().search([('id', '>', 0)])
    #     for shop in shops:
    #         # get the offline access code
    #         domain = shop['url']
    #         app = self.env['shopify.module.name'].sudo().search(
    #             ['&', ('shopify_shop_id', '=', shop.id), ('app_name', '=', 'blog post')])
    #         token = app.code
    #
    #         session = shopify.Session(domain, '2020-01', token)
    #         shopify.ShopifyResource.activate_session(session)
    #         # shopify.Blog.create({'title': "Test Blog"})
    #         article = shopify.Article({
    #             "author": self.env.user.name,
    #             "blog_id": 69125505185,
    #             "body_html": 'day la noi dung cua post duoc tao bang viec call api',
    #             "created_at": "2012-07-06T13:57:28-04:00",
    #             "published_at": "2012-07-06T13:57:28-04:00",
    #             "summary_html": '',
    #             "title": "First Post",
    #             "updated_at": "2012-07-06T13:57:51-04:00",
    #             "user_id": '',
    #             "tags": "consequuntur, cupiditate, repellendus"
    #         })
    #         article.save()
