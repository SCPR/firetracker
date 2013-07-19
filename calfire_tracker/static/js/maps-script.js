    function initialize() {


        var initialZoom = 12;

        // set zoom for mobile devices
        if (navigator.userAgent.match(/(iPad)|(iPhone)|(iPod)|(android)|(webOS)/i)) {
            initialZoom = 7;
        }

        map = new google.maps.Map(document.getElementById('map_canvas'), {
            center: new google.maps.LatLng(33.734048,-116.621643),
            zoom: 12,
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

        var fireLayer = new google.maps.KmlLayer({
            url: 'http://rmgsc.cr.usgs.gov/outgoing/geomac/ActiveFirePerimeters.kml',
            preserveViewport: true
        });

        fireLayer.setMap(map);

        google.maps.event.addDomListener(map, 'idle', function() {
          calculateCenter();
        });

        google.maps.event.addDomListener(window, 'resize', function() {
          map.setCenter(center);
        });

    }

    // function to maintain center point of map
    function calculateCenter(){
        center = map.getCenter();
    };

    google.maps.event.addDomListener(window, 'load', initialize);