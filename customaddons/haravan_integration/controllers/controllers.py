# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Controller, request
from odoo.exceptions import ValidationError
import datetime
import pytz
import dateutil.parser


class HaravanIntegration(http.Controller):
    @http.route('/webhooks', auth='public', type='http', methods=['GET'], csrf=False)
    def index(self, **kw):
        return "Hello, world"

# class GitLabWebhook(Controller):
#     @http.route('/gitlab/webhook/commit', auth='public', methods=['GET'], type='json', website=False)
#     def verify_webhook(self, **kw):
#         try:
#             print('GET : ', kw)
#         except Exception as e:
#             raise ValidationError(e)
#
#     @http.route('/gitlab/webhook/commit', auth="public", methods=['POST'], type='json', website=False)
#     def webhook_call(self, **kw):
#         try:
#             data = request.jsonrequest
#             if data.get('object_kind'):

#     @http.route('/haravan_integration/haravan_integration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('haravan_integration.listing', {
#             'root': '/haravan_integration/haravan_integration',
#             'objects': http.request.env['haravan_integration.haravan_integration'].search([]),
#         })

#     @http.route('/haravan_integration/haravan_integration/objects/<model("haravan_integration.haravan_integration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('haravan_integration.object', {
#             'object': obj
#         })
