import ee
import math
import time
import traceback
from datetime import datetime, timedelta

def get_map_bounds(m):
    """Get the bounds of the current map view as an ee.Geometry"""
    bounds = m.bounds
    coords = [[
        [bounds[0][1], bounds[0][0]],  # SW
        [bounds[0][1], bounds[1][0]],  # SE
        [bounds[1][1], bounds[1][0]],  # NE
        [bounds[1][1], bounds[0][0]],  # NW
        [bounds[0][1], bounds[0][0]]   # SW (close polygon)
    ]]
    return ee.Geometry.Polygon(coords)

def load_sar_data(geometry, start_date, end_date, collection=None):
    """Load and process SAR data for a given geometry and date range"""
    if collection is None:
        collection = ee.ImageCollection('COPERNICUS/S1_GRD')
    
    # Convert dates to ee.Date objects if they're not already
    if isinstance(start_date, (datetime, str)):
        ee_start_date = ee.Date(start_date if isinstance(start_date, str) else start_date.strftime('%Y-%m-%d'))
    else:
        ee_start_date = start_date
        
    if isinstance(end_date, (datetime, str)):
        ee_end_date = ee.Date(end_date if isinstance(end_date, str) else end_date.strftime('%Y-%m-%d'))
    else:
        ee_end_date = end_date

    # Filter collection and sort by date
    filtered = (collection
        .filterDate(ee_start_date, ee_end_date)
        .filterBounds(geometry)
        .sort('system:time_start'))
    
    # Get collection size
    size = filtered.size().getInfo()
    
    if size < 2:
        raise ValueError(f"Need at least 2 images for temporal comparison, found {size}")
    
    # Create list of images
    image_list = filtered.toList(size)
    
    # Create three temporal versions
    first_image = ee.Image(image_list.get(0))
    middle_image = ee.Image(image_list.get(size // 2))
    last_image = ee.Image(image_list.get(size - 1))
    
    # Create RGB composite using temporal difference
    composite = ee.Image.cat([
        first_image.select('VH'),
        middle_image.select('VH'),
        last_image.select('VH')
    ]).clip(geometry)
    
    return composite, size

def update_map_layers(m, composite, geometry=None, retries=3, delay=1):
    """Update map layers with retry mechanism"""
    for attempt in range(retries):
        try:
            # Reset the map layers safely
            m.clear_layers()
            time.sleep(delay)
            
            # Add basemap
            m.add_basemap('HYBRID')
            
            # Add the composite layer with specified visualization
            vis_params = {
                'bands': ['VH', 'VH_1', 'VH_2'],
                'min': -25,
                'max': 0,
                'gamma': 1.4
            }
            
            # Add SAR layer
            m.addLayer(composite, vis_params, 'SAR Temporal Composite')
            time.sleep(delay)
            
            # Add AOI boundary if provided
            if geometry:
                aoi_style = {
                    'color': 'red',
                    'fillOpacity': 0.0,
                    'weight': 2
                }
                m.add_ee_layer(geometry, aoi_style, 'AOI Boundary')
                
                # Center map on AOI
                m.centerObject(geometry, zoom=12)
            
            return True
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed:")
            traceback.print_exc()
            if attempt < retries - 1:
                time.sleep(delay)
            continue
    return False
