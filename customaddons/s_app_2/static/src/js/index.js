var url = "https://magenestdev.myshopify.com/admin/api/2020-01/blogs.json";
jQuery.ajax({
    url,
    success: function (result) {
        console.log(result)
    },
    async: false
});