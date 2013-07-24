var jqueryNoConflict = jQuery;
var kpccApiArticleDisplay = kpccApiArticleDisplay || {};

// begin main function
jqueryNoConflict(document).ready(function(){
    kpccApiArticleDisplay.constructQueryUrl();

    function appendTweets(element, content){
        jqueryNoConflict(element).append(content);
    }
});

// begin kpccApiArticleDisplay
var kpccApiArticleDisplay = {

    // construct the url to query for data
    constructQueryUrl: function(){
        var urlPrefix = 'http://www.scpr.org/api/v2/content/?';
        var urlTypes = 'types=' + kpccApiArticleDisplay.replaceQuerySpacesWith(kpccApiArticleConfig.types, '');
        var urlQuery = '&query=' + kpccApiArticleDisplay.replaceQuerySpacesWith(kpccApiArticleConfig.query, '+');
        var urlLimit = '&limit=' + kpccApiArticleConfig.limit;
        var urlPage = '&page=' + kpccApiArticleConfig.page;
        var targetUrl = urlPrefix + urlTypes + urlQuery + urlLimit + urlPage;
        kpccApiArticleDisplay.retrieveApiData(targetUrl);
    },

    retrieveApiData: function(targetUrl){
        jqueryNoConflict.getJSON(targetUrl, kpccApiArticleDisplay.createArrayFrom);
    },

    replaceQuerySpacesWith: function(string, character){
        var output = string.replace(/\s/g, character);
        return output;
    },

    takeTime: function (dateInput){
        var dateFormat = 'MMMM D, h:mm a';
        var dateOutput = moment(dateInput).format(dateFormat);
        return dateOutput;
    },

    noArticlesFound: function (elementToAppendTo){
        jqueryNoConflict(elementToAppendTo).append(
            '<p class="no-article-present">No related articles found for the ' +
            kpccApiArticleConfig.fire_display_name + ' in ' + kpccApiArticleConfig.fire_county_name + ', California.</p>'
        );
    },

    createArrayFrom: function(data){
        var article_image_asset;

        if (data.length === 0) {
            kpccApiArticleDisplay.noArticlesFound(kpccApiArticleConfig.contentContainer);

        } else {
            var fire_start_date = kpccApiArticleConfig.fire_start_date;

            jqueryNoConflict(kpccApiArticleConfig.contentContainer).append('<ul id="article-list-content"></ul>');

            // begin loop
            for (var i=0; i<data.length; i++) {
                if (data[i].assets.length === 0) {
                    article_image_asset = 'http://projects.scpr.org/firetracker/static/media/archive-fire-photo-fallback.jpg'
                } else {
                    article_image_asset = data[i].assets[0].small.url;
                }
                var short_title = data[i].short_title;
                var permalink = data[i].permalink;
                var thumbnail = data[i].thumbnail;
                var published_at = data[i].published_at;
                var teaser = data[i].teaser;
                var article_start_date = moment(data[i].published_at).format('YYYY-MM-DD')
                var articleIsOld = moment(article_start_date).isBefore(fire_start_date);

                if (articleIsOld === false) {
                    jqueryNoConflict('#article-list-content').append(
                        '<li><a href=\"' + permalink + '\" target="_blank">' +
                            '<b class="img"><img src="' + article_image_asset + '" /></b>' +
                            '<span>' + kpccApiArticleDisplay.takeTime(published_at).toUpperCase() + ' PDT</span>' +
                            '<mark>' + short_title + '</mark></a>' +
                        '</li>'
                    );

                } else {
                    continue;
                }
            }
            // end loop

            // see if any articles have been added, and if not, tell the user none have been found
            if (jqueryNoConflict('#article-list-content li').length == 0) {
                jqueryNoConflict('#article-list-content').remove();
                kpccApiArticleDisplay.noArticlesFound(kpccApiArticleConfig.contentContainer);
            }
        }
    }
}
// end kpccApiArticleDisplay