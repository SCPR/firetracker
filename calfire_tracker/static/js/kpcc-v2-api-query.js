var jqueryNoConflict = jQuery;
var kpccApiDisplay = kpccApiDisplay || {};

// begin main function
jqueryNoConflict(document).ready(function(){
    kpccApiDisplay.constructQueryUrl();
});

// begin kpccApiDisplay
var kpccApiDisplay = {

    // construct the url to query for data
    constructQueryUrl: function(){
        var urlPrefix = 'http://www.scpr.org/api/v2/content/?';
        var urlTypes = 'types=' + kpccApiDisplay.replaceQuerySpacesWith(kpccApiConfig.types, '');
        var urlQuery = '&query=' + kpccApiDisplay.replaceQuerySpacesWith(kpccApiConfig.query, '+');
        var urlLimit = '&limit=' + kpccApiConfig.limit;
        var urlPage = '&page=' + kpccApiConfig.page;
        var targetUrl = urlPrefix + urlTypes + urlQuery + urlLimit + urlPage;
        kpccApiDisplay.retrieveApiData(targetUrl);
    },

    retrieveApiData: function(targetUrl){
        jqueryNoConflict.getJSON(targetUrl, kpccApiDisplay.createArrayFrom);
    },

    replaceQuerySpacesWith: function(string, character){
        var output = string.replace(/\s/g, character);
        return output;
    },

    takeTime: function (dateInput){
        var dateFormat = 'MMM. D, h:mm a';
        var dateOutput = moment(dateInput).format(dateFormat);
        //var dateOutput = moment(dateInput).fromNow();
        return dateOutput;
    },

    createArrayFrom: function(data){

        console.log(data);

        // begin loop
        for (var i = 0; i < data.length; i++) {
            var asset = data[i].assets[0].small.url;
            var short_title = data[i].short_title;
            var permalink = data[i].permalink;
            var thumbnail = data[i].thumbnail;
            var published_at = data[i].published_at;
            var teaser = data[i].teaser;

            // write data to div
            jqueryNoConflict(kpccApiConfig.contentContainer).append(
                '<li><a href=\"' + permalink + '\" target="_blank">' +
                    '<b class="img"><img src="' + asset + '" /></b>' +
                    '<span>' + kpccApiDisplay.takeTime(published_at) + '</span>' +
                    '<mark>' + short_title + '</mark></a>' +
                '</li>');
        }
       // end loop
    }
};
// end kpccApiDisplay