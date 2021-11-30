import shopify
'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'
shopify.Session.setup(
    api_key='f322f4ab2502a9ca49dec4642d24b2b7',
    secret='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')
shopify_session = shopify.Session('mastershop321.myshopify.com', '2021-04', token='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')
shopify.ShopifyResource.activate_session(shopify_session)
existedScriptTags = shopify.ScriptTag.create({
    'event': 'onload',
    'src': 'https://odoo.website/shopify_app/static/src/js/mastershop321_script.js'
})

script = shopify.ScriptTag.find()
for scr in script:
    print(scr.src)
