var jqueryNoConflict = jQuery;

// begin main function
jqueryNoConflict(document).ready(function() {
    retriveData();
});

// grab data
function retriveData() {
    var dataSource = 'static-files/data/flat_data.json';
    jqueryNoConflict.getJSON(dataSource, renderHandlebarsDataTemplate);
};

// render handlebars template
function renderHandlebarsDataTemplate(data){
    handlebarsDebugHelper();
    renderHandlebarsTemplate('static-files/templates/content-display.handlebars', '#content-display', data);
};

// when user submit button is clicked
function userSubmit(){
    jqueryNoConflict('#content-article-text').hide();
    jqueryNoConflict('#content-article-buttons').hide();
    jqueryNoConflict('#content-display').empty();
    jqueryNoConflict('#content-user-submit').show();
    renderHandlebarsTemplate('static-files/templates/content-user-submit.handlebars', '#content-user-submit');
};
// end

// return to main view
function mapIntro(){
    jqueryNoConflict('#content-article-text').show();
    jqueryNoConflict('#content-article-buttons').show();
    jqueryNoConflict('#content-display').empty();
    jqueryNoConflict('#content-user-submit').hide();
};
// end

// embed function
function embedBox() {
    var embed_url = 'http://projects.scpr.org/static/maps/election-day-voting-issues/iframe.html';
    jAlert('<h4>Embed this on your site or blog</h4>' +
    '<span>Copy the code below and paste to source of your page: <br /><br /> &lt;iframe src=\"'+ embed_url +'\" width=\"620px\" height=\"820px\" style=\"margin: 0 auto;\" scrolling=\"no\" frameborder=\"no\"&gt;&lt;/iframe>', 'Share or Embed');
};
// end