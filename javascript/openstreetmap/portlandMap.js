var pointFeature;
var vectorLayer;
var featuresToStationIds = []
var features = []
function init() {
  //var features = [];
  map = new OpenLayers.Map("mapdiv");
  //var newLayer = new OpenLayers.Layer.OSM("Local Tiles", "http://tile.openstreetmap.org/${z}/${x}/${y}.png", {numZoomLevels: 19});
  var newLayer = new OpenLayers.Layer.OSM("Local Tiles", "http://bikeshare.cs.pdx.edu/osm/${z}/${x}/${y}.png", {numZoomLevels: 19, crossOriginKeyword: null});
  map.addLayer(newLayer); 
  // allow testing of specific renderers via "?renderer=Canvas", etc
  var renderer = OpenLayers.Util.getParameters(window.location.href).renderer;
  renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers;
  var layer_style = OpenLayers.Util.extend({}, OpenLayers.Feature.Vector.style['default']);
  layer_style.fillOpacity = 0.2;
  layer_style.graphicOpacity = 1;
  var lonlat = new OpenLayers.LonLat(-122.680591,45.510016).transform(
      new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
      new OpenLayers.Projection("EPSG:900913") // to Spherical Mercator
    );
      vectorLayer = new OpenLayers.Layer.Vector("Simple Geometry", {
          styleMap: new OpenLayers.StyleMap({'default':{
              strokeColor: "${pointColor}",
              strokeOpacity: 1,
              strokeWidth: 3,
              fillColor: "${pointColor}",
              fillOpacity: 0.8,
              pointRadius: 5,
              pointerEvents: "visiblePainted",
              label : "${name}",
              fontColor: "${favColor}",
              fontSize: "12px",
              fontFamily: "Courier New, monospace",
              fontWeight: "bold",
              labelAlign: "${align}",
              labelXOffset: "${xOffset}",
              labelYOffset: "${yOffset}"
          }}),
          renderers: renderer
      });
  var zoom = 14;
      $.ajax({url : "http://bikeshare.cs.pdx.edu/bikeshare_dramage/REST/1.0/stations/all",
        success : function(result) {
            bikeStationList = JSON.parse(result); 
            for (var i = 0; i < bikeStationList.length; i ++) {
              var latitude = parseFloat(bikeStationList[i].lat);
              var longitude = parseFloat(bikeStationList[i].lon);
              var point = new OpenLayers.Geometry.Point(longitude, latitude);
              point.transform(
                new OpenLayers.Projection("EPSG:4326"),
                new OpenLayers.Projection("EPSG:900913")
              );
              var pointFeature = new OpenLayers.Feature.Vector(point);
              pointFeature.attributes = {
                  name : "BikeShare Station " + bikeStationList[i].station_id,
                  favColor : 'black',
                  align : 'cm',
                  xOffset : 10,
                  yOffset : 10,
                  pointColor : 'blue',
                  popup : new OpenLayers.Popup("popup" + bikeStationList[i].station_id,
                                                new OpenLayers.LonLat(longitude,latitude),
                                                new OpenLayers.Size(200,200),
                                                "This Is A Popup!",
                                                true)
              };
              features.push(pointFeature);
              map.addPopup(pointFeature.attributes.popup);
              featuresToStationIds[i] = bikeStationList[i].station_id;
              map.addLayer(vectorLayer);
              vectorLayer.addFeatures(features);
              map.setCenter(lonlat, zoom); 
            }
            return;
        }
      });
    
    var report = function(e) {
        console.log("you have moused over this");
    };
     var highlightCtrl = new OpenLayers.Control.SelectFeature(vectorLayer, {
                hover: true,
                //highlightOnly: false,
                //renderIntent: "temporary",
                eventListeners: {
                    //beforefeaturehighlighted: featureOver,
                    featurehighlighted: featureHighlighted,
                    featureunhighlighted: featureUnhighlighted 
        }
     });

    map.addControl(highlightCtrl);
    highlightCtrl.activate();
    map.setCenter(lonlat, zoom);
}

function getBikestationData() {
    for (var i = 0; i < featuresToStationIds.length; i ++) {
       $.ajax({ url : "http://bikeshare.cs.pdx.edu/bikeshare_dramage/REST/1.0/stations/info/" + featuresToStationIds[i],
            success : function(result) {
                stationData = JSON.parse(result);
                setStationColor(this.stationFeatureId,stationData);  
                return;          
            },
            stationFeatureId : i
       });
    }
    vectorLayer.redraw();
}

function setStationColor(stationNum,stationData) {
    bikePercent = (stationData.num_bikes / stationData.num_docks) * 100;
    if (bikePercent >= 70) {
        features[stationNum].attributes.pointColor = 'blue';
    } else if (70 > bikePercent >= 40) {
        features[stationNum].attributes.pointColor = 'yellow';
    } else {
        features[stationNum].attributes.pointColor = 'red';
    }
}
function getRandomInt (min, max) {
  	return Math.floor(Math.random() * (max - min + 1)) + min;
}

function setRandomPointStuff() {
 	colors = ['red','yellow','blue'];
  var numFeatures = features.length;
  for (var i = 0; i< numFeatures; i ++) {
  	colorNum = getRandomInt(0,2);
  	features[i].attributes.pointColor = colors[colorNum];
  }
 vectorLayer.redraw();
}

function featureHighlighted(feature) {
    console.log("Feature hilighted");
    console.log(feature.feature.attributes);
    feature.feature.attributes.popup.show();
}

function featureUnhighlighted(feature) {
    console.log("Feature unhilighted");
    console.log(feature.feature.attributes);
    feature.feature.attributes.popup.hide();
}

setInterval(function(){getBikestationData()},15000);
