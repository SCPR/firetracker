var kpcc_api_article_display = kpcc_api_article_display || {};

// begin main function
$(document).ready(function(){
    kpcc_api_article_display.construct_query_url();

    function appendTweets(element, content){
        $(element).append(content);
    }

});

// begin kpcc_api_article_display
var kpcc_api_article_display = {

    // construct the url to query for data
    construct_query_url: function(){
        var param_1;
        var param_2;
        if (kpcc_api_article_config.display === "detail-page") {
            param_1 = kpcc_api_article_config.fire_display_name.toLowerCase();
            param_2 = kpcc_api_article_config.fire_county_name.toLowerCase();
            param_2 = param_2.replace("county", "").replace("and", "");
        } else {
            param_1 = "wildfire"
            param_2 = "burning"
        }
        var query = param_1 + " " + param_2
        var url_prefix = "http://www.scpr.org/api/v3/articles/?";
        var url_types = "types=" + kpcc_api_article_display.replace_spaces_with(kpcc_api_article_config.types, "");
        var url_query = "&query=" + kpcc_api_article_display.replace_spaces_with(query, "+");
        var url_limit = "&limit=" + kpcc_api_article_config.limit;
        var url_page = "&page=" + kpcc_api_article_config.page;
        var target_url = url_prefix + url_types + url_query + url_limit + url_page;
        kpcc_api_article_display.retrieve_api_data(target_url);
    },

    retrieve_api_data: function(target_url){
        $.getJSON(target_url, kpcc_api_article_display.route_api_data);
    },

    route_api_data: function(data){
        if (data.articles.length === 0) {
            kpcc_api_article_display.no_articles_found(kpcc_api_article_config.content_container);
        } else {
            if (kpcc_api_article_config.display === "detail-page") {
                var fire_start_date = kpcc_api_article_config.fire_start_date;
                $(kpcc_api_article_config.content_container).append("<ul id='article-list-content'></ul>");
                kpcc_api_article_display.content_loopity_loop(data, true);
            } else if (kpcc_api_article_config.display === "index-page"){
                $(kpcc_api_article_config.content_container).append("<ul id='article-list-content'></ul>");
                kpcc_api_article_display.content_loopity_loop(data, false);
            } else{
                kpcc_api_article_display.no_articles_found(kpcc_api_article_config.content_container);
            }
        }
    },

    content_loopity_loop: function(data, dateCheck){
        var article_image_asset;
        for (var i = 0; i<data.articles.length; i++) {
            var article = data.articles[i];
            if (article.assets.length) {
                article_image_asset = article.assets[0].small.url;
            } else {
                article_image_asset = "http://firetracker.scpr.org/static/media/archive-fire-photo-fallback.jpg";
            }
            var article_start_date = moment(article.published_at).format('YYYY-MM-DD')
            var article_is_old = moment(article_start_date).isBefore(kpcc_api_article_config.fire_start_date);
            if (dateCheck === false){
                $("#article-list-content").append(
                    "<li><a href='" + article.public_url + "' target='_blank'>" +
                        "<b class='img'><img src='" + article_image_asset + "' /></b>" +
                        "<span>" + kpcc_api_article_display.take_time(article.published_at) + "</span>" +
                        "<mark>" + article.short_title + "</mark></a>" +
                    "</li>"
                );
            } else {
                if (article_is_old === false) {
                    $("#article-list-content").append(
                        "<li><a href='" + article.public_url + "' target='_blank'>" +
                            "<b class='img'><img src='" + article_image_asset + "' /></b>" +
                            "<span>" + kpcc_api_article_display.take_time(article.published_at) + "</span>" +
                            "<mark>" + article.short_title + "</mark></a>" +
                        "</li>"
                    );
                }
            }
        }
    },

    no_articles_found: function(element_to_append_to){
        $(element_to_append_to).append(
            "<p class='no-article-present'>No related articles found for the " +
            kpcc_api_article_config.fire_display_name + " in " + kpcc_api_article_config.fire_county_name + ", California.</p>"
        );
    },

    replace_spaces_with: function(string, character){
        var output = string.replace(/\s/g, character);
        return output;
    },

    take_time: function(date_input){
        //var date_format = "MMMM D, h:mm a";
        var date_format = "MMMM D";
        var dateOutput = moment(date_input).format(date_format);
        return dateOutput;
    }

}
// end kpcc_api_article_display