"""
Map widget that integrates Leaflet with PyQt6.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, pyqtSignal
import ee
import os
import shutil
import json
from typing import List, Dict, Any

class MapWidget(QWidget):
    # Signals
    aoi_drawn = pyqtSignal(list)  # Emitted when AOI drawing is complete
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Get paths to template and current map
        self.template_file = os.path.join(os.path.dirname(__file__), "map_template_new.html")
        self.html_file = os.path.join(os.path.dirname(__file__), "current_map.html")
        
        # Copy template to current map
        shutil.copy2(self.template_file, self.html_file)
        
        # Create QWebEngineView and load the map
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl.fromLocalFile(self.html_file))
        
        # Add to layout
        self.layout.addWidget(self.web_view)
        
        # Initialize drawing mode state
        self.drawing_mode = False
        
        # Track current layers
        self.current_layers: Dict[str, Any] = {}
        
    def add_ee_layer(self, ee_object, vis_params: Dict[str, Any], name: str) -> None:
        """Add Earth Engine layers to the map."""
        try:
            # Remove existing layer with same name if it exists
            self.remove_layer(name)
            
            # Get the tile URL from Earth Engine
            map_id = ee.Image(ee_object).getMapId(vis_params)
            tile_url = map_id['tile_fetcher'].url_format
            
            # Create JavaScript to add the layer
            js = f"""
                var layer = L.tileLayer('{tile_url}', {{
                    maxZoom: 19,
                    attribution: 'Google Earth Engine',
                    name: '{name}'
                }});
                map.layerControl.addOverlay(layer, '{name}');
                layer.addTo(map);
                // Store layer reference
                if (!window.mapLayers) window.mapLayers = {{}};
                window.mapLayers['{name}'] = layer;
            """
            
            # Execute the JavaScript
            self.web_view.page().runJavaScript(js)
            
            # Track the layer
            self.current_layers[name] = {
                'url': tile_url,
                'vis_params': vis_params
            }
            
        except Exception as e:
            print(f"Error adding layer: {str(e)}")
            
    def remove_layer(self, name: str) -> None:
        """Remove a layer from the map."""
        if name in self.current_layers:
            js = f"""
                if (window.mapLayers && window.mapLayers['{name}']) {{
                    map.removeLayer(window.mapLayers['{name}']);
                    map.layerControl.removeLayer(window.mapLayers['{name}']);
                    delete window.mapLayers['{name}'];
                }}
            """
            self.web_view.page().runJavaScript(js)
            del self.current_layers[name]
            
    def clear_layers(self) -> None:
        """Remove all layers from the map."""
        for name in list(self.current_layers.keys()):
            self.remove_layer(name)
            
    def start_drawing(self) -> None:
        """Enable drawing mode."""
        if not self.drawing_mode:
            self.drawing_mode = True
            js = """
                // Enable drawing mode
                if (!window.drawControl) {
                    var drawnItems = new L.FeatureGroup();
                    map.addLayer(drawnItems);
                    
                    window.drawControl = new L.Control.Draw({
                        draw: {
                            polygon: {
                                allowIntersection: false,
                                drawError: {
                                    color: '#e1e100',
                                    message: '<strong>Error:</strong> Shape edges cannot cross!'
                                },
                                shapeOptions: {
                                    color: '#97009c'
                                }
                            },
                            // Disable other drawing tools
                            polyline: false,
                            circle: false,
                            rectangle: false,
                            circlemarker: false,
                            marker: false
                        },
                        edit: {
                            featureGroup: drawnItems
                        }
                    });
                    map.addControl(window.drawControl);
                    
                    map.on('draw:created', function(e) {
                        drawnItems.addLayer(e.layer);
                        var coords = e.layer.getLatLngs()[0].map(function(latlng) {
                            return [latlng.lng, latlng.lat];
                        });
                        // Close the polygon
                        coords.push(coords[0]);
                        window.qt.aoi_drawn(JSON.stringify(coords));
                    });
                }
            """
            self.web_view.page().runJavaScript(js)
            
    def stop_drawing(self) -> None:
        """Disable drawing mode."""
        if self.drawing_mode:
            self.drawing_mode = False
            js = """
                if (window.drawControl) {
                    map.removeControl(window.drawControl);
                    window.drawControl = null;
                }
            """
            self.web_view.page().runJavaScript(js)
            
    def show_aoi(self, coords: List[List[float]], style: Dict[str, Any] = None) -> None:
        """Display an AOI on the map."""
        if not style:
            style = {
                'color': '#97009c',
                'weight': 2,
                'fillOpacity': 0.2
            }
            
        # Convert coordinates to GeoJSON
        geojson = {
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'Polygon',
                'coordinates': [coords]
            }
        }
        
        js = f"""
            var style = {json.dumps(style)};
            var geojson = {json.dumps(geojson)};
            
            // Remove existing AOI layer
            if (window.aoiLayer) {{
                map.removeLayer(window.aoiLayer);
            }}
            
            // Add new AOI layer
            window.aoiLayer = L.geoJSON(geojson, {{
                style: style
            }}).addTo(map);
            
            // Zoom to AOI
            map.fitBounds(window.aoiLayer.getBounds());
        """
        self.web_view.page().runJavaScript(js)
        
    def center_map(self, geometry: ee.Geometry) -> None:
        """Center the map on an Earth Engine geometry."""
        try:
            # Get the geometry bounds
            bounds = geometry.bounds().getInfo()['coordinates'][0]
            
            # Calculate center
            center_lon = (bounds[0][0] + bounds[2][0]) / 2
            center_lat = (bounds[0][1] + bounds[2][1]) / 2
            
            # Center map
            js = f"""
                map.setView([{center_lat}, {center_lon}], 10);
            """
            self.web_view.page().runJavaScript(js)
            
        except Exception as e:
            print(f"Error centering map: {str(e)}")
            
    def __del__(self):
        """Clean up temporary files."""
        try:
            if os.path.exists(self.html_file):
                os.remove(self.html_file)
        except:
            pass
