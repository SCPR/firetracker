function initialize() {
    var california = new google.maps.LatLng(34.01862413631862, -118.4208233779297);
    var mapOptions = {
        zoom: 11,
        center: california,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }

    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    var ctaLayer = new google.maps.KmlLayer({
        url: 'http://rmgsc.cr.usgs.gov/outgoing/geomac/ActiveFirePerimeters.kml'
    });

    ctaLayer.setMap(map);
}

google.maps.event.addDomListener(window, 'load', initialize);