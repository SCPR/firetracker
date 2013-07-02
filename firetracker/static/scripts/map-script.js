var jqueryNoConflict = jQuery;
var map;

// begin main function
jqueryNoConflict(document).ready(function() {
    google.maps.event.addDomListener(window, 'load', createMap);
});

// begin function
function createMap(){

    // add encrypted table id
    var cityCrosswalkTableId = '113boV0mDDfay8ngXn8REwwIplC_uEWogLf6aepw';
    var userContributedTableId = '1RvesiAIGe14Gw3w7zjQm_2NBlZLl5EBSstdvf6E';
    var locationColumn = 'Location';
    var centerLosAngeles = new google.maps.LatLng(34.061841979429445, -118.26370239257812);
    map = new google.maps.Map(document.getElementById('content-map-canvas'), {
        center: centerLosAngeles,
        zoom: 13,
        scrollwheel: false,
        draggable: true,
        mapTypeControl: false,
        navigationControl: true,
        streetViewControl: false,
        panControl: false,
        scaleControl: false,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        navigationControlOptions: {
            style: google.maps.NavigationControlStyle.SMALL,
            position: google.maps.ControlPosition.RIGHT_TOP}
    });

    // Initialize ft layer of new crosswalks
    var cityCrosswalkLayer = new google.maps.FusionTablesLayer({
        query: {
            select: locationColumn,
            from: cityCrosswalkTableId
        },
        map: map,
        suppressInfoWindows: false
    });

    google.maps.event.addDomListener(map, 'idle', function() {
      calculateCenter();
    });

    google.maps.event.addDomListener(window, 'resize', function() {
      map.setCenter(centerLosAngeles);
    });

};

// function to maintain center point of map
function calculateCenter(){
    center = map.getCenter();
};