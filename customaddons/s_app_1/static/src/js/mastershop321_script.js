const base_url = 'https://odoo.website'

function initJQueryWsap(e) {
    var t;
    "undefined" == typeof jQuery ? ((t = document.createElement("SCRIPT")).src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js", t.type = "text/javascript", t.onload = e, document.head.appendChild(t)) : e()
}

initJQueryWsap(function () {
    if (window.AllFetchURLWsap == undefined) {
        window.AllFetchURLWsap = base_url;
        notifywhatsappthankyoupage();
    } else {
        console.log("Error Window.AllFetchURLWsap");
    }
});

window.notifywhatsappthankyoupage = function () {
    console.log("--------hello")

    // price = document.querySelector('.order-discount')
    // console.log(price.innerHTML)

    item = document.querySelectorAll('.list-view-item__title')
    for (var i=0; i<item.length; i++){
        item[i].style.height = "40px";
    }

    var shop = Shopify.shop
    function ProductBought(product) {
        var product_id = product['id']
        var vendor = product['vendor']

        $.ajax({
            type: 'POST',
            url: 'https://odoo.website/shopify_data/fetch_product/' + product_id + '/' + vendor + '/' + shop,
            dataType: 'json',
            data: JSON.stringify({jsonrpc: '2.0'}),
            contentType: 'application/json',
            error: function (request, error) {
                console.log('error')
            },
            complete(data) {
                productDetail = JSON.parse(data['responseText'])['result']
                console.log(productDetail)
                // console.log(productDetail['product_name'])
            }
        })
    }

    if (document.baseURI.startsWith('https://mastershop321.myshopify.com/products')){
        product_item = ShopifyAnalytics.meta.product
        ProductBought(product_item)
    }

    // subtotal = document.querySelector('.cart-subtotal_price')
    // console.log(subtotal.innerHTML)


    function VariantBought(variant) {
        var variant_id = variant

        $.ajax({
            type: 'POST',
            url: 'https://odoo.website/shopify_data/fetch_variant/' + variant + '/' + shop,
            dataType: 'json',
            data: JSON.stringify({jsonrpc: '2.0'}),
            contentType: 'application/json',
            error: function (request, error) {
                console.log('error')
            },
            complete(data) {
                productDetail = JSON.parse(data['responseText'])['result']
                // console.log(productDetail['discount'])

                subtotal = document.querySelector('.cart-subtotal_price')
                sub = subtotal.innerHTML.match(/(\d+.)*/g)
                console.log(parseFloat(sub[0]) )


                document.getElementById('cart-total_price').innerHTML = productDetail['total'].toString() + ' VND'
            }
        })
    }
    // document.getElementsByClassName('cart__qty-input').onchange = MakeDiscount
    if (document.baseURI.startsWith('https://mastershop321.myshopify.com/cart')) {
        variant_list = ''
        variant_items = document.getElementsByClassName('cart__row')
        for (var i = 1; i < variant_items.length; i++) {
            var variant = variant_items[i].getAttribute('data-cart-item-url').match(/(\d+)/g)
            quantity = variant_items[i].getAttribute('data-cart-item-quantity')
            quantity_num = parseFloat(quantity)

            variant_list += variant[0].toString() + ','
        }
        console.log(variant_list)
        VariantBought(variant_list)
    }
}

