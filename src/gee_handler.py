"""
Google Earth Engine initialization and core operations.
Based on successful patterns from gee4book implementation.
"""
import ee
import geemap
from typing import Optional, Dict, Any
from .auth_gee import authenticate_gee

class GEEHandler:
    def __init__(self):
        self.ee = ee
        self.geemap = geemap
        self.sentinel1 = None
        self.initialize_ee()

    def initialize_ee(self) -> None:
        """Initialize Earth Engine with error handling."""
        try:
            authenticate_gee()  # Use the separate authentication function
            
            # Initialize Sentinel-1 collection
            self.sentinel1 = ee.ImageCollection('COPERNICUS/S1_GRD')
            print("Earth Engine initialized successfully!")
        except Exception as e:
            print(f"Error initializing Earth Engine: {str(e)}")
            raise

    def get_sentinel1_collection(self, 
                               start_date: str, 
                               end_date: str, 
                               geometry: ee.Geometry,
                               polarization: str = 'VH',
                               orbit: str = 'BOTH') -> ee.ImageCollection:
        """Get Sentinel-1 collection filtered by date and bounds."""
        collection = self.sentinel1 \
            .filterDate(start_date, end_date) \
            .filterBounds(geometry)
            
        # Filter by polarization if specified
        if polarization in ['VH', 'VV']:
            collection = collection.select(polarization)
            
        # Filter by orbit direction if specified
        if orbit != 'BOTH':
            collection = collection.filter(ee.Filter.eq('orbitProperties_pass', orbit))
            
        return collection

    def create_composite(self, collection: ee.ImageCollection) -> ee.Image:
        """Create a composite image from a collection."""
        return collection.mean()

    def create_temporal_composite(self, collection: ee.ImageCollection, band: str = 'VH') -> ee.Image:
        """Create a temporal composite from first, middle, and last images."""
        # Get collection size
        size = collection.size().getInfo()
        if size < 2:
            raise ValueError(f"Need at least 2 images for temporal comparison, found {size}")
        
        # Create list of images
        image_list = collection.toList(size)
        
        # Get first, middle, and last images
        first_image = ee.Image(image_list.get(0))
        middle_image = ee.Image(image_list.get(size // 2))
        last_image = ee.Image(image_list.get(size - 1))
        
        # Create RGB composite
        return ee.Image.cat([
            first_image.select(band),
            middle_image.select(band),
            last_image.select(band)
        ])

    def get_map_bounds(self, bounds: list) -> ee.Geometry:
        """Convert map bounds to Earth Engine geometry."""
        coords = [[
            [bounds[0][1], bounds[0][0]],  # SW
            [bounds[0][1], bounds[1][0]],  # SE
            [bounds[1][1], bounds[1][0]],  # NE
            [bounds[1][1], bounds[0][0]],  # NW
            [bounds[0][1], bounds[0][0]]   # SW (close polygon)
        ]]
        return ee.Geometry.Polygon(coords)

    def get_vis_params(self, mode: str = 'temporal') -> Dict[str, Any]:
        """Get visualization parameters for different modes."""
        if mode == 'temporal':
            return {
                'bands': ['VH', 'VH_1', 'VH_2'],
                'min': -25,
                'max': 0,
                'gamma': 1.4
            }
        else:
            return {
                'min': -25,
                'max': 0,
                'palette': ['black', 'white']
            }

    def export_to_drive(self, 
                       image: ee.Image, 
                       geometry: ee.Geometry, 
                       description: str = 'sentinel1_export',
                       scale: int = 10) -> ee.batch.Task:
        """Export an image to Google Drive."""
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=description,
            scale=scale,
            region=geometry
        )
        task.start()
        return task
