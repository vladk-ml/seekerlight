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
                               geometry: ee.Geometry) -> ee.ImageCollection:
        """Get Sentinel-1 collection filtered by date and bounds."""
        return self.sentinel1 \
            .filterDate(start_date, end_date) \
            .filterBounds(geometry)

    def create_composite(self, collection: ee.ImageCollection) -> ee.Image:
        """Create a composite image from a collection."""
        return collection.mean()

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
