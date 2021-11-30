# -*- coding: utf-8 -*-
from datetime import datetime

import pytz
import requests
import shopify

from customaddons.shopify_app.controllers.config import DefaultConfig
from odoo import models, fields, api


class SocialPostInherit(models.Model):
    _inherit = 'social.post'

    def get_blog(self):
        current_app = DefaultConfig()
        shops = self.env['shopify_app.shop'].sudo().search([('id', '>', 0)])
        for shop in shops:
            # get the offline access code
            domain = shop['url']
            app = self.env['shopify.module.name'].sudo().search(
                ['&', ('shopify_shop_id', '=', shop.id), ('app_name', '=', 'blog post')])
            token = app.code

            session = shopify.Session(domain, '2020-01', token)
            shopify.ShopifyResource.activate_session(session)
        url = 'https://magenestdev.myshopify.com/admin/api/2020-07/blogs.json'
        headers = {
            'Content-Type': 'application/json',
            'client_id': current_app.SHOPIFY_API_KEY,
            'client_secret': current_app.SHOPIFY_SHARED_SECRET,
            'X-Shopify-Access-Token': token
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        list_blogs = []
        for i in range(0, len(data['blogs'])):
            list_blogs.extend([(str(data['blogs'][i]['id']), data['blogs'][i]['title'])])
        return list_blogs

    title = fields.Char(string='Title')
    # blog_id = fields.Many2one('blog.category', string='Blog')
    blog_id = fields.Selection(selection=get_blog, string='Blog', store=True)
    tag_ids = fields.Many2many('blog.tags', string='Tags')

    def get_tag_name(self):
        tags = self.tag_ids
        list_tag = []
        for tag in tags:
            tag_name = tag.name
            list_tag.append(tag_name)
        return list_tag

    def get_image(self):
        tags = self.image_ids
        list_image = []
        for tag in tags:
            tag_name = tag.name
            list_image.append(tag_name)
        return list_image[0].replace(' ', '_')

    def action_post(self):
        rec = super(SocialPostInherit, self).action_post()
        shops = self.env['shopify_app.shop'].sudo().search([('id', '>', 0)])
        for shop in shops:
            # get the offline access code
            domain = shop['url']
            app = self.env['shopify.module.name'].sudo().search(
                ['&', ('shopify_shop_id', '=', shop.id), ('app_name', '=', 'blog post')])
            token = app.code

            session = shopify.Session(domain, '2020-01', token)
            shopify.ShopifyResource.activate_session(session)
            article = shopify.Article({
                "author": self.env.user.name,
                "blog_id": int(self.blog_id),
                "body_html": str(self.message),
                "created_at": str(self.create_date),
                "published_at": str(datetime.now()),
                # "summary_html": self.get_image(),
                "title": str(self.title),
                # "updated_at": "2012-07-06T13:57:51-04:00",
                "user_id": '',
                "tags": self.get_tag_name(),
                # "image": {
                #     "created_at": str(self.create_date),
                #     "alt": str(self.get_image()),
                #     "src": 'https://cdn.shopify.com/s/files/1/0456/3356/8929/articles/'+str(self.get_image())
                # }
            })
            article.save()
        return rec


class BlogCategory(models.Model):
    _name = 'blog.category'

    name = fields.Char(string='Name')

    @api.model
    def create(self, vals):
        rec = super(BlogCategory, self).create(vals)
        shops = self.env['shopify_app.shop'].sudo().search([('id', '>', 0)])
        for shop in shops:
            domain = shop['url']
            app = self.env['shopify.module.name'].sudo().search(
                ['&', ('shopify_shop_id', '=', shop.id), ('app_name', '=', 'blog post')])
            token = app.code

            session = shopify.Session(domain, '2020-01', token)
            shopify.ShopifyResource.activate_session(session)
            shopify.Blog.create({
                'title': str(rec.name)
            })
        return rec


class BlogTags(models.Model):
    _name = 'blog.tags'

    name = fields.Char(string='Name')
