"""
Initialize and save a base map for the application.
"""
import ee
import geemap

def create_base_map():
    """Create and save the base map."""
    try:
        # Initialize Earth Engine
        ee.Initialize(project='ee-sergiyk1974')
        
        # Create map exactly like gee4book
        Map = geemap.Map(
            center=[47.2357, 39.7015],
            zoom=8,
            add_google_map=True,
            plugin_Draw=True,
            plugin_LatLngPopup=True,
            height='800px'
        )
        
        # Save the map
        map_file = "ui/base_map.html"
        Map.save(map_file)
        print(f"Base map saved to {map_file}")
        
    except Exception as e:
        print(f"Error creating base map: {str(e)}")

if __name__ == "__main__":
    create_base_map()
