import base64
import os


class DefaultConfig(object):
    PROJECT = "shopify app"
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    DEBUG = True
    TESTING = False

    # shopify
    SECRET_KEY = 'e024ff914e34fe9feec5fd48761d4492'
    SERVER_NAME = "localhost:8069"
    PREFERRED_URL_SCHEME = "https"
    BASE_URL = "https://odoo.website"
    SHOPIFY_API_KEY = 'e024ff914e34fe9feec5fd48761d4492'
    SHOPIFY_SHARED_SECRET = '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'
    API_VERSION = "2020-01"
    CID = 1
    MENU_ID = 169

    END_POINT = 'https://dfe64574e832.ngrok.io'